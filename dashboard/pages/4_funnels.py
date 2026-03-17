"""
Página 4 — Funnels de la Competencia (Top 3 Coaches RD)
Investigación real: cómo capturan leads, cómo cierran ventas, qué dicen en cada paso.
Data recolectada visitando sus páginas en vivo — hackeatumetabolismo.com/florecer, linkbio.co
"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import streamlit.components.v1 as components
from components.data_loader import load_all_images_b64, get_local_image_b64

st.set_page_config(page_title="Funnels — Gabifit", page_icon="🔬", layout="wide")

st.markdown("""
<style>
  [data-testid="stSidebar"] { background: #111 !important; }
  .block-container { padding-top: 1.5rem !important; }
  h1 { color: #ef4444 !important; }
  h2,h3 { color: #f0f0f0 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🔬 Funnels de la Competencia")
st.caption("Investigación en vivo · Top 3 coaches por seguidores · Cómo capturan y cierran clientes reales")

img_cache = load_all_images_b64()

def safe_fn(n): return re.sub(r'[^\w\-_]', '_', n)

# ── MASTER INSIGHT BANNER ──────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1a0a00,#2e1000);border:1px solid #9a3412;
            border-radius:14px;padding:20px 28px;margin-bottom:24px;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
  <div style="font-size:18px;font-weight:800;color:#fb923c;margin-bottom:10px">
    🎯 Hallazgo Principal — Investigación en Vivo
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:12px">
    <div style="background:rgba(0,0,0,.3);border-radius:10px;padding:14px;border:1px solid #333">
      <div style="color:#fbbf24;font-weight:700;font-size:13px">👑 #1 @jc_simo (368K)</div>
      <div style="color:#f0f0f0;font-size:12px;margin-top:4px;line-height:1.6">
        Único con funnel COMPLETO:<br>Sales page + VSL + precio público + Hotmart checkout
      </div>
      <div style="color:#4ade80;font-size:12px;margin-top:6px;font-weight:700">💰 $97 USD — visible en la página</div>
    </div>
    <div style="background:rgba(0,0,0,.3);border-radius:10px;padding:14px;border:1px solid #333">
      <div style="color:#94a3b8;font-weight:700;font-size:13px">🥈 #2 @davidsoto91 (301K)</div>
      <div style="color:#f0f0f0;font-size:12px;margin-top:4px;line-height:1.6">
        Sin funnel estructurado.<br>301K seguidores, email Hotmail, cero sistema de ventas.
      </div>
      <div style="color:#f87171;font-size:12px;margin-top:6px;font-weight:700">❌ Sin precio · Sin CTA · Sin landing</div>
    </div>
    <div style="background:rgba(0,0,0,.3);border-radius:10px;padding:14px;border:1px solid #333">
      <div style="color:#c2692a;font-weight:700;font-size:13px">🥉 #3 @cirujano_fitness (194K)</div>
      <div style="color:#f0f0f0;font-size:12px;margin-top:4px;line-height:1.6">
        Todo va a WhatsApp. 5 servicios en linkbio,<br>todos redirigen al mismo numero WA.
      </div>
      <div style="color:#4ade80;font-size:12px;margin-top:6px;font-weight:700">💬 +1 829-324-2214 (RD)</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# COACH #1 — JC SIMO
# ══════════════════════════════════════════════════════════════════════════════
pic1 = get_local_image_b64("data/images/profiles/jc_simo.jpg", img_cache)
pic1_src = (f"data:image/jpeg;base64,{pic1}" if pic1
            else "https://ui-avatars.com/api/?name=JC+Simo&background=222&color=fff&size=80")

st.markdown("---")
components.html(f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">

  <div style="background:linear-gradient(135deg,#1a1000,#2a1800);border:1px solid #854d0e;
              border-radius:14px;padding:20px 24px;display:flex;gap:18px;align-items:center;margin-bottom:14px">
    <img src="{pic1_src}" style="width:72px;height:72px;border-radius:50%;object-fit:cover;border:3px solid #f59e0b;flex-shrink:0"/>
    <div style="flex:1">
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <span style="font-size:20px;font-weight:800;color:#fbbf24">👑 #1 Juan Carlos Simo</span>
        <span style="background:#854d0e;color:#fbbf24;padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700">368K seguidores</span>
        <span style="background:#052e16;color:#4ade80;padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700">FUNNEL COMPLETO ✅</span>
      </div>
      <div style="color:#d97706;font-size:12px;margin-top:5px">@jc_simo · Dietética funcional · Biohacking · Salud hormonal femenina</div>
      <div style="color:#666;font-size:11px;margin-top:2px">🌐 hackeatumetabolismo.com/florecer — visitado y analizado en vivo</div>
    </div>
    <a href="https://hackeatumetabolismo.com/florecer" target="_blank"
       style="display:inline-block;padding:8px 18px;background:#b45309;border-radius:8px;
              color:#fef3c7;text-decoration:none;font-size:12px;font-weight:700;flex-shrink:0">
      🔗 Ver Sales Page
    </a>
  </div>

  <!-- FUNNEL STEPS -->
  <div style="background:#0f0f0f;border:1px solid #222;border-radius:14px;padding:18px 20px;margin-bottom:14px">
    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#555;margin-bottom:14px">
      FLUJO DEL FUNNEL — 5 PASOS
    </div>
    <div style="display:flex;align-items:stretch;gap:0;overflow-x:auto;padding-bottom:4px">

      <div style="flex:1;min-width:130px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">📱</div>
        <div style="font-size:10px;font-weight:700;color:#fbbf24;text-transform:uppercase;margin-bottom:4px">Paso 1</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">Post de IG</div>
        <div style="font-size:10px;color:#888;line-height:1.5">Contenido educativo salud hormonal. CTA: "link en bio"</div>
      </div>
      <div style="display:flex;align-items:center;padding:0 3px;color:#f59e0b;font-size:18px;flex-shrink:0">➜</div>

      <div style="flex:1;min-width:130px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">🔗</div>
        <div style="font-size:10px;font-weight:700;color:#fbbf24;text-transform:uppercase;margin-bottom:4px">Paso 2</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">Bio → Sales Page</div>
        <div style="font-size:10px;color:#888;line-height:1.5">Link directo, sin Linktree. Va directo al producto.</div>
      </div>
      <div style="display:flex;align-items:center;padding:0 3px;color:#f59e0b;font-size:18px;flex-shrink:0">➜</div>

      <div style="flex:1.4;min-width:155px;background:#1a0f00;border:2px solid #b45309;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">🚀</div>
        <div style="font-size:10px;font-weight:700;color:#fbbf24;text-transform:uppercase;margin-bottom:4px">Paso 3 ⭐ NÚCLEO</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">Sales Page VSL</div>
        <div style="font-size:10px;color:#d97706;line-height:1.6">Urgency banner · Video ventas · Pain points · $147→<strong style="color:#4ade80">$97</strong> · FAQ · 2 coaches</div>
      </div>
      <div style="display:flex;align-items:center;padding:0 3px;color:#f59e0b;font-size:18px;flex-shrink:0">➜</div>

      <div style="flex:1;min-width:130px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">💳</div>
        <div style="font-size:10px;font-weight:700;color:#fbbf24;text-transform:uppercase;margin-bottom:4px">Paso 4</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">Checkout Hotmart</div>
        <div style="font-size:10px;color:#888;line-height:1.5">Pago digital. Tarjeta/débito. Plataforma internacional.</div>
      </div>
      <div style="display:flex;align-items:center;padding:0 3px;color:#f59e0b;font-size:18px;flex-shrink:0">➜</div>

      <div style="flex:1;min-width:130px;background:#052e16;border:1px solid #166534;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">💬</div>
        <div style="font-size:10px;font-weight:700;color:#4ade80;text-transform:uppercase;margin-bottom:4px">Post-venta</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">Grupo WhatsApp</div>
        <div style="font-size:10px;color:#86efac;line-height:1.5">Incluido en compra. Comunidad + retención.</div>
      </div>

    </div>
  </div>

  <!-- DETAIL GRID -->
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:14px">
    <div style="background:#0f0f0f;border:1px solid #222;border-radius:12px;padding:14px">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;color:#f59e0b;margin-bottom:8px">🎯 TÁCTICA DE URGENCIA</div>
      <div style="font-size:11px;color:#ddd;line-height:1.8">
        ✦ Banner permanente arriba de la página<br>
        ✦ Precio tachado <span style="text-decoration:line-through;color:#888">$147</span> → <span style="color:#4ade80;font-weight:700">$97 USD</span><br>
        ✦ "OFERTA POR TIEMPO LIMITADO"<br>
        ✦ Fecha límite: 6 al 16 de marzo<br>
        ✦ CTA repetido 4 veces en la página
      </div>
    </div>
    <div style="background:#0f0f0f;border:1px solid #222;border-radius:12px;padding:14px">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;color:#f59e0b;margin-bottom:8px">💬 COPY DE VENTAS (real)</div>
      <div style="font-size:11px;color:#ddd;line-height:1.8">
        ✦ "No estás rota. Solo estás desequilibrada."<br>
        ✦ "No es la edad. No eres tú."<br>
        ✦ "Deja de usar parches para sobrevivir"<br>
        ✦ "Años de práctica clínica en una sesión"<br>
        ✦ "¿Te sientes atrapada en un cuerpo que no reconoces?"
      </div>
    </div>
    <div style="background:#0f0f0f;border:1px solid #222;border-radius:12px;padding:14px">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;color:#f59e0b;margin-bottom:8px">📦 QUÉ INCLUYE</div>
      <div style="font-size:11px;color:#ddd;line-height:1.8">
        ✦ Masterclass VIDEO vía Hotmart (1 año acceso)<br>
        ✦ Protocolo completo SOP<br>
        ✦ Protocolo Endometriosis<br>
        ✦ Anti-aging hormonal femenino<br>
        ✦ Guía suplementación estratégica<br>
        ✦ Grupo exclusivo WhatsApp
      </div>
    </div>
  </div>

  <div style="background:#0a1a0a;border:1px solid #166534;border-radius:12px;padding:14px 18px;display:flex;gap:20px;align-items:center">
    <div style="text-align:center;flex-shrink:0">
      <div style="font-size:34px;font-weight:900;color:#4ade80">9/10</div>
      <div style="font-size:9px;color:#555;text-transform:uppercase;letter-spacing:1px">Funnel Score</div>
    </div>
    <div style="flex:1">
      <div style="font-size:11px;font-weight:700;color:#4ade80;margin-bottom:5px">✅ Fortalezas</div>
      <div style="font-size:11px;color:#86efac;line-height:1.7">
        Precio visible · VSL profesional · Urgencia con fecha real · Hotmart checkout integrado ·
        WhatsApp post-venta · 2 instructores = credibilidad · FAQ elimina objeciones · Facebook Pixel (retargeting) · Copywriting emocional muy trabajado
      </div>
    </div>
    <div style="flex:1">
      <div style="font-size:11px;font-weight:700;color:#f87171;margin-bottom:5px">❌ Lo que le falta</div>
      <div style="font-size:11px;color:#fca5a5;line-height:1.7">
        Sin testimonios visibles · Sin garantía de devolución · Solo un producto (sin upsell visible)
      </div>
    </div>
  </div>

</div>
""", height=700, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
# COACH #2 — DAVID SOTO
# ══════════════════════════════════════════════════════════════════════════════
pic2 = get_local_image_b64("data/images/profiles/davidsoto91.jpg", img_cache)
pic2_src = (f"data:image/jpeg;base64,{pic2}" if pic2
            else "https://ui-avatars.com/api/?name=David+Soto&background=222&color=fff&size=80")

st.markdown("---")
components.html(f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">

  <div style="background:linear-gradient(135deg,#0f1520,#1a2035);border:1px solid #334155;
              border-radius:14px;padding:20px 24px;display:flex;gap:18px;align-items:center;margin-bottom:14px">
    <img src="{pic2_src}" style="width:72px;height:72px;border-radius:50%;object-fit:cover;border:3px solid #64748b;flex-shrink:0"/>
    <div style="flex:1">
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <span style="font-size:20px;font-weight:800;color:#94a3b8">🥈 #2 David Soto</span>
        <span style="background:#1e293b;color:#94a3b8;padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700">301K seguidores</span>
        <span style="background:#2e0000;color:#f87171;padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700">SIN FUNNEL ❌</span>
      </div>
      <div style="color:#64748b;font-size:12px;margin-top:5px">@davidsoto91 · Entrenador personal · Asesoramiento online/presencial · Málaga/Madrid</div>
      <div style="color:#666;font-size:11px;margin-top:2px">📧 david-soto-9@hotmail.com — sin URL en bio · investigado en vivo</div>
    </div>
    <a href="https://instagram.com/davidsoto91" target="_blank"
       style="display:inline-block;padding:8px 18px;background:#1e293b;border-radius:8px;
              color:#94a3b8;text-decoration:none;font-size:12px;font-weight:700;flex-shrink:0;border:1px solid #334155">
      📸 Ver Perfil
    </a>
  </div>

  <div style="background:#0f0f0f;border:1px solid #222;border-radius:14px;padding:18px 20px;margin-bottom:14px">
    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#555;margin-bottom:14px">
      FLUJO DEL "FUNNEL" — MINIMO VIABLE (investigado en vivo)
    </div>
    <div style="display:flex;align-items:stretch;gap:0">

      <div style="flex:1;min-width:140px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">📱</div>
        <div style="font-size:10px;font-weight:700;color:#94a3b8;text-transform:uppercase;margin-bottom:4px">Paso 1</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">Posts de IG</div>
        <div style="font-size:10px;color:#888;line-height:1.5">Contenido fitness y transformaciones. Sin CTA claro en captions.</div>
      </div>
      <div style="display:flex;align-items:center;padding:0 3px;color:#475569;font-size:18px;flex-shrink:0">➜</div>

      <div style="flex:1;min-width:140px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">👤</div>
        <div style="font-size:10px;font-weight:700;color:#94a3b8;text-transform:uppercase;margin-bottom:4px">Paso 2</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">Visita el Perfil</div>
        <div style="font-size:10px;color:#888;line-height:1.5">Bio: "Asesoramiento Online/Presencial". Sin link de venta ni precio.</div>
      </div>
      <div style="display:flex;align-items:center;padding:0 3px;color:#475569;font-size:18px;flex-shrink:0">➜</div>

      <div style="flex:1.4;min-width:155px;background:#2e0000;border:2px solid #7f1d1d;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">🚧</div>
        <div style="font-size:10px;font-weight:700;color:#f87171;text-transform:uppercase;margin-bottom:4px">Cuello de Botella</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">Email Hotmail / DM</div>
        <div style="font-size:10px;color:#fca5a5;line-height:1.5">El prospecto debe escribir a Hotmail o DM. Altisima friccion. Muchos abandonan.</div>
      </div>
      <div style="display:flex;align-items:center;padding:0 3px;color:#475569;font-size:18px;flex-shrink:0">➜</div>

      <div style="flex:1;min-width:140px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">🤝</div>
        <div style="font-size:10px;font-weight:700;color:#94a3b8;text-transform:uppercase;margin-bottom:4px">Cierre</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">Conversacion 1:1</div>
        <div style="font-size:10px;color:#888;line-height:1.5">Precio y servicios negociados en privado. Sin estructura.</div>
      </div>

    </div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px">
    <div style="background:#0f0f0f;border:1px solid #222;border-radius:12px;padding:14px">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;color:#94a3b8;margin-bottom:8px">🔍 SITUACION ACTUAL</div>
      <div style="font-size:11px;color:#ddd;line-height:1.8">
        ✦ 301K seguidores pero <strong style="color:#f87171">sin sistema de ventas</strong><br>
        ✦ Email de contacto es Hotmail (nada profesional)<br>
        ✦ Basado en España — mercado diferente a RD<br>
        ✦ Alcance viene del contenido, no de un funnel<br>
        ✦ Probablemente entrena clientes en Madrid presencialmente
      </div>
    </div>
    <div style="background:#0f0f0f;border:1px solid #222;border-radius:12px;padding:14px">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;color:#4ade80;margin-bottom:8px">💡 OPORTUNIDAD GABIFIT</div>
      <div style="font-size:11px;color:#ddd;line-height:1.8">
        ✦ 301K seguidores sin funnel = <strong style="color:#4ade80">audiencia desatendida en RD</strong><br>
        ✦ Un WhatsApp CTA ya supera su conversion actual<br>
        ✦ Mercado dominicano no lo tiene presente<br>
        ✦ Gabifit puede capturar su audiencia latina con funnel local<br>
        ✦ Cualquier landing basica supera su situacion
      </div>
    </div>
  </div>

  <div style="background:#1a0a0a;border:1px solid #7f1d1d;border-radius:12px;padding:14px 18px;display:flex;gap:20px;align-items:center">
    <div style="text-align:center;flex-shrink:0">
      <div style="font-size:34px;font-weight:900;color:#f87171">2/10</div>
      <div style="font-size:9px;color:#555;text-transform:uppercase;letter-spacing:1px">Funnel Score</div>
    </div>
    <div style="font-size:11px;color:#fca5a5;line-height:1.8;flex:1">
      A pesar de 301K seguidores, no tiene ningun sistema de ventas estructurado.
      Todo el trafico de Instagram termina en un perfil con email Hotmail.
      Sin precio visible, sin landing page, sin CTA accionable, sin automatizacion.
      El talento esta — el sistema de ventas, completamente ausente.
    </div>
  </div>

</div>
""", height=580, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
# COACH #3 — CIRUJANO FITNESS
# ══════════════════════════════════════════════════════════════════════════════
pic3 = get_local_image_b64("data/images/profiles/cirujano_fitness.jpg", img_cache)
pic3_src = (f"data:image/jpeg;base64,{pic3}" if pic3
            else "https://ui-avatars.com/api/?name=Cirujano+Fitness&background=222&color=fff&size=80")

st.markdown("---")
components.html(f"""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">

  <div style="background:linear-gradient(135deg,#0a1a00,#0f2a00);border:1px solid #166534;
              border-radius:14px;padding:20px 24px;display:flex;gap:18px;align-items:center;margin-bottom:14px">
    <img src="{pic3_src}" style="width:72px;height:72px;border-radius:50%;object-fit:cover;border:3px solid #22c55e;flex-shrink:0"/>
    <div style="flex:1">
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <span style="font-size:20px;font-weight:800;color:#c2692a">🥉 #3 Cirujano Fitness</span>
        <span style="background:#14532d;color:#4ade80;padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700">194K seguidores</span>
        <span style="background:#052e16;color:#4ade80;padding:3px 12px;border-radius:20px;font-size:11px;font-weight:700">100% WHATSAPP 💬</span>
      </div>
      <div style="color:#86efac;font-size:12px;margin-top:5px">@cirujano_fitness · Master Coach Internacional · Online + Presencial · Rep. Dominicana</div>
      <div style="color:#666;font-size:11px;margin-top:2px">🔗 linkbio.co/5090719hUHDtE — todas las opciones van a WA: +1 829-324-2214</div>
    </div>
    <a href="https://linkbio.co/5090719hUHDtE" target="_blank"
       style="display:inline-block;padding:8px 18px;background:#14532d;border-radius:8px;
              color:#4ade80;text-decoration:none;font-size:12px;font-weight:700;flex-shrink:0;border:1px solid #166534">
      🔗 Ver Linkbio
    </a>
  </div>

  <div style="background:#0f0f0f;border:1px solid #222;border-radius:14px;padding:18px 20px;margin-bottom:14px">
    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#555;margin-bottom:14px">
      FLUJO DEL FUNNEL — TODO VA A WHATSAPP
    </div>
    <div style="display:flex;align-items:stretch;gap:0">

      <div style="flex:1;min-width:120px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">📱</div>
        <div style="font-size:10px;font-weight:700;color:#4ade80;text-transform:uppercase;margin-bottom:4px">Paso 1</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">Posts de IG</div>
        <div style="font-size:10px;color:#888;line-height:1.5">Contenido fitness, logros, campeonatos. CTA: "info en bio"</div>
      </div>
      <div style="display:flex;align-items:center;padding:0 3px;color:#22c55e;font-size:18px;flex-shrink:0">➜</div>

      <div style="flex:1;min-width:120px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">🔗</div>
        <div style="font-size:10px;font-weight:700;color:#4ade80;text-transform:uppercase;margin-bottom:4px">Paso 2</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">Linkbio</div>
        <div style="font-size:10px;color:#888;line-height:1.5">Pagina con 5 categorias de servicios.</div>
      </div>
      <div style="display:flex;align-items:center;padding:0 3px;color:#22c55e;font-size:18px;flex-shrink:0">➜</div>

      <div style="flex:1.6;min-width:160px;background:#052e16;border:2px solid #166534;border-radius:10px;padding:12px 12px">
        <div style="font-size:10px;font-weight:700;color:#4ade80;text-transform:uppercase;margin-bottom:8px;text-align:center">5 OPCIONES — TODAS → WA</div>
        <div style="font-size:10px;color:#86efac;line-height:1.9">
          📍 Planes Presenciales → WA<br>
          📲 Planes en Linea → WA<br>
          🏋️ Miercoles Cross Training → WA<br>
          👥 Team Cirujano → WA<br>
          🏆 Marca para Campeones → WA
        </div>
      </div>
      <div style="display:flex;align-items:center;padding:0 3px;color:#22c55e;font-size:18px;flex-shrink:0">➜</div>

      <div style="flex:1;min-width:120px;background:#052e16;border:2px solid #166534;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">💬</div>
        <div style="font-size:10px;font-weight:700;color:#4ade80;text-transform:uppercase;margin-bottom:4px">Paso 3 ⭐</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">WhatsApp</div>
        <div style="font-size:10px;color:#86efac;line-height:1.5">+1 829-324-2214 (RD). Cierra 1:1 en chat.</div>
      </div>
      <div style="display:flex;align-items:center;padding:0 3px;color:#22c55e;font-size:18px;flex-shrink:0">➜</div>

      <div style="flex:1;min-width:110px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;padding:12px 10px;text-align:center">
        <div style="font-size:20px;margin-bottom:6px">🤝</div>
        <div style="font-size:10px;font-weight:700;color:#4ade80;text-transform:uppercase;margin-bottom:4px">Cierre</div>
        <div style="font-size:12px;font-weight:600;color:#f0f0f0;margin-bottom:5px">Venta 1:1</div>
        <div style="font-size:10px;color:#888;line-height:1.5">Precio acordado en conversacion privada de WA.</div>
      </div>

    </div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:14px">
    <div style="background:#0f0f0f;border:1px solid #222;border-radius:12px;padding:14px">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;color:#4ade80;margin-bottom:8px">✅ LO QUE HACE BIEN</div>
      <div style="font-size:11px;color:#ddd;line-height:1.8">
        ✦ Linkbio organizado con 5 categorias<br>
        ✦ Formulario de contacto integrado<br>
        ✦ Gimnasio fisico propio (@cirujano_fitnessgym)<br>
        ✦ Multiples lineas de negocio<br>
        ✦ Numero RD activo y verificado
      </div>
    </div>
    <div style="background:#0f0f0f;border:1px solid #222;border-radius:12px;padding:14px">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;color:#f87171;margin-bottom:8px">❌ DEBILIDADES</div>
      <div style="font-size:11px;color:#ddd;line-height:1.8">
        ✦ Sin precio visible en ningun lado<br>
        ✦ Sin testimonios o resultados publicados<br>
        ✦ Sin landing page propia<br>
        ✦ Escala limitada por capacidad en WA<br>
        ✦ Sin sistema automatizado de respuesta
      </div>
    </div>
    <div style="background:#0f0f0f;border:1px solid #222;border-radius:12px;padding:14px">
      <div style="font-size:10px;font-weight:700;text-transform:uppercase;color:#60a5fa;margin-bottom:8px">💡 OPORTUNIDAD GABIFIT</div>
      <div style="font-size:11px;color:#ddd;line-height:1.8">
        ✦ En RD WhatsApp es el canal correcto — igualar<br>
        ✦ Diferenciarse con precio transparente<br>
        ✦ Resultados visibles = ventaja directa<br>
        ✦ Una landing page ya supera su funnel<br>
        ✦ Respuesta rapida = ventaja competitiva
      </div>
    </div>
  </div>

  <div style="background:#0a1a0a;border:1px solid #166534;border-radius:12px;padding:14px 18px;display:flex;gap:20px;align-items:center">
    <div style="text-align:center;flex-shrink:0">
      <div style="font-size:34px;font-weight:900;color:#4ade80">5/10</div>
      <div style="font-size:9px;color:#555;text-transform:uppercase;letter-spacing:1px">Funnel Score</div>
    </div>
    <div style="font-size:11px;color:#86efac;line-height:1.8;flex:1">
      Tiene un sistema claro (Linkbio → WhatsApp) y varias lineas de negocio. Pero todo termina en una
      conversacion privada sin estructura ni precio. Sin automatizacion, sin seguimiento, sin escala.
      El gimnasio fisico y el numero RD son sus diferenciadores reales.
    </div>
  </div>

</div>
""", height=650, scrolling=False)


# ══════════════════════════════════════════════════════════════════════════════
# TABLA COMPARATIVA + PLAN DE ACCION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.subheader("📊 Comparativa Final + Plan de Accion para Gabifit")

components.html("""
<div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">

  <div style="background:#0f0f0f;border:1px solid #222;border-radius:14px;padding:18px 22px;margin-bottom:14px">
    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#555;margin-bottom:14px">TABLA COMPARATIVA — FUNNELS TOP 3</div>
    <table style="width:100%;border-collapse:collapse;font-size:12px">
      <thead>
        <tr style="border-bottom:1px solid #2a2a2a">
          <th style="text-align:left;padding:8px 12px;color:#666;font-weight:600;width:30%">Elemento del Funnel</th>
          <th style="text-align:center;padding:8px 12px;color:#fbbf24">👑 @jc_simo</th>
          <th style="text-align:center;padding:8px 12px;color:#94a3b8">🥈 @davidsoto91</th>
          <th style="text-align:center;padding:8px 12px;color:#4ade80">🥉 @cirujano_fitness</th>
        </tr>
      </thead>
      <tbody>
        <tr style="border-bottom:1px solid #1a1a1a"><td style="padding:8px 12px;color:#bbb">Sales Page propia</td><td style="text-align:center;padding:8px;color:#4ade80">✅ Completa + VSL</td><td style="text-align:center;padding:8px;color:#f87171">❌ No</td><td style="text-align:center;padding:8px;color:#f87171">❌ No</td></tr>
        <tr style="border-bottom:1px solid #1a1a1a"><td style="padding:8px 12px;color:#bbb">Precio visible</td><td style="text-align:center;padding:8px;color:#4ade80">✅ $97 USD</td><td style="text-align:center;padding:8px;color:#f87171">❌ No</td><td style="text-align:center;padding:8px;color:#f87171">❌ No</td></tr>
        <tr style="border-bottom:1px solid #1a1a1a"><td style="padding:8px 12px;color:#bbb">Link en bio activo</td><td style="text-align:center;padding:8px;color:#4ade80">✅ Directo</td><td style="text-align:center;padding:8px;color:#f87171">❌ Sin link</td><td style="text-align:center;padding:8px;color:#4ade80">✅ Linkbio</td></tr>
        <tr style="border-bottom:1px solid #1a1a1a"><td style="padding:8px 12px;color:#bbb">Canal de cierre</td><td style="text-align:center;padding:8px;color:#60a5fa">💳 Hotmart</td><td style="text-align:center;padding:8px;color:#888">📧 Email/DM</td><td style="text-align:center;padding:8px;color:#4ade80">💬 WhatsApp</td></tr>
        <tr style="border-bottom:1px solid #1a1a1a"><td style="padding:8px 12px;color:#bbb">Urgencia / Scarcity</td><td style="text-align:center;padding:8px;color:#4ade80">✅ Precio + fecha limite</td><td style="text-align:center;padding:8px;color:#f87171">❌ No</td><td style="text-align:center;padding:8px;color:#f87171">❌ No</td></tr>
        <tr style="border-bottom:1px solid #1a1a1a"><td style="padding:8px 12px;color:#bbb">Post-venta / retención</td><td style="text-align:center;padding:8px;color:#4ade80">✅ Grupo WhatsApp</td><td style="text-align:center;padding:8px;color:#f87171">❌ No</td><td style="text-align:center;padding:8px;color:#888">🏋️ Gimnasio</td></tr>
        <tr style="border-bottom:1px solid #1a1a1a"><td style="padding:8px 12px;color:#bbb">Facebook Pixel / Retargeting</td><td style="text-align:center;padding:8px;color:#4ade80">✅ Instalado</td><td style="text-align:center;padding:8px;color:#f87171">❌ No</td><td style="text-align:center;padding:8px;color:#f87171">❌ No</td></tr>
        <tr><td style="padding:10px 12px;color:#f0f0f0;font-weight:700">FUNNEL SCORE</td><td style="text-align:center;padding:10px;color:#4ade80;font-weight:800;font-size:18px">9/10</td><td style="text-align:center;padding:10px;color:#f87171;font-weight:800;font-size:18px">2/10</td><td style="text-align:center;padding:10px;color:#fbbf24;font-weight:800;font-size:18px">5/10</td></tr>
      </tbody>
    </table>
  </div>

  <!-- ACTION PLAN -->
  <div style="background:linear-gradient(135deg,#0c1a0c,#0a1a0a);border:2px solid #166534;border-radius:14px;padding:20px 24px">
    <div style="font-size:15px;font-weight:800;color:#4ade80;margin-bottom:14px">
      🚀 Plan de Accion para Gabifit — Basado en Investigacion Real
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <div>
        <div style="font-size:11px;font-weight:700;color:#86efac;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px">HACER YA (Semana 1)</div>
        <div style="font-size:11px;color:#d1fae5;line-height:2.0">
          ✦ Activar WhatsApp como canal de cierre (estandar en RD)<br>
          ✦ Link directo en bio a pagina de servicios o WA<br>
          ✦ Publicar precios — ningun competidor lo hace = ventaja unica<br>
          ✦ Crear Linkbio con categorias de servicios claras
        </div>
      </div>
      <div>
        <div style="font-size:11px;font-weight:700;color:#86efac;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px">DIFERENCIADORES vs COMPETENCIA</div>
        <div style="font-size:11px;color:#d1fae5;line-height:2.0">
          ✦ Unico en mostrar precio = elimina friccion del "cuanto cobras"<br>
          ✦ Resultados de clientes visibles = ninguno los muestra bien<br>
          ✦ Respuesta rapida en WA = ventaja sobre cirujano_fitness<br>
          ✦ VSL simple (video de presentacion) = nivel de @jc_simo pero local
        </div>
      </div>
    </div>
  </div>

</div>
""", height=640, scrolling=False)

st.divider()
st.caption("🔬 Investigacion realizada en vivo — hackeatumetabolismo.com/florecer · linkbio.co/5090719hUHDtE · instagram.com/davidsoto91 · Datos recolectados Marzo 2026")
