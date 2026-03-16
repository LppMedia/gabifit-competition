"""
Page 3: Services & Offers
Built from raw Instagram profile data — real bios, real posts, real coaches.
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

st.set_page_config(page_title="Servicios — Gabifit", page_icon="🛎️", layout="wide")

st.title("🛎️ Servicios de la Competencia")
st.caption("Qué ofrecen los coaches de fitness RD — datos reales de Instagram")

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

# ── Service detection from bio + captions ─────────────────────────────────────
SERVICE_KEYWORDS = {
    "🌐 Online":         ["online", "virtual", "remoto", "distancia", "zoom", "whatsapp"],
    "🏋️ Presencial":     ["presencial", "gym", "gimnasio", "studio", "estudio", "pesas"],
    "🥗 Nutrición":      ["nutrici", "alimentaci", "dieta", "plan alimenticio", "nutri", "macros"],
    "🔥 Transformación": ["transform", "cambio", "bajar de peso", "pérdida", "perder peso", "definici"],
    "💪 Hipertrofia":    ["musculo", "fuerza", "hipertrofia", "volumen", "masa", "ganar músculo"],
    "📊 Evaluación":     ["evaluaci", "assess", "diagnos", "medici", "análisis corporal"],
    "👥 Grupos":         ["grupo", "clase", "boot camp", "bootcamp", "clase grupal"],
    "💊 Suplementos":    ["suplemento", "proteína", "creatina", "supplement"],
}

CTA_KEYWORDS = {
    "💬 WhatsApp":         lambda u, b: "wa.me" in u or "wa.link" in u or "wasap" in b or "whatsapp" in b,
    "🔗 Linktree":         lambda u, b: "linktr.ee" in u or "linkbio" in u,
    "📋 Formulario":       lambda u, b: "forms.gle" in u or "google.com/forms" in u,
    "🚀 Página de Ventas": lambda u, b: "hackeatumetabolismo" in u or "florecer" in u or "canva.site" in u or "rebrand.ly" in u,
    "📱 Tel en Bio":       lambda u, b: bool(re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', b or "")),
}

def get_services(bio, captions):
    text = ((bio or "") + " " + (captions or "")).lower()
    return [label for label, kws in SERVICE_KEYWORDS.items() if any(k in text for k in kws)]

def get_cta(ext_url, bio):
    u, b = (ext_url or "").lower(), (bio or "").lower()
    for label, fn in CTA_KEYWORDS.items():
        if fn(u, b):
            return label
    return "👁️ Solo Orgánico"

def fmt(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

def safe_fn(name):
    return re.sub(r'[^\w\-_]', '_', name)

# Build enriched coach list
coaches = []
for p in profiles_sorted:
    uname     = p.get("username", "")
    fname     = p.get("fullName", uname)
    bio       = p.get("biography", "") or ""
    followers = p.get("followersCount", 0)
    ext_url   = p.get("externalUrl", "") or ""
    user_posts = posts_by_user.get(uname, [])
    all_caps  = " ".join([(x.get("caption") or "") for x in user_posts])

    services  = get_services(bio, all_caps)
    cta       = get_cta(ext_url, bio)
    phones    = re.findall(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', bio)

    avg_likes = round(sum(x.get("likesCount",0) for x in user_posts) / len(user_posts)) if user_posts else 0
    eng_rate  = 0.0
    if followers and user_posts:
        tl = sum(x.get("likesCount",0) for x in user_posts)
        tc = sum(x.get("commentsCount",0) for x in user_posts)
        eng_rate = round((tl + tc) / len(user_posts) / followers * 100, 2)

    coaches.append({
        "username": uname, "fullName": fname, "bio": bio,
        "followers": followers, "ext_url": ext_url,
        "services": services, "cta": cta, "phones": phones,
        "avg_likes": avg_likes, "eng_rate": eng_rate,
        "posts": user_posts,
    })

# ── Sidebar filter ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filtros")
    all_services = sorted({s for c in coaches for s in c["services"]})
    sel_services = st.multiselect("Servicios", all_services, default=[])
    sel_cta = st.selectbox("CTA / Cierre", ["Todos"] + sorted({c["cta"] for c in coaches}))
    min_followers = st.slider("Mínimo seguidores", 0, 400000, 0, step=1000)

filtered = [c for c in coaches
    if c["followers"] >= min_followers
    and (not sel_services or any(s in c["services"] for s in sel_services))
    and (sel_cta == "Todos" or c["cta"] == sel_cta)
]

# ── Overview metrics ───────────────────────────────────────────────────────────
service_counts = {s: sum(1 for c in coaches if s in c["services"]) for s in SERVICE_KEYWORDS}
cta_counts     = defaultdict(int)
for c in coaches:
    cta_counts[c["cta"]] += 1

cols = st.columns(4)
for i, (svc, cnt) in enumerate(sorted(service_counts.items(), key=lambda x: -x[1])[:4]):
    cols[i].metric(svc, f"{cnt}/{len(coaches)}", f"{cnt/len(coaches)*100:.0f}%")

st.divider()

# ── Charts row ─────────────────────────────────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("Servicios más ofrecidos")
    svc_df_data = sorted(service_counts.items(), key=lambda x: -x[1])
    fig = px.bar(
        x=[v for _, v in svc_df_data],
        y=[k for k, _ in svc_df_data],
        orientation="h",
        color=[v for _, v in svc_df_data],
        color_continuous_scale="Reds",
        labels={"x": "Coaches", "y": ""},
        template="plotly_dark",
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False,
                      margin=dict(l=20, r=20, t=20, b=20), height=320)
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    st.subheader("Cómo cierran clientes")
    cta_items = sorted(cta_counts.items(), key=lambda x: -x[1])
    fig2 = px.pie(
        names=[k for k, _ in cta_items],
        values=[v for _, v in cta_items],
        hole=0.4,
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Reds_r,
    )
    fig2.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=320)
    st.plotly_chart(fig2, use_container_width=True)

# ── Heatmap coaches x services ─────────────────────────────────────────────────
st.subheader("Qué ofrece cada coach")
svc_labels = list(SERVICE_KEYWORDS.keys())
coach_names = [c["fullName"] for c in filtered]
matrix = [[1 if s in c["services"] else 0 for s in svc_labels] for c in filtered]

if filtered:
    fig3 = go.Figure(go.Heatmap(
        z=matrix,
        x=svc_labels,
        y=coach_names,
        colorscale=[[0, "#1a1a1a"], [1, "#ef4444"]],
        showscale=False,
        xgap=2, ygap=2,
    ))
    fig3.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, t=20, b=20),
        height=max(300, len(filtered) * 28),
        xaxis=dict(tickangle=-30),
    )
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── Coach cards with services ──────────────────────────────────────────────────
st.subheader(f"Detalle por coach ({len(filtered)} coaches)")

for coach in filtered:
    uname    = coach["username"]
    fname    = coach["fullName"]
    bio      = coach["bio"]
    followers= coach["followers"]
    services = coach["services"]
    cta      = coach["cta"]
    ext_url  = coach["ext_url"]
    phones   = coach["phones"]
    eng      = coach["eng_rate"]
    avg_likes= coach["avg_likes"]

    pic_b64  = get_local_image_b64(f"data/images/profiles/{safe_fn(uname)}.jpg", img_cache)
    pic_src  = f"data:image/jpeg;base64,{pic_b64}" if pic_b64 else \
               f"https://ui-avatars.com/api/?name={fname.replace(' ','+')}&background=222&color=fff&size=80"

    ig_url   = f"https://instagram.com/{uname}"
    eng_col  = "#22c55e" if eng > 3 else ("#f97316" if eng > 1 else "#888")

    svc_html = "".join([
        f'<span style="background:#0a1a0a;color:#86efac;border:1px solid #166534;'
        f'padding:3px 10px;border-radius:10px;font-size:12px;margin:2px 3px 2px 0;display:inline-block">{s}</span>'
        for s in (services or ["📋 General"])
    ])

    cta_colors = {
        "💬 WhatsApp":         ("#052e16", "#4ade80", "#166534"),
        "🔗 Linktree":         ("#0c1a2e", "#60a5fa", "#1e3a5f"),
        "📋 Formulario":       ("#1a0a2e", "#c084fc", "#5b21b6"),
        "🚀 Página de Ventas": ("#2e1000", "#fb923c", "#9a3412"),
        "📱 Tel en Bio":       ("#052e16", "#4ade80", "#166534"),
        "👁️ Solo Orgánico":    ("#2e0000", "#f87171", "#991b1b"),
    }
    cbg, cfg, cborder = cta_colors.get(cta, ("#1a1a1a","#888","#333"))

    phone_html = f'<span style="color:#4ade80;font-size:12px;margin-left:8px">📞 {phones[0]}</span>' if phones else ""

    ext_label = "🔗 Link"
    if "wa.me" in ext_url or "wa.link" in ext_url:  ext_label = "💬 WhatsApp"
    elif "forms.gle" in ext_url or "google.com/forms" in ext_url: ext_label = "📋 Formulario"
    elif "linktr.ee" in ext_url: ext_label = "🌳 Linktree"
    elif "hackeatumetabolismo" in ext_url: ext_label = "🚀 Sales Page"
    ext_btn = f'<a href="{ext_url}" target="_blank" style="display:inline-block;padding:5px 12px;background:#1a1a1a;border:1px solid #333;border-radius:6px;color:#ddd;text-decoration:none;font-size:12px;font-weight:600;margin-left:8px">{ext_label}</a>' if ext_url else ""

    card = f"""
    <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:16px 20px;
                font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin-bottom:2px">
      <div style="display:flex;gap:14px;align-items:flex-start">
        <img src="{pic_src}" style="width:56px;height:56px;border-radius:50%;object-fit:cover;border:2px solid #333;flex-shrink:0"/>
        <div style="flex:1;min-width:0">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
            <span style="font-size:16px;font-weight:800;color:#f0f0f0">{fname}</span>
            <a href="{ig_url}" target="_blank" style="color:#60a5fa;font-size:12px;text-decoration:none">@{uname}</a>
            <span style="color:#888;font-size:12px">{fmt(followers)} seg</span>
            <span style="color:{eng_col};font-size:12px;font-weight:600">{eng}% eng</span>
            <span style="color:#aaa;font-size:12px">❤️ {avg_likes} avg</span>
          </div>

          <div style="margin:8px 0 4px">
            <span style="background:{cbg};color:{cfg};border:1px solid {cborder};
                         padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600">{cta}</span>
            {phone_html}
            <a href="{ig_url}" target="_blank" style="display:inline-block;padding:4px 12px;border-radius:6px;text-decoration:none;
               color:white;font-size:12px;font-weight:600;background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045);margin-left:8px">📸 IG</a>
            {ext_btn}
          </div>

          <div style="margin-bottom:8px">
            <span style="font-size:10px;color:#555;text-transform:uppercase;letter-spacing:1px;margin-right:6px">SERVICIOS</span>
            {svc_html}
          </div>

          <div style="font-size:12px;color:#999;line-height:1.5">{bio[:200] + "..." if len(bio) > 200 else bio}</div>
        </div>
      </div>
    </div>"""

    components.html(card, height=200, scrolling=False)

st.divider()
st.caption(f"📊 {len(filtered)} coaches · {len(posts)} posts analizados · Datos de Instagram via Apify")
