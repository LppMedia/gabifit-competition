"""
Gabifit — DR Fitness Market Intelligence
Hero / Overview page — first thing the client sees.
"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from collections import defaultdict

st.set_page_config(
    page_title="Gabifit — DR Fitness Intelligence",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stSidebar"]          { background:#111 !important; }
  [data-testid="collapsedControl"]   { color:#888 !important; }
  .block-container                   { padding-top:1rem !important; padding-bottom:2rem !important; }
  h1,h2,h3                           { color:#f0f0f0 !important; }
  .stMetric label                    { color:#888 !important; font-size:11px !important; text-transform:uppercase; letter-spacing:.5px; }
  .stMetric [data-testid="stMetricValue"] { color:#f0f0f0 !important; font-size:26px !important; font-weight:800 !important; }
  .stMetric [data-testid="stMetricDelta"] { font-size:12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
from dashboard.components.data_loader import (
    load_raw_instagram_profiles,
    load_raw_instagram_posts,
    load_all_images_b64,
    get_local_image_b64,
)

with st.spinner(""):
    profiles  = load_raw_instagram_profiles()
    posts     = load_raw_instagram_posts()
    img_cache = load_all_images_b64()

if not profiles:
    st.error("Sin datos. Corre `python run_collection.py` primero.")
    st.stop()

# ── Helpers ────────────────────────────────────────────────────────────────────
def safe_fn(n): return re.sub(r'[^\w\-_]', '_', n)
def fmt(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(int(n))

def detect_cta(url, bio):
    url, bio_l = (url or "").lower(), (bio or "").lower()
    if "wa.me" in url or "wa.link" in url or "whatsapp" in url: return "WhatsApp"
    if "linktr.ee" in url or "linkbio" in url:                  return "Linktree"
    if "forms.gle" in url or "google.com/forms" in url:         return "Formulario"
    if "hackeatumetabolismo" in url or "canva.site" in url:     return "Sales Page"
    if "wasap" in bio_l or any(x in (bio or "") for x in ["829","809","849"]): return "WhatsApp"
    return "Orgánico"

posts_by_user = defaultdict(list)
for p in posts:
    posts_by_user[p.get("ownerUsername","")].append(p)

profiles_sorted = sorted(profiles, key=lambda x: x.get("followersCount",0), reverse=True)

def eng_rate(profile):
    uname = profile.get("username","")
    followers = profile.get("followersCount",0)
    user_posts = posts_by_user.get(uname,[])
    if not followers or not user_posts: return 0.0
    total = sum(p.get("likesCount",0)+p.get("commentsCount",0) for p in user_posts)
    return round(total/len(user_posts)/followers*100, 2)

# ── Compute summary stats ──────────────────────────────────────────────────────
total_followers = sum(p.get("followersCount",0) for p in profiles)
total_posts_pub = sum(p.get("postsCount",0) for p in profiles)
cta_counts = defaultdict(int)
for p in profiles:
    cta_counts[detect_cta(p.get("externalUrl",""), p.get("biography",""))] += 1

wa_count   = cta_counts["WhatsApp"]
eng_rates  = [eng_rate(p) for p in profiles]
avg_eng    = round(sum(eng_rates)/len(eng_rates), 2) if eng_rates else 0
top_coach  = profiles_sorted[0]
top_eng    = max(profiles, key=eng_rate)

# ══════════════════════════════════════════════════════════════════════════════
# HERO BANNER
# ══════════════════════════════════════════════════════════════════════════════
components.html(f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
            background:linear-gradient(135deg,#0a0a0a 0%,#1a0808 50%,#0a0a0a 100%);
            border:1px solid #2a1a1a;border-radius:20px;padding:36px 40px 32px;
            margin-bottom:4px;position:relative;overflow:hidden">

  <!-- Background glow -->
  <div style="position:absolute;top:-40px;right:-40px;width:300px;height:300px;
              background:radial-gradient(circle,rgba(239,68,68,.12) 0%,transparent 70%);
              pointer-events:none"></div>
  <div style="position:absolute;bottom:-60px;left:20%;width:400px;height:200px;
              background:radial-gradient(circle,rgba(239,68,68,.06) 0%,transparent 70%);
              pointer-events:none"></div>

  <div style="display:flex;align-items:center;gap:16px;margin-bottom:10px">
    <span style="font-size:36px">🏆</span>
    <div>
      <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:3px;
                  color:#ef4444;margin-bottom:4px">GABIFIT · INTELIGENCIA COMPETITIVA</div>
      <h1 style="font-size:32px;font-weight:900;color:#f0f0f0;margin:0;line-height:1.1">
        Mercado Fitness RD —
        <span style="background:linear-gradient(90deg,#ef4444,#f97316);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent">
          Radiografía Completa
        </span>
      </h1>
    </div>
  </div>

  <p style="color:#888;font-size:15px;max-width:700px;line-height:1.7;margin:0 0 24px 0">
    Análisis profundo de <strong style="color:#f0f0f0">{len(profiles)} coaches dominicanos</strong>
    de fitness en Instagram — sus seguidores, cómo cierran clientes, qué publican,
    y dónde están las <strong style="color:#ef4444">oportunidades de mercado</strong> para Gabifit.
  </p>

  <div style="display:flex;gap:10px;flex-wrap:wrap">
    <span style="background:#1a0808;border:1px solid #7f1d1d;color:#fca5a5;
                 padding:6px 16px;border-radius:20px;font-size:12px;font-weight:600">
      📱 {len(profiles)} perfiles analizados
    </span>
    <span style="background:#0a1a0a;border:1px solid #166534;color:#86efac;
                 padding:6px 16px;border-radius:20px;font-size:12px;font-weight:600">
      📸 {len(posts)} posts estudiados
    </span>
    <span style="background:#1a1000;border:1px solid #854d0e;color:#fde68a;
                 padding:6px 16px;border-radius:20px;font-size:12px;font-weight:600">
      👥 {fmt(total_followers)} seguidores combinados
    </span>
    <span style="background:#0c1a2e;border:1px solid #1e3a5f;color:#93c5fd;
                 padding:6px 16px;border-radius:20px;font-size:12px;font-weight:600">
      🔬 Funnels investigados en vivo
    </span>
  </div>
</div>
""", height=240, scrolling=False)

