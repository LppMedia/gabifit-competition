"""
Página 0 — Perfiles de Competidores
Vista rica con fotos, bios, posts, CTAs y links reales.
"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import streamlit.components.v1 as components
from collections import defaultdict
from components.data_loader import (
    load_raw_instagram_profiles,
    load_raw_instagram_posts,
    load_all_images_b64,
    get_local_image_b64,
)

st.set_page_config(page_title="Perfiles Competidores", page_icon="👥", layout="wide")

# ── CSS global ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stSidebar"] { background: #111 !important; }
  .block-container { padding-top: 1.5rem !important; }
  h1 { color: #ff4444 !important; }
</style>
""", unsafe_allow_html=True)

st.title("👥 Perfiles de Competidores — RD Fitness")
st.caption("Datos reales scraped de Instagram · Fotos, bios, cómo cierran clientes, top posts")

# ── Load data (all cached) ─────────────────────────────────────────────────────
with st.spinner("Cargando perfiles e imágenes..."):
    profiles   = load_raw_instagram_profiles()
    posts      = load_raw_instagram_posts()
    img_cache  = load_all_images_b64()  # loads all 125 images once, then cached

if not profiles:
    st.error("No hay datos. Corre `python run_collection.py` primero.")
    st.stop()

# Index posts by owner
posts_by_user = defaultdict(list)
for p in posts:
    posts_by_user[p.get("ownerUsername", "")].append(p)

# Sort by followers
profiles_sorted = sorted(profiles, key=lambda x: x.get("followersCount", 0), reverse=True)

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filtros")
    search = st.text_input("Buscar coach", placeholder="nombre o @username")
    min_followers = st.slider("Mínimo seguidores", 0, 400000, 0, step=1000,
                               format="%d")
    cta_options = ["Todos", "WhatsApp", "Linktree", "Formulario", "Página de Ventas", "Solo Orgánico"]
    cta_filter = st.selectbox("Cómo cierra clientes", cta_options)
    sort_by = st.selectbox("Ordenar por", ["Seguidores ↓", "Engagement ↓", "Avg Likes ↓"])

    st.divider()
    st.markdown("**Leyenda Engagement**")
    st.markdown("🟢 Alto > 3%  |  🟡 Medio 1-3%  |  🔴 Bajo < 1%")

# ── Helper functions ───────────────────────────────────────────────────────────
def safe_fn(name):
    return re.sub(r'[^\w\-_]', '_', name)

def detect_cta_label(url, bio):
    url = (url or "").lower()
    bio_lower = (bio or "").lower()
    if "wa.me" in url or "wa.link" in url or "whatsapp" in url:
        return "WhatsApp"
    if "linktr.ee" in url or "linkbio" in url:
        return "Linktree"
    if "forms.gle" in url or "google.com/forms" in url:
        return "Formulario"
    if "hackeatumetabolismo" in url or "florecer" in url or "canva.site" in url or "rebrand.ly" in url:
        return "Página de Ventas"
    if "wasap" in bio_lower or "829" in (bio or "") or "809" in (bio or "") or "849" in (bio or ""):
        return "WhatsApp"
    return "Solo Orgánico"

def get_cta_html(url, bio):
    label = detect_cta_label(url, bio)
    colors = {
        "WhatsApp":        ("#052e16", "#4ade80", "#166534"),
        "Linktree":        ("#0c1a2e", "#60a5fa", "#1e3a5f"),
        "Formulario":      ("#1a0a2e", "#c084fc", "#5b21b6"),
        "Página de Ventas":("#2e1000", "#fb923c", "#9a3412"),
        "Solo Orgánico":   ("#2e0000", "#f87171", "#991b1b"),
    }
    icons = {
        "WhatsApp": "💬", "Linktree": "🔗", "Formulario": "📋",
        "Página de Ventas": "🚀", "Solo Orgánico": "👁️",
    }
    descs = {
        "WhatsApp":         "Cierra por DM/WhatsApp — fricción mínima",
        "Linktree":         "Múltiples opciones de contacto",
        "Formulario":       "Pre-califica leads — posicionamiento premium",
        "Página de Ventas": "Funnel completo con landing page",
        "Solo Orgánico":    "Sin CTA claro — solo contenido orgánico",
    }
    bg, fg, border = colors.get(label, ("#1a1a1a", "#888", "#333"))
    icon = icons.get(label, "")
    desc = descs.get(label, "")
    return label, f"""
    <span style="background:{bg};color:{fg};border:1px solid {border};
                 padding:5px 14px;border-radius:20px;font-size:13px;font-weight:600;
                 display:inline-block;margin-right:6px">{icon} {label}</span>
    <span style="color:#666;font-size:12px;font-style:italic">{desc}</span>"""

