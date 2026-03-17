"""
Página 2 — Social Media de la Competencia
Datos reales de Instagram: seguidores, engagement, top posts, frecuencia de contenido.
100% vinculada con los mismos perfiles de la sección Perfiles.
"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict
from components.data_loader import (
    load_raw_instagram_profiles,
    load_raw_instagram_posts,
    load_all_images_b64,
    get_local_image_b64,
)

st.set_page_config(page_title="Social Media — Gabifit", page_icon="📱", layout="wide")

st.markdown("""
<style>
  [data-testid="stSidebar"] { background: #111 !important; }
  .block-container { padding-top: 1.5rem !important; }
  h1 { color: #ef4444 !important; }
  h2 { color: #f0f0f0 !important; }
  h3 { color: #f0f0f0 !important; }
  .stMetric label { color: #888 !important; font-size: 12px !important; }
  .stMetric [data-testid="stMetricValue"] { color: #f0f0f0 !important; font-size: 22px !important; }
</style>
""", unsafe_allow_html=True)

st.title("📱 Social Media de la Competencia")
st.caption("Datos reales de Instagram · Mismos coaches de la sección Perfiles · Engagement, posts, alcance")

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("Cargando datos..."):
    profiles  = load_raw_instagram_profiles()
    posts     = load_raw_instagram_posts()
    img_cache = load_all_images_b64()

if not profiles:
    st.error("Sin datos. Corre `python run_collection.py` primero.")
    st.stop()

# ── Helper functions ───────────────────────────────────────────────────────────
def safe_fn(name):
    return re.sub(r'[^\w\-_]', '_', name)

def format_num(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(int(n))

def eng_rate(profile, user_posts):
    followers = profile.get("followersCount", 0)
    if not followers or not user_posts: return 0.0
    total = sum(p.get("likesCount", 0) + p.get("commentsCount", 0) for p in user_posts)
    return round(total / len(user_posts) / followers * 100, 2)

def avg_likes(user_posts):
    if not user_posts: return 0
    return round(sum(p.get("likesCount", 0) for p in user_posts) / len(user_posts))

def detect_cta(url, bio):
    url = (url or "").lower()
    bio_lower = (bio or "").lower()
    if "wa.me" in url or "wa.link" in url or "whatsapp" in url: return "WhatsApp"
    if "linktr.ee" in url or "linkbio" in url:                  return "Linktree"
    if "forms.gle" in url or "google.com/forms" in url:         return "Formulario"
    if "hackeatumetabolismo" in url or "canva.site" in url:     return "Página de Ventas"
    if "wasap" in bio_lower or any(x in (bio or "") for x in ["829","809","849"]): return "WhatsApp"
    return "Solo Orgánico"

# ── Index posts by owner ───────────────────────────────────────────────────────
posts_by_user = defaultdict(list)
for p in posts:
    posts_by_user[p.get("ownerUsername", "")].append(p)

profiles_sorted = sorted(profiles, key=lambda x: x.get("followersCount", 0), reverse=True)

# ── Sidebar filters (same as Perfiles) ────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filtros")
    search = st.text_input("Buscar coach", placeholder="nombre o @username")
    min_followers = st.slider("Mínimo seguidores", 0, 400_000, 0, step=1_000, format="%d")
    cta_filter = st.selectbox("Cómo cierra clientes",
                              ["Todos", "WhatsApp", "Linktree", "Formulario", "Página de Ventas", "Solo Orgánico"])
    sort_by = st.selectbox("Ordenar por",
                           ["Seguidores ↓", "Engagement ↓", "Avg Likes ↓", "Posts Totales ↓"])
    st.divider()
    st.markdown("**Leyenda Engagement**")
    st.markdown("🟢 Alto > 3%  |  🟡 Medio 1-3%  |  🔴 Bajo < 1%")

# ── Build filtered+enriched list ──────────────────────────────────────────────
coaches = []
for profile in profiles_sorted:
    uname     = profile.get("username", "")
    fname     = profile.get("fullName", uname)
    bio       = profile.get("biography", "")
    ext       = profile.get("externalUrl", "") or ""
    followers = profile.get("followersCount", 0)
    following = profile.get("followingCount", 0)
    posts_cnt = profile.get("postsCount", 0)
    user_posts = posts_by_user.get(uname, [])

    if search and search.lower() not in uname.lower() and search.lower() not in fname.lower():
        continue
    if followers < min_followers:
        continue
    if cta_filter != "Todos" and detect_cta(ext, bio) != cta_filter:
        continue

    er   = eng_rate(profile, user_posts)
    al   = avg_likes(user_posts)
    cta  = detect_cta(ext, bio)
    ratio = round(followers / following, 1) if following else 0

    coaches.append({
        "profile":   profile,
        "posts":     user_posts,
        "uname":     uname,
        "fname":     fname,
        "bio":       bio,
        "ext":       ext,
        "followers": followers,
        "following": following,
        "posts_cnt": posts_cnt,
        "eng":       er,
        "avg_likes": al,
        "cta":       cta,
        "ratio":     ratio,
        "ig_url":    f"https://instagram.com/{uname}",
    })

if sort_by == "Engagement ↓":
    coaches.sort(key=lambda x: x["eng"], reverse=True)
elif sort_by == "Avg Likes ↓":
    coaches.sort(key=lambda x: x["avg_likes"], reverse=True)
elif sort_by == "Posts Totales ↓":
    coaches.sort(key=lambda x: x["posts_cnt"], reverse=True)

if not coaches:
    st.info("Sin resultados con los filtros actuales.")
    st.stop()

# ── SUMMARY METRICS ────────────────────────────────────────────────────────────
total_followers = sum(c["followers"] for c in coaches)
avg_eng_all     = round(sum(c["eng"] for c in coaches) / len(coaches), 2)
total_posts_all = sum(c["posts_cnt"] for c in coaches)
top_eng_coach   = max(coaches, key=lambda x: x["eng"])

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Coaches analizados",   len(coaches))
c2.metric("Seguidores combinados", format_num(total_followers))
c3.metric("Engagement promedio",  f"{avg_eng_all}%")
c4.metric("Posts totales",        f"{total_posts_all:,}")
c5.metric("Mayor engagement",     f"@{top_eng_coach['uname']}", f"{top_eng_coach['eng']}%")

st.markdown("---")

# ── CHART ROW 1: Followers bar + Engagement bar ────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🏆 Ranking por Seguidores")
    names  = [c["fname"].split()[0] + f"\n@{c['uname']}" for c in coaches]
    folls  = [c["followers"] for c in coaches]
    colors_bar = ["#ef4444" if i == 0 else "#f97316" if i == 1 else "#fbbf24" if i == 2 else "#374151" for i in range(len(coaches))]

    fig = go.Figure(go.Bar(
        x=folls, y=names,
        orientation="h",
        marker_color=colors_bar,
        text=[format_num(f) for f in folls],
        textposition="outside",
        textfont=dict(color="#aaa", size=11),
    ))
    fig.update_layout(
        paper_bgcolor="#111", plot_bgcolor="#111",
        font=dict(color="#ccc", size=11),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        margin=dict(l=120, r=60, t=10, b=10),
        height=max(300, len(coaches) * 32),
        showlegend=False,
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("⚡ Engagement Rate por Coach")
    eng_sorted = sorted(coaches, key=lambda x: x["eng"], reverse=True)
    eng_names  = [c["fname"].split()[0] + f"\n@{c['uname']}" for c in eng_sorted]
    eng_vals   = [c["eng"] for c in eng_sorted]
    eng_colors = ["#22c55e" if e > 3 else "#f97316" if e > 1 else "#6b7280" for e in eng_vals]

    fig2 = go.Figure(go.Bar(
        x=eng_vals, y=eng_names,
        orientation="h",
        marker_color=eng_colors,
        text=[f"{e}%" for e in eng_vals],
        textposition="outside",
        textfont=dict(color="#aaa", size=11),
    ))
    fig2.update_layout(
        paper_bgcolor="#111", plot_bgcolor="#111",
        font=dict(color="#ccc", size=11),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        margin=dict(l=120, r=60, t=10, b=10),
        height=max(300, len(coaches) * 32),
        showlegend=False,
    )
    fig2.update_yaxes(autorange="reversed")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── CHART ROW 2: Scatter Followers vs Engagement + CTA Pie ────────────────────
col_l, col_r = st.columns([3, 2])

with col_l:
    st.subheader("📊 Seguidores vs Engagement")
    fig3 = go.Figure()
    cta_palette = {
        "WhatsApp":         "#22c55e",
        "Linktree":         "#60a5fa",
        "Formulario":       "#c084fc",
        "Página de Ventas": "#fb923c",
        "Solo Orgánico":    "#6b7280",
    }
    for cta_type, color in cta_palette.items():
        subset = [c for c in coaches if c["cta"] == cta_type]
        if not subset: continue
        fig3.add_trace(go.Scatter(
            x=[c["followers"] for c in subset],
            y=[c["eng"] for c in subset],
            mode="markers+text",
            name=cta_type,
            marker=dict(size=14, color=color, line=dict(width=1, color="#333")),
            text=[f"@{c['uname']}" for c in subset],
            textposition="top center",
            textfont=dict(size=9, color="#aaa"),
        ))
    fig3.add_hline(y=3, line_dash="dot", line_color="#22c55e",
                   annotation_text="Alto >3%", annotation_font_color="#22c55e", annotation_font_size=10)
    fig3.add_hline(y=1, line_dash="dot", line_color="#f97316",
                   annotation_text="Medio >1%", annotation_font_color="#f97316", annotation_font_size=10)
    fig3.update_layout(
        paper_bgcolor="#111", plot_bgcolor="#111",
        font=dict(color="#ccc"),
        xaxis=dict(showgrid=False, title="Seguidores", color="#666"),
        yaxis=dict(showgrid=False, title="Engagement %", color="#666"),
        legend=dict(bgcolor="#1a1a1a", bordercolor="#333", font=dict(size=11)),
        margin=dict(l=20, r=20, t=10, b=40),
        height=380,
    )
    st.plotly_chart(fig3, use_container_width=True)

with col_r:
    st.subheader("📣 Método de Cierre de Clientes")
    cta_counts = defaultdict(int)
    for c in coaches:
        cta_counts[c["cta"]] += 1
    cta_colors_pie = {
        "WhatsApp":         "#22c55e",
        "Linktree":         "#60a5fa",
        "Formulario":       "#c084fc",
        "Página de Ventas": "#fb923c",
        "Solo Orgánico":    "#6b7280",
    }
    labels  = list(cta_counts.keys())
    values  = list(cta_counts.values())
    colors  = [cta_colors_pie.get(l, "#555") for l in labels]
    fig4 = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#111", width=2)),
        textfont=dict(size=11, color="#ddd"),
    ))
    fig4.update_layout(
        paper_bgcolor="#111",
        font=dict(color="#ccc"),
        showlegend=True,
        legend=dict(bgcolor="#1a1a1a", bordercolor="#333", font=dict(size=11)),
        margin=dict(l=10, r=10, t=10, b=10),
        height=300,
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Insight callout
    wa_pct = round(cta_counts.get("WhatsApp", 0) / len(coaches) * 100)
    st.markdown(f"""
    <div style="background:#052e16;border:1px solid #166534;border-radius:10px;padding:12px 16px;margin-top:4px">
      <div style="color:#4ade80;font-size:13px;font-weight:700">💬 Insight clave</div>
      <div style="color:#86efac;font-size:12px;margin-top:4px">
        El <strong>{wa_pct}%</strong> de coaches cierra clientes por <strong>WhatsApp</strong>.
        No hay precios públicos. El funnel completo ocurre en privado.
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── TOP POSTS GRID (best performing across all coaches) ───────────────────────
st.subheader("🔥 Top Posts de Toda la Competencia")
st.caption("Los posts con más likes entre todos los coaches analizados")

all_posts_flat = []
for c in coaches:
    for post in c["posts"]:
        all_posts_flat.append({**post, "_coach": c})

top_posts_all = sorted(all_posts_flat, key=lambda p: p.get("likesCount", 0), reverse=True)[:12]

if top_posts_all:
    cols_per_row = 4
    rows = [top_posts_all[i:i+cols_per_row] for i in range(0, len(top_posts_all), cols_per_row)]

    for row in rows:
        grid_cols = st.columns(cols_per_row)
        for col, post in zip(grid_cols, row):
            c_data  = post["_coach"]
            uname   = c_data["uname"]
            fname   = c_data["fname"]
            sc      = post.get("shortCode", "")
            likes   = post.get("likesCount", 0)
            comments = post.get("commentsCount", 0)
            caption = (post.get("caption") or "")[:80].strip()
            post_url = post.get("url") or f"https://instagram.com/p/{sc}"

            img_b64 = get_local_image_b64(f"data/images/posts/{safe_fn(uname)}_{safe_fn(sc)}.jpg", img_cache)
            if img_b64:
                img_src = f"data:image/jpeg;base64,{img_b64}"
            else:
                img_src = post.get("displayUrl", "")

            pic_b64 = get_local_image_b64(f"data/images/profiles/{safe_fn(uname)}.jpg", img_cache)
            if pic_b64:
                pic_src = f"data:image/jpeg;base64,{pic_b64}"
            else:
                pic_src = f"https://ui-avatars.com/api/?name={fname.replace(' ','+')}&background=222&color=fff&size=40"

            card = f"""
            <div style="background:#141414;border:1px solid #222;border-radius:12px;overflow:hidden;
                        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
              <a href="{post_url}" target="_blank" style="display:block;text-decoration:none">
                <div style="aspect-ratio:1;overflow:hidden;background:#1a1a1a">
                  <img src="{img_src}" style="width:100%;height:100%;object-fit:cover;display:block"/>
                </div>
              </a>
              <div style="padding:10px 12px">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                  <img src="{pic_src}" style="width:28px;height:28px;border-radius:50%;object-fit:cover;border:1px solid #333"/>
                  <a href="{c_data['ig_url']}" target="_blank"
                     style="color:#60a5fa;font-size:11px;text-decoration:none;font-weight:600">@{uname}</a>
                </div>
                <div style="display:flex;gap:12px;margin-bottom:6px">
                  <span style="color:#f0f0f0;font-size:13px;font-weight:700">❤️ {format_num(likes)}</span>
                  <span style="color:#888;font-size:13px">💬 {comments}</span>
                </div>
                <p style="color:#999;font-size:11px;line-height:1.5;margin:0;
                          display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">
                  {caption or '<em style="color:#555">Sin caption</em>'}
                </p>
              </div>
            </div>"""

            with col:
                components.html(card, height=310, scrolling=False)

st.markdown("---")

# ── PER-COACH SOCIAL STATS CARDS ──────────────────────────────────────────────
st.subheader("👤 Stats por Coach")
st.caption("Haz clic en Instagram para ver el perfil completo · Ordenado por: " + sort_by)

for rank_i, c in enumerate(coaches):
    uname     = c["uname"]
    fname     = c["fname"]
    followers = c["followers"]
    following = c["following"]
    posts_cnt = c["posts_cnt"]
    er        = c["eng"]
    al        = c["avg_likes"]
    ratio     = c["ratio"]
    cta_label = c["cta"]
    ig_url    = c["ig_url"]
    ext       = c["ext"]
    user_posts = c["posts"]

    # Colours
    eng_color = "#22c55e" if er > 3 else ("#f97316" if er > 1 else "#888")
    cta_colors = {
        "WhatsApp":         ("#052e16", "#4ade80", "#166534"),
        "Linktree":         ("#0c1a2e", "#60a5fa", "#1e3a5f"),
        "Formulario":       ("#1a0a2e", "#c084fc", "#5b21b6"),
        "Página de Ventas": ("#2e1000", "#fb923c", "#9a3412"),
        "Solo Orgánico":    ("#2e0000", "#f87171", "#991b1b"),
    }
    cta_icons = {"WhatsApp":"💬","Linktree":"🔗","Formulario":"📋","Página de Ventas":"🚀","Solo Orgánico":"👁️"}
    cb_bg, cb_fg, cb_brd = cta_colors.get(cta_label, ("#1a1a1a","#888","#333"))
    cta_badge = f'<span style="background:{cb_bg};color:{cb_fg};border:1px solid {cb_brd};padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600">{cta_icons.get(cta_label,"")} {cta_label}</span>'

    # Profile pic
    pic_b64 = get_local_image_b64(f"data/images/profiles/{safe_fn(uname)}.jpg", img_cache)
    pic_src = f"data:image/jpeg;base64,{pic_b64}" if pic_b64 else \
              f"https://ui-avatars.com/api/?name={fname.replace(' ','+')}&background=222&color=fff&size=80"

    # Best 3 posts mini thumbnails
    top3 = sorted(user_posts, key=lambda p: p.get("likesCount", 0), reverse=True)[:3]
    thumb_html = ""
    for post in top3:
        sc   = post.get("shortCode", "")
        plikes = format_num(post.get("likesCount", 0))
        purl = post.get("url") or f"https://instagram.com/p/{sc}"
        tb64 = get_local_image_b64(f"data/images/posts/{safe_fn(uname)}_{safe_fn(sc)}.jpg", img_cache)
        tsrc = f"data:image/jpeg;base64,{tb64}" if tb64 else post.get("displayUrl","")
        thumb_html += f"""
        <a href="{purl}" target="_blank"
           style="display:block;position:relative;width:72px;height:72px;border-radius:8px;
                  overflow:hidden;border:1px solid #2a2a2a;flex-shrink:0;text-decoration:none">
          <img src="{tsrc}" style="width:100%;height:100%;object-fit:cover;display:block"/>
          <div style="position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,.65);
                      font-size:9px;color:#fff;text-align:center;padding:2px 0;font-weight:600">
            ❤️ {plikes}
          </div>
        </a>"""

    # External link button
    ext_btn = ""
    if ext:
        ext_label = "💬 WhatsApp" if "wa.me" in ext or "wa.link" in ext \
               else "🌳 Linktree" if "linktr.ee" in ext \
               else "📋 Formulario" if "forms.gle" in ext \
               else "🚀 Sales Page" if "hackeatumetabolismo" in ext \
               else "🔗 Link en Bio"
        ext_btn = f'<a href="{ext}" target="_blank" style="display:inline-block;padding:6px 14px;background:#1a1a1a;border:1px solid #333;border-radius:8px;color:#ddd;text-decoration:none;font-size:12px;font-weight:600;margin-left:8px">{ext_label}</a>'

    orig_rank = next((i+1 for i,p in enumerate(profiles_sorted) if p.get("username")==uname), 0)
    rank_label = f"<span style='background:#1a1a1a;color:#666;border:1px solid #333;padding:2px 10px;border-radius:10px;font-size:11px;font-weight:700'>#{orig_rank}</span>"

    card = f"""
    <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;overflow:hidden;
                font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin-bottom:2px">
      <div style="padding:16px 20px;display:flex;gap:16px;align-items:center">

        <!-- AVATAR -->
        <div style="flex-shrink:0">
          <img src="{pic_src}" style="width:64px;height:64px;border-radius:50%;object-fit:cover;border:2px solid #333"/>
        </div>

        <!-- NAME + HANDLE -->
        <div style="flex:1;min-width:0">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:2px">
            <span style="font-size:16px;font-weight:800;color:#f0f0f0">{fname}</span>
            {rank_label}
          </div>
          <a href="{ig_url}" target="_blank" style="color:#60a5fa;font-size:12px;text-decoration:none">@{uname}</a>
        </div>

        <!-- STATS GRID -->
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;flex-shrink:0;min-width:320px">
          <div style="text-align:center;background:#111;border-radius:8px;padding:8px 4px">
            <div style="font-size:17px;font-weight:700;color:#f0f0f0">{format_num(followers)}</div>
            <div style="font-size:9px;color:#555;text-transform:uppercase;letter-spacing:.5px">Seguidores</div>
          </div>
          <div style="text-align:center;background:#111;border-radius:8px;padding:8px 4px">
            <div style="font-size:17px;font-weight:700;color:{eng_color}">{er}%</div>
            <div style="font-size:9px;color:#555;text-transform:uppercase;letter-spacing:.5px">Engagement</div>
          </div>
          <div style="text-align:center;background:#111;border-radius:8px;padding:8px 4px">
            <div style="font-size:17px;font-weight:700;color:#f0f0f0">❤️ {format_num(al)}</div>
            <div style="font-size:9px;color:#555;text-transform:uppercase;letter-spacing:.5px">Avg Likes</div>
          </div>
          <div style="text-align:center;background:#111;border-radius:8px;padding:8px 4px">
            <div style="font-size:17px;font-weight:700;color:#f0f0f0">{posts_cnt}</div>
            <div style="font-size:9px;color:#555;text-transform:uppercase;letter-spacing:.5px">Posts IG</div>
          </div>
        </div>

        <!-- TOP THUMBS -->
        <div style="display:flex;gap:6px;flex-shrink:0">
          {thumb_html if thumb_html else '<span style="color:#444;font-size:11px">Sin posts</span>'}
        </div>

      </div>

      <!-- FOOTER BAR -->
      <div style="background:#111;padding:10px 20px;display:flex;align-items:center;gap:12px;border-top:1px solid #222">
        {cta_badge}
        <a href="{ig_url}" target="_blank"
           style="display:inline-block;padding:6px 14px;border-radius:8px;text-decoration:none;color:white;
                  font-size:12px;font-weight:600;background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045)">
          📸 Ver Instagram
        </a>
        {ext_btn}
        <span style="color:#555;font-size:11px;margin-left:auto">
          Ratio Seg/Sig: <strong style="color:#888">{ratio}x</strong>
          &nbsp;·&nbsp; {len(user_posts)} posts analizados
        </span>
      </div>
    </div>"""

    components.html(card, height=170, scrolling=False)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(f"📊 {len(coaches)} coaches · {sum(c['posts_cnt'] for c in coaches):,} posts publicados · {len(posts)} posts analizados · Datos vía Apify Instagram Scraper")
