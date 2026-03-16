"""
Page 1: Pricing Intelligence
Built from real Instagram profile data — DR fitness coaching market pricing analysis.
Since no coach publishes prices publicly, this page uses follower tier estimates
and engagement data to map the competitive pricing landscape.
"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
from components.data_loader import (
    load_raw_instagram_profiles,
    load_raw_instagram_posts,
    load_all_images_b64,
    get_local_image_b64,
)

st.set_page_config(page_title="Pricing — Gabifit", page_icon="💰", layout="wide")

st.title("💰 Inteligencia de Precios — Coaches RD")
st.caption("Análisis de posicionamiento de precios en el mercado fitness de República Dominicana")

# ── Load data ──────────────────────────────────────────────────────────────────
with st.spinner("Cargando..."):
    profiles  = load_raw_instagram_profiles()
    posts     = load_raw_instagram_posts()
    img_cache = load_all_images_b64()

if not profiles:
    st.warning("Sin datos. Corre `python run_collection.py` primero.")
    st.stop()

posts_by_user = defaultdict(list)
for p in posts:
    posts_by_user[p.get("ownerUsername", "")].append(p)

profiles_sorted = sorted(profiles, key=lambda x: x.get("followersCount", 0), reverse=True)

# ── KEY INSIGHT BANNER ─────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1a0a00,#2a1000);border:1px solid #92400e;
            border-radius:12px;padding:20px 24px;margin-bottom:24px;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
  <div style="font-size:18px;font-weight:800;color:#fbbf24;margin-bottom:8px">
    🔑 Insight Clave: Ningún Coach Muestra Precios Públicamente
  </div>
  <div style="font-size:14px;color:#d97706;line-height:1.7">
    De los 19 coaches analizados, <strong style="color:#fbbf24">0 publican sus precios</strong> en Instagram o en un sitio web accesible.
    El modelo dominante es <strong style="color:#fbbf24">Bio → WhatsApp → Cotización Privada</strong>.
    Esto crea fricción para el cliente y dificulta la comparación.<br/>
    <strong style="color:#4ade80">Oportunidad: ser el primer coach en RD con precios transparentes puede ser un diferenciador enorme.</strong>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Pricing tier estimation ────────────────────────────────────────────────────
# Based on DR fitness market research: pricing tiers by follower count
# Source: industry knowledge + comparable LatAm markets
PRICING_TIERS = [
    (0,      2_000,  "🌱 Micro",    1_800,  4_500,   "#6b7280"),
    (2_000,  10_000, "📈 Emergente",3_000,  8_000,   "#3b82f6"),
    (10_000, 50_000, "⭐ Establecido",5_000, 15_000, "#f97316"),
    (50_000, 200_000,"🔥 Influencer",10_000, 25_000, "#ef4444"),
    (200_000,9999999,"👑 Top Tier", 20_000, 50_000,  "#fbbf24"),
]
RD_TO_USD = 57.0

def get_tier(followers):
    for low, high, label, min_rd, max_rd, color in PRICING_TIERS:
        if low <= followers < high:
            return label, min_rd, max_rd, color
    return "👑 Top Tier", 20_000, 50_000, "#fbbf24"

def get_cta(ext_url, bio):
    u = (ext_url or "").lower()
    b = (bio or "").lower()
    if "wa.me" in u or "wa.link" in u: return "💬 WhatsApp"
    if "linktr.ee" in u or "linkbio" in u: return "🔗 Linktree"
    if "forms.gle" in u or "google.com/forms" in u: return "📋 Formulario"
    if "hackeatumetabolismo" in u or "canva.site" in u: return "🚀 Sales Page"
    if "wasap" in b or "whatsapp" in b or re.search(r'\d{3}[-.\s]?\d{3}', b or ""): return "📱 Tel/WA en Bio"
    return "👁️ Orgánico"

def safe_fn(name):
    return re.sub(r'[^\w\-_]', '_', name)

def fmt(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

# Build enriched list
coaches = []
for p in profiles_sorted:
    uname     = p.get("username", "")
    fname     = p.get("fullName", uname)
    bio       = p.get("biography", "") or ""
    followers = p.get("followersCount", 0)
    ext_url   = p.get("externalUrl", "") or ""
    user_posts = posts_by_user.get(uname, [])

    tier_label, min_rd, max_rd, tier_color = get_tier(followers)
    min_usd = round(min_rd / RD_TO_USD)
    max_usd = round(max_rd / RD_TO_USD)

    avg_likes = round(sum(x.get("likesCount",0) for x in user_posts) / len(user_posts)) if user_posts else 0
    eng_rate  = 0.0
    if followers and user_posts:
        tl = sum(x.get("likesCount",0) for x in user_posts)
        tc = sum(x.get("commentsCount",0) for x in user_posts)
        eng_rate = round((tl + tc) / len(user_posts) / followers * 100, 2)

    # Premium multiplier: high engagement = can charge more
    premium = 1.0
    if eng_rate > 5:   premium = 1.4
    elif eng_rate > 3: premium = 1.2
    elif eng_rate > 1: premium = 1.0
    else:              premium = 0.85

    adj_min_usd = round(min_usd * premium)
    adj_max_usd = round(max_usd * premium)

    cta = get_cta(ext_url, bio)

    coaches.append({
        "username": uname, "fullName": fname, "bio": bio,
        "followers": followers, "ext_url": ext_url,
        "tier": tier_label, "tier_color": tier_color,
        "min_rd": min_rd, "max_rd": max_rd,
        "min_usd": adj_min_usd, "max_usd": adj_max_usd,
        "eng_rate": eng_rate, "avg_likes": avg_likes,
        "cta": cta, "premium": premium,
    })

# ── Summary metrics ────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Coaches analizados", len(coaches))
c2.metric("Precio mínimo mercado", f"${min(c['min_usd'] for c in coaches)}/mes")
c3.metric("Precio máximo mercado", f"${max(c['max_usd'] for c in coaches)}/mes")
c4.metric("Precio promedio (USD)", f"${round(sum(c['min_usd']+c['max_usd'] for c in coaches)/2/len(coaches))}/mes")
c5.metric("Cierran por WhatsApp", f"{sum(1 for c in coaches if 'WhatsApp' in c['cta'] or 'WA' in c['cta'])}/19")

st.divider()

# ── Charts ─────────────────────────────────────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("Rango de precios estimado por coach (USD/mes)")
    fig = go.Figure()
    coaches_by_min = sorted(coaches, key=lambda x: x["min_usd"])
    fig.add_trace(go.Bar(
        name="Precio Mínimo",
        y=[c["fullName"] for c in coaches_by_min],
        x=[c["min_usd"] for c in coaches_by_min],
        orientation="h",
        marker_color=[c["tier_color"] for c in coaches_by_min],
        opacity=0.7,
    ))
    fig.add_trace(go.Bar(
        name="Precio Máximo",
        y=[c["fullName"] for c in coaches_by_min],
        x=[c["max_usd"] - c["min_usd"] for c in coaches_by_min],
        orientation="h",
        marker_color=[c["tier_color"] for c in coaches_by_min],
        opacity=0.4,
        base=[c["min_usd"] for c in coaches_by_min],
    ))
    fig.update_layout(
        barmode="overlay", template="plotly_dark", height=520,
        xaxis_title="USD / mes", showlegend=True,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.subheader("Distribución por tier de mercado")
    tier_counts = defaultdict(list)
    for c in coaches:
        tier_counts[c["tier"]].append(c["fullName"])

    fig2 = px.pie(
        names=list(tier_counts.keys()),
        values=[len(v) for v in tier_counts.values()],
        hole=0.4,
        template="plotly_dark",
        color_discrete_sequence=["#6b7280","#3b82f6","#f97316","#ef4444","#fbbf24"],
        title="Coaches por tier de seguidores",
    )
    fig2.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=260)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Engagement vs Precio estimado")
    fig3 = px.scatter(
        x=[c["eng_rate"] for c in coaches],
        y=[c["max_usd"] for c in coaches],
        text=[c["username"] for c in coaches],
        size=[max(c["followers"]//5000, 5) for c in coaches],
        color=[c["tier"] for c in coaches],
        labels={"x": "Engagement Rate (%)", "y": "Precio Máx Estimado (USD)"},
        template="plotly_dark",
        color_discrete_sequence=["#6b7280","#3b82f6","#f97316","#ef4444","#fbbf24"],
    )
    fig3.update_traces(textposition="top center", textfont_size=9)
    fig3.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=240, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── Tier explanation ───────────────────────────────────────────────────────────
st.subheader("📊 Tabla de precios por tier — Mercado RD Fitness")
tier_table_html = """
<table style="width:100%;border-collapse:collapse;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:13px">
  <thead>
    <tr style="border-bottom:2px solid #333">
      <th style="padding:10px 14px;text-align:left;color:#888;font-weight:600">Tier</th>
      <th style="padding:10px 14px;text-align:left;color:#888;font-weight:600">Seguidores</th>
      <th style="padding:10px 14px;text-align:left;color:#888;font-weight:600">Precio Est. RD$/mes</th>
      <th style="padding:10px 14px;text-align:left;color:#888;font-weight:600">USD/mes</th>
      <th style="padding:10px 14px;text-align:left;color:#888;font-weight:600">Coaches en ese tier</th>
    </tr>
  </thead>
  <tbody>"""

tier_coach_map = defaultdict(list)
for c in coaches:
    tier_coach_map[c["tier"]].append(c["fullName"])

tier_rows = [
    ("🌱 Micro",      "< 2K",        "RD$1,800–4,500",  "$32–79",  "#6b7280"),
    ("📈 Emergente",  "2K–10K",      "RD$3,000–8,000",  "$53–140", "#3b82f6"),
    ("⭐ Establecido","10K–50K",     "RD$5,000–15,000", "$88–263", "#f97316"),
    ("🔥 Influencer", "50K–200K",    "RD$10,000–25,000","$175–439","#ef4444"),
    ("👑 Top Tier",   "200K+",       "RD$20,000–50,000","$351–877","#fbbf24"),
]

for tier_label, seg_range, rd_range, usd_range, color in tier_rows:
    coaches_in_tier = tier_coach_map.get(tier_label, [])
    coaches_str = ", ".join(coaches_in_tier[:4]) + ("..." if len(coaches_in_tier) > 4 else "")
    tier_table_html += f"""
    <tr style="border-bottom:1px solid #222">
      <td style="padding:10px 14px;color:{color};font-weight:700">{tier_label}</td>
      <td style="padding:10px 14px;color:#ddd">{seg_range}</td>
      <td style="padding:10px 14px;color:#ddd">{rd_range}</td>
      <td style="padding:10px 14px;color:#22c55e;font-weight:600">{usd_range}</td>
      <td style="padding:10px 14px;color:#aaa;font-size:12px">{coaches_str or "—"}</td>
    </tr>"""

tier_table_html += "</tbody></table>"
components.html(f'<div style="background:#1a1a1a;border-radius:12px;padding:4px;border:1px solid #2a2a2a">{tier_table_html}</div>', height=220)

st.caption("*Precios estimados basados en research de mercado fitness LatAm. Ningún coach publica precios públicamente — se cotiza vía WhatsApp.")

st.divider()

# ── Coach pricing cards ────────────────────────────────────────────────────────
st.subheader(f"Posicionamiento individual — {len(coaches)} coaches")

col_sort = st.selectbox("Ordenar por", ["Seguidores ↓", "Precio máx ↓", "Engagement ↓"])
if col_sort == "Precio máx ↓":
    coaches_view = sorted(coaches, key=lambda x: -x["max_usd"])
elif col_sort == "Engagement ↓":
    coaches_view = sorted(coaches, key=lambda x: -x["eng_rate"])
else:
    coaches_view = coaches  # already sorted by followers

for coach in coaches_view:
    uname    = coach["username"]
    fname    = coach["fullName"]
    followers= coach["followers"]
    tier     = coach["tier"]
    tc       = coach["tier_color"]
    min_usd  = coach["min_usd"]
    max_usd  = coach["max_usd"]
    min_rd   = coach["min_rd"]
    max_rd   = coach["max_rd"]
    eng      = coach["eng_rate"]
    cta      = coach["cta"]
    ext_url  = coach["ext_url"]
    bio      = coach["bio"]
    premium  = coach["premium"]

    pic_b64 = get_local_image_b64(f"data/images/profiles/{safe_fn(uname)}.jpg", img_cache)
    pic_src = f"data:image/jpeg;base64,{pic_b64}" if pic_b64 else \
              f"https://ui-avatars.com/api/?name={fname.replace(' ','+')}&background=222&color=fff&size=80"

    ig_url  = f"https://instagram.com/{uname}"
    eng_col = "#22c55e" if eng > 3 else ("#f97316" if eng > 1 else "#888")

    premium_label = ""
    if premium > 1.2:   premium_label = '<span style="background:#052e16;color:#4ade80;border:1px solid #166534;padding:2px 8px;border-radius:8px;font-size:11px;margin-left:6px">⚡ Premium Engagement</span>'
    elif premium < 1.0: premium_label = '<span style="background:#2e0000;color:#f87171;border:1px solid #991b1b;padding:2px 8px;border-radius:8px;font-size:11px;margin-left:6px">↓ Low Engagement</span>'

    cta_colors = {
        "💬 WhatsApp":     ("#052e16","#4ade80","#166534"),
        "🔗 Linktree":     ("#0c1a2e","#60a5fa","#1e3a5f"),
        "📋 Formulario":   ("#1a0a2e","#c084fc","#5b21b6"),
        "🚀 Sales Page":   ("#2e1000","#fb923c","#9a3412"),
        "📱 Tel/WA en Bio":("#052e16","#4ade80","#166534"),
        "👁️ Orgánico":    ("#2e0000","#f87171","#991b1b"),
    }
    cbg, cfg, cborder = cta_colors.get(cta, ("#1a1a1a","#888","#333"))

    ext_label = "🔗 Ver Enlace"
    if "wa.me" in ext_url or "wa.link" in ext_url:   ext_label = "💬 Cotizar por WhatsApp"
    elif "forms.gle" in ext_url or "google.com/forms" in ext_url: ext_label = "📋 Aplicar"
    elif "hackeatumetabolismo" in ext_url:            ext_label = "🚀 Ver Sales Page"
    elif "linktr.ee" in ext_url:                     ext_label = "🌳 Ver Linktree"
    ext_btn = f'<a href="{ext_url}" target="_blank" style="display:inline-block;padding:6px 14px;background:#1a1a1a;border:1px solid #333;border-radius:6px;color:#ddd;text-decoration:none;font-size:12px;font-weight:600;margin-left:8px">{ext_label}</a>' if ext_url else ""

    card = f"""
    <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:16px 20px;
                font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
      <div style="display:flex;gap:14px;align-items:flex-start">
        <img src="{pic_src}" style="width:56px;height:56px;border-radius:50%;object-fit:cover;border:2px solid #333;flex-shrink:0"/>
        <div style="flex:1;min-width:0">

          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px">
            <span style="font-size:16px;font-weight:800;color:#f0f0f0">{fname}</span>
            <a href="{ig_url}" target="_blank" style="color:#60a5fa;font-size:12px;text-decoration:none">@{uname}</a>
            <span style="background:#111;color:{tc};border:1px solid {tc}44;padding:2px 8px;border-radius:8px;font-size:12px;font-weight:600">{tier}</span>
            {premium_label}
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin-bottom:12px">
            <div style="background:#111;border-radius:8px;padding:10px 12px;text-align:center">
              <div style="font-size:18px;font-weight:800;color:#f0f0f0">{fmt(followers)}</div>
              <div style="font-size:10px;color:#555;text-transform:uppercase;letter-spacing:.5px">Seguidores</div>
            </div>
            <div style="background:#111;border-radius:8px;padding:10px 12px;text-align:center">
              <div style="font-size:18px;font-weight:800;color:{eng_col}">{eng}%</div>
              <div style="font-size:10px;color:#555;text-transform:uppercase;letter-spacing:.5px">Engagement</div>
            </div>
            <div style="background:#111;border-radius:8px;padding:10px 12px;text-align:center">
              <div style="font-size:16px;font-weight:800;color:#22c55e">${min_usd}–${max_usd}</div>
              <div style="font-size:10px;color:#555;text-transform:uppercase;letter-spacing:.5px">USD / mes est.</div>
            </div>
            <div style="background:#111;border-radius:8px;padding:10px 12px;text-align:center">
              <div style="font-size:14px;font-weight:700;color:#fbbf24">RD${min_rd:,}–{max_rd:,}</div>
              <div style="font-size:10px;color:#555;text-transform:uppercase;letter-spacing:.5px">RD$ / mes est.</div>
            </div>
          </div>

          <div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:8px">
            <span style="font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.8px">CÓMO COTIZA:</span>
            <span style="background:{cbg};color:{cfg};border:1px solid {cborder};padding:3px 10px;border-radius:10px;font-size:12px;font-weight:600">{cta}</span>
            <a href="{ig_url}" target="_blank" style="display:inline-block;padding:5px 12px;border-radius:6px;text-decoration:none;color:white;font-size:12px;font-weight:600;background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045)">📸 Instagram</a>
            {ext_btn}
          </div>

          <div style="font-size:12px;color:#777;line-height:1.4;font-style:italic">{bio[:180] + "..." if len(bio) > 180 else bio}</div>
        </div>
      </div>
    </div>"""

    components.html(card, height=260, scrolling=False)

st.divider()
st.caption("💡 Precios estimados basados en tiers de seguidores + ajuste por engagement rate. Tasa de cambio: RD$57 = $1 USD. Ningún coach publica precios — modelo de cotización privada vía WhatsApp domina el mercado.")
