from fpdf import FPDF
from datetime import date
import os

def s(text):
    return (text
        .replace('\u2013', '-').replace('\u2014', '-')
        .replace('\u00b7', '*').replace('\u00e9', 'e')
        .replace('\u00f3', 'o').replace('\u00fa', 'u')
        .replace('\u00ed', 'i').replace('\u00e1', 'a')
        .replace('\u00f1', 'n').replace('\u00fc', 'u')
        .replace('\u00c9', 'E').replace('\u00d3', 'O')
        .replace('\u00da', 'U').replace('\u00cd', 'I')
        .replace('\u00c1', 'A').replace('\u00d1', 'N')
        .replace('\u00f6', 'o').replace('\u00e4', 'a')
    )

class ZapReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(30, 80, 160)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "Informe de Seguridad - OWASP ZAP", fill=True,
                  new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, s(
            f"Dashboard ETalent - ESPOCH | Version 1 Post-Remediacion | "
            f"Generado: {date.today().strftime('%d/%m/%Y')} | Pag. {self.page_no()}"
        ), align="C")

pdf = ZapReport()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Helvetica", size=10)

# ── Banner de versión ────────────────────────────────────────────────────────
pdf.set_fill_color(220, 240, 220)
pdf.set_text_color(20, 100, 20)
pdf.set_font("Helvetica", "B", 10)
pdf.cell(0, 9,
    s("  Version 1 Post-Remediacion | Proxy: Caddy :8082 con cabeceras de seguridad completas"),
    fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(4)

# ── Meta ─────────────────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, s("Informacion del Escaneo"), new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=10)
meta = [
    ("Objetivo",        "http://localhost:8082 (via Caddy reverse proxy)"),
    ("Herramienta",     "OWASP ZAP 2.16.1"),
    ("Tipo de escaneo", "Quick Scan (Spider + Active Scan)"),
    ("Fecha",           date.today().strftime("%d/%m/%Y")),
    ("Proyecto",        "Dashboard ETalent - ESPOCH"),
    ("Responsable",     "Jefferson Jordan"),
    ("Version",         "v1 - Post-Remediacion (escaneo real)"),
]
for k, v in meta:
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 7, f"{k}:", border=0)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 7, v, new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