# ══════════════════════════════════════════════════════════════════════════════
# KPI ROW
# ══════════════════════════════════════════════════════════════════════════════
c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("Coaches", len(profiles), "RD Fitness")
c2.metric("Seguidores", fmt(total_followers), "combinados")
c3.metric("Posts publicados", f"{total_posts_pub:,}", "en total")
c4.metric("Posts analizados", len(posts), "con captions")
c5.metric("Avg Engagement", f"{avg_eng}%", "Instagram")
c6.metric("Cierran por WA", f"{wa_count}/{len(profiles)}", f"{round(wa_count/len(profiles)*100)}%")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# CHART ROW 1: Followers ranking + CTA breakdown
# ══════════════════════════════════════════════════════════════════════════════
col_l, col_r = st.columns([3, 2])

with col_l:
    st.subheader("👑 Ranking de Seguidores")
    names  = [p.get("fullName","").split()[0] + f"\n@{p.get('username','')}" for p in profiles_sorted]
    folls  = [p.get("followersCount",0) for p in profiles_sorted]
    bar_colors = ["#ef4444" if i==0 else "#f97316" if i==1 else "#fbbf24" if i==2
                  else "#374151" for i in range(len(profiles_sorted))]

    fig = go.Figure(go.Bar(
        x=folls, y=names, orientation="h",
        marker_color=bar_colors,
        text=[fmt(f) for f in folls],
        textposition="outside",
        textfont=dict(color="#aaa", size=10),
    ))
    fig.update_layout(
        paper_bgcolor="#111", plot_bgcolor="#111",
        font=dict(color="#ccc", size=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=9)),
        margin=dict(l=130, r=70, t=10, b=10),
        height=max(300, len(profiles_sorted)*28),
        showlegend=False,
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.subheader("📣 Cómo Cierran Clientes")
    cta_colors = {
        "WhatsApp":  "#22c55e", "Linktree": "#60a5fa",
        "Formulario":"#c084fc", "Sales Page":"#fb923c", "Orgánico":"#6b7280",
    }
    labels = list(cta_counts.keys())
    values = list(cta_counts.values())
    colors = [cta_colors.get(l,"#555") for l in labels]

    fig2 = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.6,
        marker=dict(colors=colors, line=dict(color="#111", width=2)),
        textfont=dict(size=11, color="#ddd"),
    ))
    fig2.update_layout(
        paper_bgcolor="#111", font=dict(color="#ccc"),
        showlegend=True,
        legend=dict(bgcolor="#1a1a1a", bordercolor="#333", font=dict(size=11)),
        margin=dict(l=10,r=10,t=10,b=10), height=280,
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Key insight
    wa_pct = round(wa_count/len(profiles)*100)
    st.markdown(f"""
    <div style="background:#052e16;border:1px solid #166534;border-radius:10px;
                padding:12px 16px;font-family:-apple-system,sans-serif">
      <div style="color:#4ade80;font-weight:700;font-size:13px">💡 Insight Clave</div>
      <div style="color:#86efac;font-size:12px;margin-top:5px;line-height:1.6">
        El <strong>{wa_pct}%</strong> cierra por WhatsApp.<br>
        <strong>Nadie muestra precio público.</strong><br>
        Solo <strong>1 coach</strong> tiene funnel completo.
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# CHART ROW 2: Engagement scatter + top profiles strip
# ══════════════════════════════════════════════════════════════════════════════
col_a, col_b = st.columns([2, 3])

with col_a:
    st.subheader("⚡ Engagement vs Seguidores")
    cta_palette = {
        "WhatsApp":"#22c55e","Linktree":"#60a5fa",
        "Formulario":"#c084fc","Sales Page":"#fb923c","Orgánico":"#6b7280",
    }
    fig3 = go.Figure()
    cta_groups = defaultdict(list)
    for p in profiles:
        cta = detect_cta(p.get("externalUrl",""), p.get("biography",""))
        cta_groups[cta].append(p)

    for cta_type, group in cta_groups.items():
        fig3.add_trace(go.Scatter(
            x=[p.get("followersCount",0) for p in group],
            y=[eng_rate(p) for p in group],
            mode="markers+text",
            name=cta_type,
            marker=dict(size=13, color=cta_palette.get(cta_type,"#555"),
                        line=dict(width=1, color="#333")),
            text=[f"@{p.get('username','')}" for p in group],
            textposition="top center",
            textfont=dict(size=8, color="#999"),
        ))
    fig3.add_hline(y=3, line_dash="dot", line_color="#22c55e",
                   annotation_text="Alto >3%", annotation_font_color="#22c55e",
                   annotation_font_size=9)
    fig3.add_hline(y=1, line_dash="dot", line_color="#f97316",
                   annotation_text="Medio >1%", annotation_font_color="#f97316",
                   annotation_font_size=9)
    fig3.update_layout(
        paper_bgcolor="#111", plot_bgcolor="#111",
        font=dict(color="#ccc"),
        xaxis=dict(showgrid=False, title=dict(text="Seguidores", font=dict(size=11)), color="#555"),
        yaxis=dict(showgrid=False, title=dict(text="Engagement %", font=dict(size=11)), color="#555"),
        legend=dict(bgcolor="#1a1a1a", bordercolor="#333", font=dict(size=10)),
        margin=dict(l=20,r=20,t=10,b=40), height=320,
    )
    st.plotly_chart(fig3, use_container_width=True)

with col_b:
    st.subheader("🏅 Top Coaches — Vista Rápida")

    top5 = profiles_sorted[:5]
    cards_html = ""
    for i, p in enumerate(top5):
        uname    = p.get("username","")
        fname    = p.get("fullName", uname)
        followers= p.get("followersCount",0)
        bio      = (p.get("biography","") or "")[:80]
        ext      = p.get("externalUrl","") or ""
        er       = eng_rate(p)
        cta      = detect_cta(ext, p.get("biography",""))
        ig_url   = f"https://instagram.com/{uname}"
        eng_color= "#22c55e" if er>3 else ("#f97316" if er>1 else "#888")

        # Profile pic
        pic_b64 = get_local_image_b64(f"data/images/profiles/{safe_fn(uname)}.jpg", img_cache)
        pic_src = (f"data:image/jpeg;base64,{pic_b64}" if pic_b64
                   else f"https://ui-avatars.com/api/?name={fname.replace(' ','+')}&background=222&color=fff&size=60")

        # Rank medal
        medals = {0:"👑",1:"🥈",2:"🥉"}
        medal  = medals.get(i, f"#{i+1}")

        # CTA color
        cta_bg = {"WhatsApp":"#052e16","Linktree":"#0c1a2e",
                  "Formulario":"#1a0a2e","Sales Page":"#2e1000","Orgánico":"#1a1a1a"}
        cta_fg = {"WhatsApp":"#4ade80","Linktree":"#60a5fa",
                  "Formulario":"#c084fc","Sales Page":"#fb923c","Orgánico":"#888"}
        cb = cta_bg.get(cta,"#1a1a1a"); cf = cta_fg.get(cta,"#888")

        # Top post thumbnail
        user_posts = sorted(posts_by_user.get(uname,[]),
                            key=lambda x: x.get("likesCount",0), reverse=True)
        thumb_html = ""
        if user_posts:
            tp = user_posts[0]
            sc = tp.get("shortCode","")
            tb64 = get_local_image_b64(f"data/images/posts/{safe_fn(uname)}_{safe_fn(sc)}.jpg", img_cache)
            tsrc = f"data:image/jpeg;base64,{tb64}" if tb64 else tp.get("displayUrl","")
            turl = tp.get("url") or f"https://instagram.com/p/{sc}"
            thumb_html = f"""
            <a href="{turl}" target="_blank"
               style="display:block;width:52px;height:52px;border-radius:8px;
                      overflow:hidden;border:1px solid #2a2a2a;flex-shrink:0">
              <img src="{tsrc}" style="width:100%;height:100%;object-fit:cover"/>
            </a>"""

        cards_html += f"""
        <div style="display:flex;align-items:center;gap:12px;padding:10px 14px;
                    background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;
                    margin-bottom:8px">
          <span style="font-size:18px;flex-shrink:0;width:24px;text-align:center">{medal}</span>
          <img src="{pic_src}" style="width:46px;height:46px;border-radius:50%;
               object-fit:cover;border:2px solid #333;flex-shrink:0"/>
          <div style="flex:1;min-width:0">
            <div style="font-size:13px;font-weight:700;color:#f0f0f0;white-space:nowrap;
                        overflow:hidden;text-overflow:ellipsis">{fname}</div>
            <a href="{ig_url}" target="_blank"
               style="color:#60a5fa;font-size:11px;text-decoration:none">@{uname}</a>
          </div>
          <div style="text-align:center;min-width:60px">
            <div style="font-size:14px;font-weight:700;color:#f0f0f0">{fmt(followers)}</div>
            <div style="font-size:9px;color:#555;text-transform:uppercase">Seg.</div>
          </div>
          <div style="text-align:center;min-width:48px">
            <div style="font-size:14px;font-weight:700;color:{eng_color}">{er}%</div>
            <div style="font-size:9px;color:#555;text-transform:uppercase">Eng.</div>
          </div>
          <span style="background:{cb};color:{cf};border:1px solid {cf}33;
                       padding:3px 10px;border-radius:14px;font-size:10px;font-weight:600;
                       white-space:nowrap;flex-shrink:0">{cta}</span>
          {thumb_html}
        </div>"""

    components.html(f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
      {cards_html}
    </div>
    """, height=360, scrolling=False)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION NAVIGATION CARDS
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🗺️ Explorar el Dashboard")

nav_html = """
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
            display:grid;grid-template-columns:repeat(5,1fr);gap:12px">

  <a href="/perfiles" target="_self" style="text-decoration:none">
    <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;
                padding:20px 16px;text-align:center;transition:border-color .2s;
                cursor:pointer" onmouseover="this.style.borderColor='#ef4444'"
                onmouseout="this.style.borderColor='#2a2a2a'">
      <div style="font-size:28px;margin-bottom:10px">👥</div>
      <div style="font-size:14px;font-weight:700;color:#f0f0f0;margin-bottom:6px">Perfiles</div>
      <div style="font-size:11px;color:#666;line-height:1.5">
        Fotos, bios, posts y CTAs reales de cada coach
      </div>
      <div style="margin-top:10px;font-size:10px;color:#ef4444;font-weight:700">VER →</div>
    </div>
  </a>

  <a href="/pricing" target="_self" style="text-decoration:none">
    <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;
                padding:20px 16px;text-align:center;cursor:pointer"
                onmouseover="this.style.borderColor='#f97316'"
                onmouseout="this.style.borderColor='#2a2a2a'">
      <div style="font-size:28px;margin-bottom:10px">💰</div>
      <div style="font-size:14px;font-weight:700;color:#f0f0f0;margin-bottom:6px">Pricing</div>
      <div style="font-size:11px;color:#666;line-height:1.5">
        Estimados de precios RD$ y USD por tier de seguidores
      </div>
      <div style="margin-top:10px;font-size:10px;color:#f97316;font-weight:700">VER →</div>
    </div>
  </a>

  <a href="/social_media" target="_self" style="text-decoration:none">
    <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;
                padding:20px 16px;text-align:center;cursor:pointer"
                onmouseover="this.style.borderColor='#60a5fa'"
                onmouseout="this.style.borderColor='#2a2a2a'">
      <div style="font-size:28px;margin-bottom:10px">📱</div>
      <div style="font-size:14px;font-weight:700;color:#f0f0f0;margin-bottom:6px">Social Media</div>
      <div style="font-size:11px;color:#666;line-height:1.5">
        Engagement, top posts y comparativas de alcance
      </div>
      <div style="margin-top:10px;font-size:10px;color:#60a5fa;font-weight:700">VER →</div>
    </div>
  </a>

  <a href="/services" target="_self" style="text-decoration:none">
    <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;
                padding:20px 16px;text-align:center;cursor:pointer"
                onmouseover="this.style.borderColor='#c084fc'"
                onmouseout="this.style.borderColor='#2a2a2a'">
      <div style="font-size:28px;margin-bottom:10px">🛎️</div>
      <div style="font-size:14px;font-weight:700;color:#f0f0f0;margin-bottom:6px">Servicios</div>
      <div style="font-size:11px;color:#666;line-height:1.5">
        Qué ofrece cada coach y gaps del mercado
      </div>
      <div style="margin-top:10px;font-size:10px;color:#c084fc;font-weight:700">VER →</div>
    </div>
  </a>

  <a href="/funnels" target="_self" style="text-decoration:none">
    <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:14px;
                padding:20px 16px;text-align:center;cursor:pointer"
                onmouseover="this.style.borderColor='#4ade80'"
                onmouseout="this.style.borderColor='#2a2a2a'">
      <div style="font-size:28px;margin-bottom:10px">🔬</div>
      <div style="font-size:14px;font-weight:700;color:#f0f0f0;margin-bottom:6px">Funnels</div>
      <div style="font-size:11px;color:#666;line-height:1.5">
        Investigación en vivo: cómo cierran clientes los top 3
      </div>
      <div style="margin-top:10px;font-size:10px;color:#4ade80;font-weight:700">VER →</div>
    </div>
  </a>

</div>
"""
components.html(nav_html, height=170, scrolling=False)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# BOTTOM: 3 BIG OPPORTUNITIES FOR GABIFIT
# ══════════════════════════════════════════════════════════════════════════════
components.html(f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
  <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;
              color:#555;margin-bottom:14px">🎯 LAS 3 MAYORES OPORTUNIDADES PARA GABIFIT</div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">

    <div style="background:linear-gradient(135deg,#0c1a0c,#052e16);border:1px solid #166534;
                border-radius:14px;padding:20px">
      <div style="font-size:24px;margin-bottom:10px">💰</div>
      <div style="font-size:14px;font-weight:800;color:#4ade80;margin-bottom:8px">
        Precio Transparente
      </div>
      <div style="font-size:12px;color:#86efac;line-height:1.7">
        <strong>0 de {len(profiles)} coaches</strong> muestra precio público.<br>
        El que lo muestre primero elimina la fricción del "¿cuánto cobras?"
        y convierte más leads en clientes sin conversación.
      </div>
    </div>

    <div style="background:linear-gradient(135deg,#1a0c0c,#2e1000);border:1px solid #9a3412;
                border-radius:14px;padding:20px">
      <div style="font-size:24px;margin-bottom:10px">📲</div>
      <div style="font-size:14px;font-weight:800;color:#fb923c;margin-bottom:8px">
        Funnel Automatizado
      </div>
      <div style="font-size:12px;color:#fed7aa;line-height:1.7">
        Solo <strong>1 coach</strong> tiene una sales page real.<br>
        El resto cierra por WhatsApp sin sistema. Un funnel básico
        (landing + WA automático) ya supera al {round((len(profiles)-1)/len(profiles)*100)}% del mercado.
      </div>
    </div>

    <div style="background:linear-gradient(135deg,#0c0c1a,#0c1a2e);border:1px solid #1e3a5f;
                border-radius:14px;padding:20px">
      <div style="font-size:24px;margin-bottom:10px">📊</div>
      <div style="font-size:14px;font-weight:800;color:#60a5fa;margin-bottom:8px">
        Resultados Públicos
      </div>
      <div style="font-size:12px;color:#bfdbfe;line-height:1.7">
        Engagement promedio del mercado: <strong>{avg_eng}%</strong>.<br>
        Nadie muestra resultados reales de clientes con números.
        Testimonios con datos concretos = diferenciador inmediato.
      </div>
    </div>

  </div>
</div>
""", height=210, scrolling=False)

st.caption(f"📊 {len(profiles)} coaches · {len(posts)} posts · {fmt(total_followers)} seguidores combinados · Datos vía Apify Instagram Scraper · Actualizado Marzo 2026")
