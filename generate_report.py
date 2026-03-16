"""
generate_report.py
Generates a rich HTML competitive intelligence report from raw scraped data.
Shows competitor profiles, images, closing mechanisms, content strategy.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict
import re

sys.stdout.reconfigure(encoding='utf-8')

IMG_DIR = Path("data/images")

def safe_filename(name):
    return re.sub(r'[^\w\-_]', '_', name)

def local_profile_pic(username, fallback_name):
    local = IMG_DIR / "profiles" / f"{safe_filename(username)}.jpg"
    if local.exists():
        return str(local).replace("\\", "/")
    return f"https://ui-avatars.com/api/?name={fallback_name}&background=333&color=fff&size=120"

def local_post_img(username, short_code, cdn_url):
    local = IMG_DIR / "posts" / f"{safe_filename(username)}_{safe_filename(short_code)}.jpg"
    if local.exists():
        return str(local).replace("\\", "/")
    return cdn_url  # fallback to CDN

# ── Load data ──────────────────────────────────────────────────────────────────
DATA = Path("data/raw")

with open(DATA / "instagram_profiles.json", encoding="utf-8") as f:
    ig_profiles = json.load(f)

with open(DATA / "instagram_posts.json", encoding="utf-8") as f:
    ig_posts = json.load(f)

# Index posts by owner
posts_by_user = defaultdict(list)
for post in ig_posts:
    posts_by_user[post.get("ownerUsername", "")].append(post)

# ── Analyze each competitor ─────────────────────────────────────────────────────
def detect_cta(url, bio):
    """Detect how this coach closes clients."""
    url = (url or "").lower()
    bio_lower = (bio or "").lower()

    signals = []

    if "wa.me" in url or "wa.link" in url or "whatsapp" in url:
        signals.append(("💬 WhatsApp Directo", "green", "Cierra por DM/WhatsApp — fricción mínima"))
    if "linktr.ee" in url or "linkbio" in url or "linkin.bio" in url:
        signals.append(("🔗 Linktree/LinkBio", "blue", "Múltiples opciones de contacto"))
    if "forms.gle" in url or "docs.google.com/forms" in url:
        signals.append(("📋 Formulario de Aplicación", "purple", "Pre-califica leads con formulario — más premium"))
    if "hackeatumetabolismo" in url or "florecer" in url:
        signals.append(("🚀 Página de Ventas", "orange", "Funnel completo con landing page"))
    if "canva.site" in url or "rebrand.ly" in url or "beacons" in url:
        signals.append(("🌐 Mini-website", "teal", "Sitio propio para conversiones"))
    if not signals:
        if "wasap" in bio_lower or "whatsapp" in bio_lower or "829" in bio or "809" in bio or "849" in bio:
            signals.append(("📱 Teléfono/WhatsApp en Bio", "green", "Contacto directo en descripción"))
        elif "dm" in bio_lower or "mensaje" in bio_lower or "inbox" in bio_lower:
            signals.append(("📨 DM Directo", "gray", "Cierra por mensajes directos en Instagram"))
        else:
            signals.append(("👁️ Solo Orgánico", "red", "Sin CTA claro — solo contenido"))

    return signals

def extract_phone(bio):
    """Extract phone numbers from bio."""
    phones = re.findall(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\d{10})', bio or "")
    return phones[:2]

def classify_services(bio, captions_text):
    """Classify services offered."""
    text = (bio or "") + " " + (captions_text or "")
    text_lower = text.lower()
    services = []

    if any(w in text_lower for w in ["online", "virtual", "remoto", "distancia"]):
        services.append("🌐 Coaching Online")
    if any(w in text_lower for w in ["presencial", "gym", "gimnasio", "studio", "estudio"]):
        services.append("🏋️ Presencial")
    if any(w in text_lower for w in ["nutrici", "alimentaci", "dieta", "plan alimenticio"]):
        services.append("🥗 Nutrición")
    if any(w in text_lower for w in ["transform", "definici", "perder peso", "bajar de peso", "pérdida"]):
        services.append("🔥 Transformación Corporal")
    if any(w in text_lower for w in ["musculo", "fuerza", "hipertrofia", "volumen", "masa"]):
        services.append("💪 Ganancia Muscular")
    if any(w in text_lower for w in ["evaluaci", "assess", "diagnos"]):
        services.append("📊 Evaluación Física")
    if any(w in text_lower for w in ["grupo", "clase", "boot camp", "bootcamp"]):
        services.append("👥 Clases Grupales")

    return services or ["📋 Entrenamiento General"]

def analyze_content_strategy(posts):
    """Analyze what content this coach posts."""
    all_text = " ".join([(p.get("caption") or "") for p in posts]).lower()
    strategies = []

    if any(w in all_text for w in ["testimonio", "resultado", "transform", "antes", "después"]):
        strategies.append("✅ Testimonios/Resultados")
    if any(w in all_text for w in ["tip", "consejo", "aprende", "sabes que", "sabías"]):
        strategies.append("💡 Contenido Educativo")
    if any(w in all_text for w in ["motivaci", "inspira", "puedes", "tú puedes"]):
        strategies.append("🔥 Motivacional")
    if any(w in all_text for w in ["venta", "oferta", "precio", "plan", "disponible"]):
        strategies.append("💰 Venta Directa")
    if any(w in all_text for w in ["reel", "baile", "challenge", "trend"]):
        strategies.append("🎬 Reels/Tendencias")

    avg_likes = sum(p.get("likesCount", 0) for p in posts) / len(posts) if posts else 0
    avg_comments = sum(p.get("commentsCount", 0) for p in posts) / len(posts) if posts else 0

    return strategies, round(avg_likes), round(avg_comments)

# Sort profiles by followers
ig_profiles_sorted = sorted(ig_profiles, key=lambda x: x.get("followersCount", 0), reverse=True)

# ── Build HTML ─────────────────────────────────────────────────────────────────
def format_number(n):
    if n >= 1000000:
        return f"{n/1000000:.1f}M"
    if n >= 1000:
        return f"{n/1000:.1f}K"
    return str(n)

def truncate(text, max_len=200):
    if not text:
        return ""
    text = text.strip()
    return text[:max_len] + "..." if len(text) > max_len else text

# Build competitor cards HTML
cards_html = ""
for rank, profile in enumerate(ig_profiles_sorted, 1):
    username = profile.get("username", "")
    full_name = profile.get("fullName", username)
    bio = profile.get("biography", "")
    followers = profile.get("followersCount", 0)
    following = profile.get("followsCount", 0)
    posts_count = profile.get("postsCount", 0)
    profile_pic = local_profile_pic(username, full_name.replace(" ", "+"))
    external_url = profile.get("externalUrl", "") or ""
    ig_url = f"https://instagram.com/{username}"

    # Analysis
    cta_signals = detect_cta(external_url, bio)
    phones = extract_phone(bio)
    user_posts = posts_by_user.get(username, [])

    all_captions = " ".join([(p.get("caption") or "") for p in user_posts])
    services = classify_services(bio, all_captions)
    content_strategies, avg_likes, avg_comments = analyze_content_strategy(user_posts)

    followers_f = format_number(followers)

    # Engagement rate
    eng_rate = 0
    if followers > 0 and user_posts:
        total_likes = sum(p.get("likesCount", 0) for p in user_posts)
        total_comments = sum(p.get("commentsCount", 0) for p in user_posts)
        eng_rate = round((total_likes + total_comments) / len(user_posts) / followers * 100, 2)

    # Top 3 posts
    top_posts = sorted(user_posts, key=lambda p: p.get("likesCount", 0), reverse=True)[:3]

    post_cards = ""
    for post in top_posts:
        short_code = post.get("shortCode", "")
        cdn_url = post.get("displayUrl", "")
        img_url = local_post_img(username, short_code, cdn_url)
        caption_short = truncate(post.get("caption", ""), 120)
        likes = format_number(post.get("likesCount", 0))
        comments = post.get("commentsCount", 0)
        post_url = post.get("url", f"https://instagram.com/p/{short_code}")
        hashtags = post.get("hashtags", [])[:4]
        hashtags_html = " ".join([f'<span class="tag">#{h}</span>' for h in hashtags])

        post_cards += f"""
        <a href="{post_url}" target="_blank" class="post-card">
            <div class="post-img-wrap">
                <img src="{img_url}" alt="post" loading="lazy" onerror="this.parentElement.style.background='#2a2a2a';this.style.display='none'"/>
            </div>
            <div class="post-meta">
                <span>❤️ {likes}</span>
                <span>💬 {comments}</span>
            </div>
            <div class="post-caption">{caption_short}</div>
            <div class="post-tags">{hashtags_html}</div>
        </a>"""

    # CTA badges
    cta_badges = ""
    for label, color, tooltip in cta_signals:
        cta_badges += f'<span class="cta-badge cta-{color}" title="{tooltip}">{label}</span>'

    # Services badges
    service_badges = "".join([f'<span class="service-badge">{s}</span>' for s in services])
    content_badges = "".join([f'<span class="content-badge">{s}</span>' for s in content_strategies])

    # External link button
    ext_btn = ""
    if external_url:
        ext_label = "🔗 Link en Bio"
        if "wa.me" in external_url or "wa.link" in external_url:
            ext_label = "💬 WhatsApp"
        elif "forms.gle" in external_url or "google.com/forms" in external_url:
            ext_label = "📋 Formulario"
        elif "linktr.ee" in external_url:
            ext_label = "🌳 Linktree"
        elif "hackeatumetabolismo" in external_url:
            ext_label = "🚀 Sales Page"
        ext_btn = f'<a href="{external_url}" target="_blank" class="ext-btn">{ext_label}</a>'

    phone_html = ""
    if phones:
        phone_html = f'<div class="phone-row">📞 {" | ".join(phones)}</div>'

    rank_badge = ""
    if rank == 1:
        rank_badge = '<div class="rank-badge gold">👑 #1</div>'
    elif rank == 2:
        rank_badge = '<div class="rank-badge silver">🥈 #2</div>'
    elif rank == 3:
        rank_badge = '<div class="rank-badge bronze">🥉 #3</div>'
    else:
        rank_badge = f'<div class="rank-badge default">#{rank}</div>'

    eng_color = "eng-high" if eng_rate > 3 else ("eng-mid" if eng_rate > 1 else "eng-low")

    cards_html += f"""
    <div class="coach-card" id="{username}">
        <div class="card-header">
            {rank_badge}
            <div class="avatar-wrap">
                <img src="{profile_pic}" alt="{full_name}" class="avatar" loading="lazy"/>
            </div>
            <div class="coach-info">
                <h2 class="coach-name">{full_name}</h2>
                <a href="{ig_url}" target="_blank" class="coach-handle">@{username}</a>
                <div class="stats-row">
                    <div class="stat-item">
                        <div class="stat-val">{followers_f}</div>
                        <div class="stat-label">Seguidores</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-val {eng_color}">{eng_rate}%</div>
                        <div class="stat-label">Engagement</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-val">❤️ {avg_likes}</div>
                        <div class="stat-label">Avg Likes</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-val">{posts_count}</div>
                        <div class="stat-label">Posts</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card-body">
            <div class="section-row">
                <div class="left-col">
                    <div class="section-label">BIO</div>
                    <p class="bio-text">{bio or '<em style="color:#666">Sin bio</em>'}</p>
                    {phone_html}

                    <div class="section-label">COMO CIERRA CLIENTES</div>
                    <div class="cta-row">{cta_badges}</div>
                    {"<p class='cta-detail'>" + cta_signals[0][2] + "</p>" if cta_signals else ""}

                    <div class="link-row">
                        <a href="{ig_url}" target="_blank" class="ig-btn">📸 Ver Instagram</a>
                        {ext_btn}
                    </div>

                    <div class="section-label">SERVICIOS</div>
                    <div class="badges-wrap">{service_badges}</div>

                    <div class="section-label">ESTRATEGIA DE CONTENIDO</div>
                    <div class="badges-wrap">{content_badges}</div>
                </div>

                <div class="right-col">
                    <div class="section-label">TOP POSTS ({len(top_posts)} mejores)</div>
                    <div class="posts-row">
                        {post_cards if post_cards else '<p style="color:#666">Sin posts disponibles</p>'}
                    </div>
                </div>
            </div>
        </div>
    </div>"""

# Summary stats for header
total_coaches = len(ig_profiles_sorted)
total_followers = sum(p.get("followersCount", 0) for p in ig_profiles_sorted)
avg_followers = total_followers // total_coaches if total_coaches else 0

# Count CTAs
whatsapp_count = sum(1 for p in ig_profiles_sorted
    if "wa.me" in (p.get("externalUrl") or "") or "wa.link" in (p.get("externalUrl") or "")
    or "wasap" in (p.get("biography") or "").lower() or "whatsapp" in (p.get("biography") or "").lower())
forms_count = sum(1 for p in ig_profiles_sorted
    if "forms.gle" in (p.get("externalUrl") or "") or "google.com/forms" in (p.get("externalUrl") or ""))
linktree_count = sum(1 for p in ig_profiles_sorted
    if "linktr.ee" in (p.get("externalUrl") or "") or "linkbio" in (p.get("externalUrl") or ""))

# Top 5 for quick nav
top5_nav = ""
for p in ig_profiles_sorted[:7]:
    uname = p["username"]
    fname = p.get("fullName", uname).replace("'", "")
    pic = local_profile_pic(uname, fname.replace(" ", "+"))
    top5_nav += f'<a href="#{uname}" class="nav-coach"><img src="{pic}"/> {fname}</a>'

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Inteligencia Competitiva — Coaches Fitness RD 🇩🇴</title>
<style>
  :root {{
    --bg: #0f0f0f;
    --card: #1a1a1a;
    --card2: #222;
    --border: #2a2a2a;
    --accent: #ff4444;
    --accent2: #ff8800;
    --text: #f0f0f0;
    --muted: #888;
    --green: #22c55e;
    --blue: #3b82f6;
    --purple: #a855f7;
    --orange: #f97316;
    --teal: #14b8a6;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }}

  /* NAV */
  .navbar {{ background:#111; border-bottom:1px solid var(--border); padding:16px 32px; display:flex; align-items:center; gap:24px; position:sticky; top:0; z-index:100; }}
  .navbar-title {{ font-size:18px; font-weight:700; color:var(--accent); white-space:nowrap; }}
  .nav-coaches {{ display:flex; gap:12px; overflow-x:auto; flex:1; }}
  .nav-coach {{ display:flex; align-items:center; gap:8px; padding:6px 12px; background:var(--card); border-radius:20px; text-decoration:none; color:var(--text); font-size:13px; white-space:nowrap; border:1px solid var(--border); transition:all 0.2s; flex-shrink:0; }}
  .nav-coach:hover {{ border-color:var(--accent); background:#2a1a1a; }}
  .nav-coach img {{ width:28px; height:28px; border-radius:50%; object-fit:cover; }}

  /* HERO */
  .hero {{ background:linear-gradient(135deg, #1a0000 0%, #0f0f0f 50%, #001a0a 100%); padding:48px 32px; text-align:center; border-bottom:1px solid var(--border); }}
  .hero h1 {{ font-size:36px; font-weight:800; background:linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:8px; }}
  .hero p {{ color:var(--muted); font-size:16px; margin-bottom:32px; }}
  .summary-stats {{ display:flex; gap:24px; justify-content:center; flex-wrap:wrap; }}
  .summary-stat {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:20px 28px; text-align:center; }}
  .summary-stat-val {{ font-size:32px; font-weight:800; color:var(--accent); }}
  .summary-stat-label {{ font-size:13px; color:var(--muted); margin-top:4px; }}

  /* KEY INSIGHTS */
  .insights-section {{ max-width:1200px; margin:32px auto; padding:0 24px; }}
  .insights-title {{ font-size:22px; font-weight:700; margin-bottom:16px; }}
  .insights-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:16px; }}
  .insight-card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:20px; }}
  .insight-icon {{ font-size:28px; margin-bottom:8px; }}
  .insight-title {{ font-size:15px; font-weight:700; margin-bottom:6px; }}
  .insight-body {{ font-size:13px; color:var(--muted); line-height:1.6; }}
  .insight-highlight {{ color:var(--accent); font-weight:600; }}

  /* COACHES LIST */
  .coaches-section {{ max-width:1200px; margin:0 auto; padding:0 24px 48px; }}
  .section-header {{ font-size:22px; font-weight:700; margin-bottom:20px; padding-top:16px; }}

  /* COACH CARD */
  .coach-card {{ background:var(--card); border:1px solid var(--border); border-radius:16px; margin-bottom:32px; overflow:hidden; transition:border-color 0.2s; }}
  .coach-card:hover {{ border-color:#444; }}
  .card-header {{ background:var(--card2); padding:24px; display:flex; gap:20px; align-items:flex-start; position:relative; }}
  .rank-badge {{ position:absolute; top:16px; right:16px; font-size:13px; font-weight:700; padding:4px 10px; border-radius:20px; }}
  .rank-badge.gold {{ background:#3a2a00; color:#fbbf24; border:1px solid #854d0e; }}
  .rank-badge.silver {{ background:#1a1a2a; color:#94a3b8; border:1px solid #475569; }}
  .rank-badge.bronze {{ background:#2a1a00; color:#c2692a; border:1px solid #7c2d12; }}
  .rank-badge.default {{ background:#1a1a1a; color:#666; border:1px solid #333; }}
  .avatar-wrap {{ flex-shrink:0; }}
  .avatar {{ width:90px; height:90px; border-radius:50%; object-fit:cover; border:3px solid var(--border); }}
  .coach-info {{ flex:1; }}
  .coach-name {{ font-size:22px; font-weight:800; margin-bottom:2px; }}
  .coach-handle {{ color:var(--blue); text-decoration:none; font-size:14px; display:block; margin-bottom:12px; }}
  .coach-handle:hover {{ text-decoration:underline; }}
  .stats-row {{ display:flex; gap:20px; flex-wrap:wrap; }}
  .stat-item {{ text-align:center; }}
  .stat-val {{ font-size:18px; font-weight:700; }}
  .stat-label {{ font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; }}
  .eng-high {{ color:var(--green); }}
  .eng-mid {{ color:var(--accent2); }}
  .eng-low {{ color:var(--muted); }}

  /* CARD BODY */
  .card-body {{ padding:24px; }}
  .section-row {{ display:grid; grid-template-columns:1fr 1fr; gap:32px; }}
  @media(max-width:768px) {{ .section-row {{ grid-template-columns:1fr; }} }}
  .section-label {{ font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:var(--muted); margin-bottom:8px; margin-top:16px; }}
  .section-label:first-child {{ margin-top:0; }}
  .bio-text {{ font-size:14px; line-height:1.7; color:#ccc; white-space:pre-line; }}
  .phone-row {{ font-size:13px; color:var(--green); margin-top:8px; font-weight:600; }}

  /* CTAs */
  .cta-row {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:8px; }}
  .cta-badge {{ display:inline-flex; align-items:center; gap:4px; padding:5px 12px; border-radius:20px; font-size:13px; font-weight:600; cursor:default; }}
  .cta-green {{ background:#052e16; color:#4ade80; border:1px solid #166534; }}
  .cta-blue {{ background:#0c1a2e; color:#60a5fa; border:1px solid #1e3a5f; }}
  .cta-purple {{ background:#1a0a2e; color:#c084fc; border:1px solid #5b21b6; }}
  .cta-orange {{ background:#2e1000; color:#fb923c; border:1px solid #9a3412; }}
  .cta-teal {{ background:#021a18; color:#2dd4bf; border:1px solid #0f766e; }}
  .cta-red {{ background:#2e0000; color:#f87171; border:1px solid #991b1b; }}
  .cta-gray {{ background:#1a1a1a; color:#9ca3af; border:1px solid #374151; }}
  .cta-detail {{ font-size:12px; color:var(--muted); margin-top:4px; font-style:italic; }}

  /* LINKS */
  .link-row {{ display:flex; gap:10px; flex-wrap:wrap; margin:12px 0; }}
  .ig-btn {{ display:inline-flex; align-items:center; gap:6px; padding:8px 16px; background:linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045); border-radius:8px; text-decoration:none; color:white; font-size:13px; font-weight:600; transition:opacity 0.2s; }}
  .ig-btn:hover {{ opacity:0.85; }}
  .ext-btn {{ display:inline-flex; align-items:center; gap:6px; padding:8px 16px; background:#1a1a1a; border:1px solid var(--border); border-radius:8px; text-decoration:none; color:var(--text); font-size:13px; font-weight:600; transition:all 0.2s; }}
  .ext-btn:hover {{ border-color:var(--accent2); color:var(--accent2); }}

  /* BADGES */
  .badges-wrap {{ display:flex; flex-wrap:wrap; gap:6px; }}
  .service-badge {{ background:#0a1a0a; color:#86efac; border:1px solid #166534; padding:4px 10px; border-radius:12px; font-size:12px; }}
  .content-badge {{ background:#0a0a1a; color:#93c5fd; border:1px solid #1e3a5f; padding:4px 10px; border-radius:12px; font-size:12px; }}
  .tag {{ background:#1a1a1a; color:#888; padding:2px 7px; border-radius:8px; font-size:11px; }}

  /* POSTS */
  .posts-row {{ display:flex; gap:12px; flex-wrap:wrap; }}
  .post-card {{ background:var(--bg); border:1px solid var(--border); border-radius:10px; overflow:hidden; width:calc(33.33% - 8px); min-width:140px; text-decoration:none; color:var(--text); transition:border-color 0.2s; display:block; }}
  .post-card:hover {{ border-color:var(--accent); }}
  .post-img-wrap {{ width:100%; aspect-ratio:1; overflow:hidden; background:#1a1a1a; }}
  .post-img-wrap img {{ width:100%; height:100%; object-fit:cover; transition:transform 0.3s; display:block; }}
  .post-card:hover .post-img-wrap img {{ transform:scale(1.05); }}
  .post-meta {{ display:flex; gap:10px; padding:8px 10px 4px; font-size:12px; color:var(--muted); }}
  .post-caption {{ padding:0 10px 6px; font-size:11px; color:#aaa; line-height:1.5; }}
  .post-tags {{ padding:0 10px 8px; display:flex; flex-wrap:wrap; gap:4px; }}

  /* FOOTER */
  .footer {{ background:#111; border-top:1px solid var(--border); padding:24px 32px; text-align:center; color:var(--muted); font-size:13px; }}
  .footer a {{ color:var(--blue); text-decoration:none; }}
</style>
</head>
<body>

<nav class="navbar">
  <div class="navbar-title">🏆 Competencia RD</div>
  <div class="nav-coaches">
    {top5_nav}
  </div>
</nav>

<div class="hero">
  <h1>Inteligencia Competitiva — Coaches Fitness RD 🇩🇴</h1>
  <p>Análisis completo de {total_coaches} competidores en Instagram • Datos scraped en tiempo real</p>
  <div class="summary-stats">
    <div class="summary-stat">
      <div class="summary-stat-val">{total_coaches}</div>
      <div class="summary-stat-label">Competidores Analizados</div>
    </div>
    <div class="summary-stat">
      <div class="summary-stat-val">{format_number(total_followers)}</div>
      <div class="summary-stat-label">Seguidores Totales</div>
    </div>
    <div class="summary-stat">
      <div class="summary-stat-val">{format_number(avg_followers)}</div>
      <div class="summary-stat-label">Promedio por Coach</div>
    </div>
    <div class="summary-stat">
      <div class="summary-stat-val">{whatsapp_count}</div>
      <div class="summary-stat-label">Cierran por WhatsApp</div>
    </div>
    <div class="summary-stat">
      <div class="summary-stat-val">{forms_count}</div>
      <div class="summary-stat-label">Usan Formulario</div>
    </div>
    <div class="summary-stat">
      <div class="summary-stat-val">{len(ig_posts)}</div>
      <div class="summary-stat-label">Posts Analizados</div>
    </div>
  </div>
</div>

<div class="insights-section">
  <div class="insights-title">🔍 Insights Clave — Cómo Funciona la Competencia</div>
  <div class="insights-grid">
    <div class="insight-card">
      <div class="insight-icon">💬</div>
      <div class="insight-title">WhatsApp es el Rey del Cierre</div>
      <div class="insight-body">
        <span class="insight-highlight">{whatsapp_count} de {total_coaches} coaches</span> cierran directamente por WhatsApp.
        Algunos lo muestran en bio, otros redirigen a wa.me con número pre-cargado.
        Es el canal con menos fricción en RD.
      </div>
    </div>
    <div class="insight-card">
      <div class="insight-icon">📋</div>
      <div class="insight-title">Formularios = Coaches Premium</div>
      <div class="insight-body">
        <span class="insight-highlight">{forms_count} coaches</span> usan Google Forms para pre-calificar leads.
        Esto indica un posicionamiento más premium — pre-seleccionan quién entra al programa
        y crean percepción de exclusividad.
      </div>
    </div>
    <div class="insight-card">
      <div class="insight-icon">🚀</div>
      <div class="insight-title">Pocos Tienen Funnel Real</div>
      <div class="insight-body">
        Solo <span class="insight-highlight">1-2 coaches</span> tienen landing pages/sales pages reales
        (ej: hackeatumetabolismo.com). La mayoría va directo Bio → WhatsApp sin
        nurturing, email capture ni automation.
      </div>
    </div>
    <div class="insight-card">
      <div class="insight-icon">👑</div>
      <div class="insight-title">Top 2 Dominan el Mercado</div>
      <div class="insight-body">
        <span class="insight-highlight">jc_simo ({format_number(368057)}) y davidsoto91 ({format_number(301337)})</span>
        concentran la mayoría de followers. Pero hay un mercado medio (10K-70K)
        con alta engagement que es más vulnerable.
      </div>
    </div>
    <div class="insight-card">
      <div class="insight-icon">📱</div>
      <div class="insight-title">Estrategia de Contenido Repetitiva</div>
      <div class="insight-body">
        La mayoría usa solo <span class="insight-highlight">motivacional + resultados</span>.
        Muy pocos hacen contenido educativo profundo o series.
        Oportunidad: contenido de alta autoridad y especificidad.
      </div>
    </div>
    <div class="insight-card">
      <div class="insight-icon">💰</div>
      <div class="insight-title">Precios Opacos</div>
      <div class="insight-body">
        <span class="insight-highlight">Ninguno muestra precios públicamente</span> en Instagram.
        El modelo es "contáctame" — negociación privada.
        Esto puede ser una oportunidad si ofreces transparencia de precios.
      </div>
    </div>
  </div>
</div>

<div class="coaches-section">
  <div class="section-header">📊 Perfiles Completos — Ranking por Seguidores</div>
  {cards_html}
</div>

<div class="footer">
  Generado el 2026-03-16 · {len(ig_profiles)} coaches · {len(ig_posts)} posts analizados ·
  Datos via <a href="https://apify.com" target="_blank">Apify</a> · Gabifit Competition Intelligence
</div>

</body>
</html>"""

output_path = Path("competition_report.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Report generated: {output_path}")
print(f"Coaches: {len(ig_profiles_sorted)}")
print(f"Posts analyzed: {len(ig_posts)}")
print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")
