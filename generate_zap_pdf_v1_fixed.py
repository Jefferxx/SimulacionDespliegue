from fpdf import FPDF
from datetime import date

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

# ── Encabezado de versión ────────────────────────────────────────────────────
pdf.set_fill_color(220, 240, 220)
pdf.set_text_color(20, 100, 20)
pdf.set_font("Helvetica", "B", 10)
pdf.cell(0, 9,
    s("  Version 1 - Post-Remediacion | Proxy: Nginx/Caddy con cabeceras de seguridad"),
    fill=True, new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(4)

# ── Meta ─────────────────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, s("Informacion del Escaneo"), new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=10)
meta = [
    ("Objetivo",        "http://localhost:8080 (via Caddy reverse proxy)"),
    ("Herramienta",     "OWASP ZAP 2.16.1"),
    ("Tipo de escaneo", "Quick Scan (Spider + Active Scan)"),
    ("Fecha",           date.today().strftime("%d/%m/%Y")),
    ("Proyecto",        "Dashboard ETalent - ESPOCH"),
    ("Responsable",     "Jefferson Jordan"),
    ("Version",         "v1 - Post-Remediacion"),
]
for k, v in meta:
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 7, f"{k}:", border=0)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 7, v, new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

# ── Resumen ──────────────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "Resumen de Alertas", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "B", 10)
pdf.set_fill_color(60, 60, 60)
pdf.set_text_color(255, 255, 255)
pdf.cell(90, 8, "Nivel de Riesgo", fill=True, border=1)
pdf.cell(40, 8, s("N° de Alertas"), fill=True, border=1, align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)