def ext_btn_html(url):
    if not url:
        return ""
    label = "🔗 Link en Bio"
    if "wa.me" in url or "wa.link" in url:     label = "💬 WhatsApp"
    elif "forms.gle" in url or "google.com/forms" in url: label = "📋 Formulario"
    elif "linktr.ee" in url:                   label = "🌳 Linktree"
    elif "hackeatumetabolismo" in url:         label = "🚀 Sales Page"
    elif "canva.site" in url or "rebrand.ly" in url: label = "🌐 Mini-site"
    return f'<a href="{url}" target="_blank" style="display:inline-block;padding:7px 16px;background:#1a1a1a;border:1px solid #333;border-radius:8px;color:#ddd;text-decoration:none;font-size:13px;font-weight:600;margin-left:8px">{label}</a>'

def format_number(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

def classify_services(bio, captions):
    text = ((bio or "") + " " + (captions or "")).lower()
    s = []
    if any(w in text for w in ["online", "virtual", "remoto", "distancia"]): s.append("🌐 Online")
    if any(w in text for w in ["presencial", "gym", "gimnasio", "studio"]):  s.append("🏋️ Presencial")
    if any(w in text for w in ["nutrici", "alimentaci", "dieta"]):           s.append("🥗 Nutrición")
    if any(w in text for w in ["transform", "bajar de peso", "pérdida"]):    s.append("🔥 Transformación")
    if any(w in text for w in ["musculo", "fuerza", "hipertrofia"]):         s.append("💪 Hipertrofia")
    if any(w in text for w in ["evaluaci", "assess"]):                       s.append("📊 Evaluación")
    return s or ["📋 General"]

def badges_html(items, bg="#0a1a0a", fg="#86efac", border="#166534"):
    return "".join([
        f'<span style="background:{bg};color:{fg};border:1px solid {border};'
        f'padding:3px 10px;border-radius:10px;font-size:12px;margin:2px 3px 2px 0;display:inline-block">{i}</span>'
        for i in items
    ])

# ── Build filtered list ────────────────────────────────────────────────────────
def compute_eng(profile, user_posts):
    followers = profile.get("followersCount", 0)
    if not followers or not user_posts: return 0.0
    total_l = sum(p.get("likesCount", 0) for p in user_posts)
    total_c = sum(p.get("commentsCount", 0) for p in user_posts)
    return round((total_l + total_c) / len(user_posts) / followers * 100, 2)

def compute_avg_likes(user_posts):
    if not user_posts: return 0
    return round(sum(p.get("likesCount", 0) for p in user_posts) / len(user_posts))

# Apply filters
filtered = []
for profile in profiles_sorted:
    uname = profile.get("username", "")
    fname = profile.get("fullName", uname)
    bio   = profile.get("biography", "")
    ext   = profile.get("externalUrl", "") or ""
    followers = profile.get("followersCount", 0)
    user_posts = posts_by_user.get(uname, [])

    # Search
    if search and search.lower() not in uname.lower() and search.lower() not in fname.lower():
        continue
    # Followers
    if followers < min_followers:
        continue
    # CTA
    if cta_filter != "Todos" and detect_cta_label(ext, bio) != cta_filter:
        continue

    eng = compute_eng(profile, user_posts)
    avg_likes = compute_avg_likes(user_posts)
    filtered.append((profile, user_posts, eng, avg_likes))

# Sort
if sort_by == "Engagement ↓":
    filtered.sort(key=lambda x: x[2], reverse=True)
elif sort_by == "Avg Likes ↓":
    filtered.sort(key=lambda x: x[3], reverse=True)
# default: already sorted by followers

# ── Summary bar ───────────────────────────────────────────────────────────────
total_f = sum(p.get("followersCount", 0) for p in profiles_sorted)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Coaches", len(filtered), f"de {len(profiles_sorted)}")
c2.metric("Seguidores totales", format_number(total_f))
c3.metric("Cierran WA", sum(1 for p in profiles_sorted if detect_cta_label(p.get("externalUrl",""), p.get("biography","")) == "WhatsApp"))
c4.metric("Usan Formulario", sum(1 for p in profiles_sorted if detect_cta_label(p.get("externalUrl",""), p.get("biography","")) == "Formulario"))
c5.metric("Posts analizados", len(posts))

st.divider()

if not filtered:
    st.info("Sin resultados con los filtros actuales.")
    st.stop()

# ── Render each coach card ─────────────────────────────────────────────────────
for rank_idx, (profile, user_posts, eng_rate, avg_likes) in enumerate(filtered):
    uname     = profile.get("username", "")
    fname     = profile.get("fullName", uname)
    bio       = profile.get("biography", "")
    followers = profile.get("followersCount", 0)
    posts_cnt = profile.get("postsCount", 0)
    ext_url   = profile.get("externalUrl", "") or ""
    ig_url    = f"https://instagram.com/{uname}"

    # Profile picture (local b64)
    pic_b64 = get_local_image_b64(f"data/images/profiles/{safe_fn(uname)}.jpg", img_cache)
    if pic_b64:
        pic_src = f"data:image/jpeg;base64,{pic_b64}"
    else:
        pic_src = f"https://ui-avatars.com/api/?name={fname.replace(' ','+')}&background=222&color=fff&size=120"

    # Stats colors
    eng_color = "#22c55e" if eng_rate > 3 else ("#f97316" if eng_rate > 1 else "#888")

    # CTA
    cta_label, cta_badge_html = get_cta_html(ext_url, bio)

    # Services
    all_caps = " ".join([(p.get("caption") or "") for p in user_posts])
    services = classify_services(bio, all_caps)

    # Phone in bio
    phones = re.findall(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\d{10})', bio or "")
    phone_html = f'<div style="color:#4ade80;font-size:13px;font-weight:600;margin-top:6px">📞 {" | ".join(phones[:2])}</div>' if phones else ""

    # Top 3 posts
    top_posts = sorted(user_posts, key=lambda p: p.get("likesCount", 0), reverse=True)[:3]
    post_cards_html = ""
    for post in top_posts:
        sc   = post.get("shortCode", "")
        img_b64 = get_local_image_b64(f"data/images/posts/{safe_fn(uname)}_{safe_fn(sc)}.jpg", img_cache)
        if img_b64:
            img_src = f"data:image/jpeg;base64,{img_b64}"
        else:
            img_src = post.get("displayUrl", "")
        likes_f    = format_number(post.get("likesCount", 0))
        comments_n = post.get("commentsCount", 0)
        caption    = (post.get("caption") or "")[:100].strip()
        if len(post.get("caption") or "") > 100:
            caption += "..."
        post_link  = post.get("url") or f"https://instagram.com/p/{sc}"
        tags       = post.get("hashtags", [])[:3]
        tags_html  = " ".join([f'<span style="background:#1a1a1a;color:#666;padding:1px 6px;border-radius:6px;font-size:10px">#{t}</span>' for t in tags])

        post_cards_html += f"""
        <a href="{post_link}" target="_blank" style="display:block;width:calc(33.33% - 6px);min-width:120px;
           background:#0f0f0f;border:1px solid #2a2a2a;border-radius:10px;overflow:hidden;
           text-decoration:none;color:#ddd;transition:border-color 0.2s;flex-shrink:0">
          <div style="aspect-ratio:1;overflow:hidden;background:#1a1a1a">
            <img src="{img_src}" style="width:100%;height:100%;object-fit:cover;display:block"/>
          </div>
          <div style="padding:8px 10px">
            <div style="font-size:12px;color:#aaa;margin-bottom:4px">❤️ {likes_f} &nbsp; 💬 {comments_n}</div>
            <div style="font-size:11px;color:#999;line-height:1.4;margin-bottom:4px">{caption}</div>
            <div>{tags_html}</div>
          </div>
        </a>"""

    posts_section = f"""
    <div style="margin-top:0">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#555;margin-bottom:8px">
        TOP POSTS ({len(top_posts)} mejores por likes)
      </div>
      <div style="display:flex;gap:9px;flex-wrap:wrap">
        {post_cards_html if post_cards_html else '<p style="color:#555;font-size:13px">Sin posts disponibles</p>'}
      </div>
    </div>"""

    # Global rank
    orig_rank = next((i+1 for i, p in enumerate(profiles_sorted) if p.get("username") == uname), 0)
    rank_colors = {1: ("#3a2a00","#fbbf24","👑"), 2: ("#1a1a2a","#94a3b8","🥈"), 3: ("#2a1a00","#c2692a","🥉")}
    rb_bg, rb_fg, rb_icon = rank_colors.get(orig_rank, ("#1a1a1a","#555",""))
    rank_label = f"<span style='background:{rb_bg};color:{rb_fg};padding:3px 10px;border-radius:12px;font-size:12px;font-weight:700'>{'#'+str(orig_rank)} {rb_icon}</span>"

    card_html = f"""
    <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:16px;
                overflow:hidden;margin-bottom:4px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">

      <!-- HEADER -->
      <div style="background:#222;padding:20px 24px;display:flex;gap:18px;align-items:flex-start;position:relative">
        <div style="position:absolute;top:16px;right:20px">{rank_label}</div>
        <img src="{pic_src}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:3px solid #333;flex-shrink:0"/>
        <div style="flex:1;min-width:0">
          <div style="font-size:20px;font-weight:800;color:#f0f0f0;margin-bottom:2px">{fname}</div>
          <a href="{ig_url}" target="_blank" style="color:#60a5fa;font-size:13px;text-decoration:none">@{uname}</a>
          <div style="display:flex;gap:20px;margin-top:10px;flex-wrap:wrap">
            <div style="text-align:center">
              <div style="font-size:18px;font-weight:700;color:#f0f0f0">{format_number(followers)}</div>
              <div style="font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.5px">Seguidores</div>
            </div>
            <div style="text-align:center">
              <div style="font-size:18px;font-weight:700;color:{eng_color}">{eng_rate}%</div>
              <div style="font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.5px">Engagement</div>
            </div>
            <div style="text-align:center">
              <div style="font-size:18px;font-weight:700;color:#f0f0f0">❤️ {avg_likes}</div>
              <div style="font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.5px">Avg Likes</div>
            </div>
            <div style="text-align:center">
              <div style="font-size:18px;font-weight:700;color:#f0f0f0">{posts_cnt}</div>
              <div style="font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.5px">Posts</div>
            </div>
          </div>
        </div>
      </div>

      <!-- BODY -->
      <div style="padding:20px 24px;display:grid;grid-template-columns:1fr 1.4fr;gap:28px">

        <!-- LEFT -->
        <div>
          <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#555;margin-bottom:6px">BIO</div>
          <p style="font-size:13px;color:#bbb;line-height:1.7;white-space:pre-line;margin:0 0 4px 0">{bio or '<em style="color:#444">Sin bio</em>'}</p>
          {phone_html}

          <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#555;margin:14px 0 6px 0">COMO CIERRA CLIENTES</div>
          {cta_badge_html}

          <div style="margin:14px 0 6px 0;display:flex;flex-wrap:wrap;gap:8px;align-items:center">
            <a href="{ig_url}" target="_blank"
               style="display:inline-block;padding:7px 16px;border-radius:8px;text-decoration:none;color:white;font-size:13px;font-weight:600;
                      background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045)">📸 Ver Instagram</a>
            {ext_btn_html(ext_url)}
          </div>

          <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:#555;margin:14px 0 6px 0">SERVICIOS</div>
          <div>{badges_html(services)}</div>
        </div>

        <!-- RIGHT: POSTS -->
        <div>{posts_section}</div>

      </div>
    </div>"""

    # Height: bigger if coach has posts (right column needs room for 3 post images)
    card_height = 720 if top_posts else 440
    components.html(card_html, height=card_height, scrolling=False)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(f"📊 {len(filtered)} coaches mostrados · {len(posts)} posts analizados · Datos de Instagram via Apify")