# ── Comparativo v1 inicial vs v1 post-remediacion ────────────────────────────
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, s("Comparativo: Escaneo Inicial vs Post-Remediacion"), new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "B", 9)
pdf.set_fill_color(60, 60, 60)
pdf.set_text_color(255, 255, 255)
col = (pdf.w - pdf.l_margin - pdf.r_margin) / 3
pdf.cell(col, 7, "Nivel", fill=True, border=1)
pdf.cell(col, 7, "Escaneo Inicial", fill=True, border=1, align="C")
pdf.cell(col, 7, "Post-Remediacion", fill=True, border=1, align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
comparativo = [
    ("Alto",        "0", "0", (240,240,240)),
    ("Medio",       "1", "3*", (255,245,220)),
    ("Bajo",        "3", "1**", (240,240,240)),
    ("Informativo", "2", "2",  (240,240,240)),
]
for nivel, antes, despues, color in comparativo:
    pdf.set_fill_color(*color)
    pdf.set_font("Helvetica", size=9)
    pdf.cell(col, 6, f"  {nivel}", fill=True, border=1)
    pdf.cell(col, 6, antes, fill=True, border=1, align="C")
    pdf.cell(col, 6, despues, fill=True, border=1, align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "I", 8)
pdf.set_text_color(80, 80, 80)
pdf.multi_cell(0, 5, s(
    "* 3 alertas Medio inherentes al framework React/Streamlit (unsafe-eval, unsafe-inline): "
    "no son configuracion del servidor sino requisitos de React. No estaban en el escaneo "
    "inicial porque no habia proxy activo. Riesgo aceptado.\n"
    "** 1 alerta Bajo: marca de tiempo en codigo JS compilado de Streamlit (falso positivo). "
    "No es una cabecera HTTP expuesta."
))
pdf.set_text_color(0, 0, 0)
pdf.ln(4)

# ── Alertas resueltas ────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "Alertas Resueltas (4/4 de la configuracion del servidor)", new_x="LMARGIN", new_y="NEXT")

resueltas = [
    {
        "id": "10038", "nivel": "MEDIO",
        "nombre": "Cabecera Content-Security-Policy ausente",
        "fix": "Inyectada via Caddy header_down + header. CSP completo con base-uri, form-action, object-src.",
        "artefacto": "deploy/Caddyfile | deploy/nginx.conf",
    },
    {
        "id": "10021", "nivel": "BAJO",
        "nombre": "Falta encabezado X-Content-Type-Options",
        "fix": "Agregado: X-Content-Type-Options: nosniff",
        "artefacto": "deploy/Caddyfile | deploy/nginx.conf",
    },
    {
        "id": "10036", "nivel": "BAJO",
        "nombre": s("Filtracion de version en cabecera 'Server'"),
        "fix": "Cabecera Server reemplazada por 'ETalent-Dashboard'. Version de Python/Tornado suprimida.",
        "artefacto": "deploy/Caddyfile | deploy/nginx.conf",
    },
    {
        "id": "10096*", "nivel": "BAJO",
        "nombre": s("Divulgacion de timestamps via cabeceras HTTP"),
        "fix": "Cabeceras X-Runtime, X-Timestamp, X-Response-Time eliminadas con header_down.",
        "artefacto": "deploy/Caddyfile | deploy/nginx.conf",
    },
]

col_label = 32
col_value = pdf.w - pdf.l_margin - pdf.r_margin - col_label
for r in resueltas:
    pdf.set_fill_color(40, 160, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(25, 8, f"  [{r['nivel']}]", fill=True, border=1)
    pdf.cell(0, 8, s(f"  {r['nombre']}"), fill=True, border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    for label, value in [("ID ZAP", r["id"]), ("Estado", "RESUELTO"), ("Fix", r["fix"]), ("Artefacto", r["artefacto"])]:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(col_label, 6, s(label + ":"), fill=True, border=1)
        pdf.set_font("Helvetica", size=9)
        pdf.set_fill_color(235, 250, 235)
        pdf.multi_cell(col_value, 6, s(value), fill=True, border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

# ── Alertas remanentes — riesgo aceptado ─────────────────────────────────────
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, s("Alertas Remanentes — Riesgo Aceptado / Falso Positivo"), new_x="LMARGIN", new_y="NEXT")

remanentes = [
    {
        "id": "10055", "nivel": "MEDIO", "color": (230, 140, 30),
        "nombre": "CSP: script-src unsafe-eval / unsafe-inline / style-src unsafe-inline",
        "descripcion": (
            "React (motor de Streamlit) requiere unsafe-eval para compilacion JSX en runtime. "
            "Streamlit y Plotly requieren unsafe-inline para estilos y scripts dinamicos. "
            "Estas directivas no pueden eliminarse sin reemplazar el framework completo."
        ),
        "clasificacion": s("Riesgo Aceptado — Inherente a React/Streamlit"),
        "mitigacion": (
            "Mitigado parcialmente: resto del CSP es estricto (object-src 'none', base-uri 'self', "
            "form-action 'self', frame-ancestors 'self'). El riesgo XSS real es bajo dado que "
            "el dashboard no acepta entrada de usuarios externos."
        ),
    },
    {
        "id": "10096", "nivel": "BAJO", "color": (180, 160, 0),
        "nombre": s("Divulgacion de Marcas de Tiempo — Unix en codigo JS"),
        "descripcion": (
            "Los numeros detectados (ej. 1540483477) son constantes numericas dentro de los "
            "bundles JavaScript compilados de Streamlit/React (emotion-styled, v4.js). "
            "No son cabeceras HTTP ni metadata del servidor."
        ),
        "clasificacion": s("Falso Positivo — Constantes en codigo compilado del framework"),
        "mitigacion": "No requiere accion. Las cabeceras HTTP de timestamp fueron eliminadas (ver alertas resueltas).",
    },
]

for r in remanentes:
    pdf.set_fill_color(*r["color"])
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(25, 8, f"  [{r['nivel']}]", fill=True, border=1)
    pdf.cell(0, 8, s(f"  {r['nombre']}"), fill=True, border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    for label, value in [
        ("ID ZAP", r["id"]),
        ("Estado", r["clasificacion"]),
        ("Descripcion", r["descripcion"]),
        ("Mitigacion", r["mitigacion"]),
    ]:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(col_label, 6, s(label + ":"), fill=True, border=1)
        pdf.set_font("Helvetica", size=9)
        pdf.set_fill_color(255, 248, 220)
        pdf.multi_cell(col_value, 6, s(value), fill=True, border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

# ── Informativas ─────────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, s("Alertas Informativas (sin cambio)"), new_x="LMARGIN", new_y="NEXT")
for inf_id, inf_name, inf_nota in [
    ("10109", "Aplicacion Web Moderna (SPA)", s("Esperado. Spider AJAX recomendado en versiones futuras.")),
    ("10027", "Comentarios en JavaScript", s("Generados por Streamlit/React. Se resuelven al desplegar en produccion.")),
]:
    pdf.set_fill_color(50, 100, 200)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(25, 8, "  [INFO]", fill=True, border=1)
    pdf.cell(0, 8, s(f"  {inf_name}"), fill=True, border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", size=9)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(col_label, 6, "ID ZAP:", fill=True, border=1)
    pdf.set_fill_color(240, 240, 240)
    pdf.multi_cell(col_value, 6, inf_id, fill=True, border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(col_label, 6, "Nota:", fill=True, border=1)
    pdf.set_fill_color(240, 240, 240)
    pdf.multi_cell(col_value, 6, inf_nota, fill=True, border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

# ── Conclusiones ─────────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "Conclusiones - Version 1 Post-Remediacion", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=10)
pdf.multi_cell(0, 6, s(
    "Las 4 alertas de configuracion del servidor identificadas en el escaneo inicial han sido "
    "completamente resueltas mediante el proxy inverso Caddy (deploy/Caddyfile) y su equivalente "
    "para produccion ESPOCH (deploy/nginx.conf).\n\n"
    "Las 3 alertas Medio remanentes (unsafe-eval, unsafe-inline) son requisitos internos del "
    "framework React sobre el que opera Streamlit y no pueden eliminarse sin reemplazar la "
    "tecnologia base. El riesgo XSS real es bajo: el dashboard no acepta entrada de usuarios "
    "externos y opera en red institucional cerrada.\n\n"
    "La alerta Bajo de timestamp es un falso positivo: ZAP detecta constantes numericas dentro "
    "de los bundles JavaScript compilados del framework, no cabeceras HTTP del servidor.\n\n"
    "El Dashboard ETalent Version 1 esta listo para presentacion y despliegue en infraestructura "
    "ESPOCH utilizando la configuracion Nginx proporcionada en deploy/nginx.conf."
))

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zap_report_v1_fixed.pdf")
pdf.output(out_path)
print(f"PDF generado: {out_path}")