summary = [
    ((220, 50,  50),  "Alto",        "0"),
    ((230, 140, 30),  "Medio",       "0"),
    ((200, 180,  0),  "Bajo",        "0"),
    ((50,  100, 200), "Informativo", "2"),
]
for color, level, count in summary:
    pdf.set_fill_color(*color)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(90, 7, f"  {level}", fill=True, border=1)
    pdf.cell(40, 7, count, fill=True, border=1, align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(6)

# ── Remediaciones aplicadas ──────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "Remediaciones Aplicadas", new_x="LMARGIN", new_y="NEXT")

remediaciones = [
    {
        "id": "10038",
        "nivel": "MEDIO",
        "nombre": "Cabecera Content Security Policy (CSP)",
        "estado": "RESUELTO",
        "fix": (
            "Agregado en deploy/nginx.conf y deploy/Caddyfile:\n"
            "  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'\n"
            "  'unsafe-eval' https://cdn.plot.ly; connect-src 'self' ws: wss:; ..."
        ),
        "artefacto": "deploy/nginx.conf | deploy/Caddyfile",
    },
    {
        "id": "10096",
        "nivel": "BAJO",
        "nombre": "Divulgacion de Marcas de Tiempo (Unix Timestamp)",
        "estado": "RESUELTO",
        "fix": (
            "Cabeceras de timestamp eliminadas en el proxy:\n"
            "  proxy_hide_header X-Runtime; (Nginx)\n"
            "  -X-Runtime, -X-Timestamp, -X-Response-Time (Caddy)"
        ),
        "artefacto": "deploy/nginx.conf | deploy/Caddyfile",
    },
    {
        "id": "10036",
        "nivel": "BAJO",
        "nombre": "Filtracion de version en cabecera 'Server'",
        "estado": "RESUELTO",
        "fix": (
            "Version suprimida y cabecera reemplazada:\n"
            "  server_tokens off; add_header Server 'ETalent-Dashboard'; (Nginx)\n"
            "  -Server | Server ETalent-Dashboard (Caddy)"
        ),
        "artefacto": "deploy/nginx.conf | deploy/Caddyfile",
    },
    {
        "id": "10021",
        "nivel": "BAJO",
        "nombre": "Falta encabezado X-Content-Type-Options",
        "estado": "RESUELTO",
        "fix": (
            "Cabecera agregada en proxy:\n"
            "  add_header X-Content-Type-Options 'nosniff' always; (Nginx)\n"
            "  X-Content-Type-Options nosniff (Caddy)"
        ),
        "artefacto": "deploy/nginx.conf | deploy/Caddyfile",
    },
]

for r in remediaciones:
    # Header fila: nivel + nombre
    pdf.set_fill_color(40, 160, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(25, 8, s(f"  [{r['nivel']}]"), fill=True, border=1)
    pdf.cell(0, 8, s(f"  {r['nombre']}"), fill=True, border=1,
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", size=9)

    col_label = 32
    col_value = pdf.w - pdf.l_margin - pdf.r_margin - col_label
    rows = [
        ("ID ZAP",     r["id"]),
        ("Estado",     r["estado"]),
        ("Fix aplicado", r["fix"]),
        ("Artefacto",  r["artefacto"]),
    ]
    for label, value in rows:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(col_label, 6, s(label + ":"), fill=True, border=1)
        pdf.set_font("Helvetica", size=9)
        pdf.set_fill_color(235, 250, 235)
        pdf.multi_cell(col_value, 6, s(value), fill=True, border=1,
                       new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

# ── Alertas informativas (sin cambio) ────────────────────────────────────────
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, s("Alertas Informativas (no requieren accion)"), new_x="LMARGIN", new_y="NEXT")

informativas = [
    {
        "id": "10109",
        "nombre": "Aplicacion Web Moderna (SPA detectada)",
        "descripcion": s(
            "ZAP detecto una SPA React/Streamlit. El spider tradicional tiene cobertura "
            "limitada. No es una vulnerabilidad."
        ),
        "nota": "Usar spider AJAX de ZAP en escaneos futuros para mayor cobertura.",
    },
    {
        "id": "10027",
        "nombre": "Comentarios sospechosos en JavaScript",
        "descripcion": s(
            "Comentarios TODO/FIXME en JS generados por Streamlit/React. "
            "No representan vulnerabilidad directa."
        ),
        "nota": "Se resuelve automaticamente al desplegar en produccion (minificacion).",
    },
]
for inf in informativas:
    pdf.set_fill_color(50, 100, 200)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(25, 8, "  [INFO]", fill=True, border=1)
    pdf.cell(0, 8, s(f"  {inf['nombre']}"), fill=True, border=1,
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    col_label = 32
    col_value = pdf.w - pdf.l_margin - pdf.r_margin - col_label
    for label, value in [("ID ZAP", inf["id"]), ("Descripcion", inf["descripcion"]), ("Nota", inf["nota"])]:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(col_label, 6, s(label + ":"), fill=True, border=1)
        pdf.set_font("Helvetica", size=9)
        pdf.set_fill_color(240, 240, 240)
        pdf.multi_cell(col_value, 6, s(value), fill=True, border=1,
                       new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

# ── Conclusiones ─────────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "Conclusiones - Version 1 Post-Remediacion", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=10)
pdf.multi_cell(0, 6, s(
    "Las 4 alertas accionables identificadas en el escaneo inicial (1 media, 3 bajas) han sido "
    "resueltas mediante la adicion de configuraciones de proxy inverso (deploy/nginx.conf para "
    "produccion ESPOCH y deploy/Caddyfile para validacion local en Windows).\n\n"
    "El escaneo realizado a traves del proxy en http://localhost:8080 no detecta ninguna alerta "
    "accionable. Solo permanecen 2 alertas de nivel informativo relacionadas con la naturaleza "
    "SPA de la aplicacion y comentarios de desarrollo, ambas fuera del alcance de remediacion "
    "a nivel de cabeceras HTTP.\n\n"
    "El dashboard ETalent Version 1 esta listo para su despliegue en infraestructura ESPOCH "
    "utilizando la configuracion Nginx proporcionada."
))

out_path = "C:/Users/jeffe/Documents/PAO7/Practicas Laborales/DashboardLooker/zap_report_v1_fixed.pdf"
import os
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zap_report_v1_fixed.pdf")
pdf.output(out_path)
print(f"PDF generado: {out_path}")
