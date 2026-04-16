from fpdf import FPDF
from datetime import date

def s(text):
    """Sanitize text to latin-1 safe characters."""
    return (text
        .replace('\u2013', '-').replace('\u2014', '-')
        .replace('\u00b7', '*').replace('\u00e9', 'e')
        .replace('\u00f3', 'o').replace('\u00fa', 'u')
        .replace('\u00ed', 'i').replace('\u00e1', 'a')
        .replace('\u00f1', 'n').replace('\u00fc', 'u')
    )

class ZapReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(30, 80, 160)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "Informe de Seguridad - OWASP ZAP", fill=True, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, s(f"Dashboard ETalent - ESPOCH | Generado: {date.today().strftime('%d/%m/%Y')} | Pag. {self.page_no()}"), align="C")

pdf = ZapReport()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Helvetica", size=10)

# Meta
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "Información del Escaneo", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=10)
meta = [
    ("Objetivo", "http://localhost:8501"),
    ("Herramienta", "OWASP ZAP 2.16.1"),
    ("Tipo de escaneo", "Quick Scan (Spider + Active Scan)"),
    ("Fecha", date.today().strftime("%d/%m/%Y")),
    ("Proyecto", "Dashboard ETalent - ESPOCH"),
    ("Responsable", "Jefferson Jordan"),
]
for k, v in meta:
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 7, f"{k}:", border=0)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 7, v, new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

# Resumen
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "Resumen de Alertas", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "B", 10)
pdf.set_fill_color(60, 60, 60)
pdf.set_text_color(255, 255, 255)
pdf.cell(90, 8, "Nivel de Riesgo", fill=True, border=1)
pdf.cell(40, 8, "N° de Alertas", fill=True, border=1, align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)

summary = [
    ((220, 50, 50),   "Alto",        "0"),
    ((230, 140, 30),  "Medio",       "1"),
    ((200, 180, 0),   "Bajo",        "3"),
    ((50, 100, 200),  "Informativo", "2"),
]
for color, level, count in summary:
    pdf.set_fill_color(*color)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(90, 7, f"  {level}", fill=True, border=1)
    pdf.cell(40, 7, count, fill=True, border=1, align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(6)

# Alertas detalladas
alerts = [
    {
        "id": "10038",
        "nivel": "MEDIO",
        "color": (230, 140, 30),
        "nombre": "Cabecera Content Security Policy (CSP) no configurada",
        "instancias": 3,
        "descripcion": (
            "Falta el encabezado HTTP 'Content-Security-Policy' en las respuestas del servidor. "
            "Sin esta politica, el navegador no tiene restricciones sobre que recursos puede cargar, "
            "facilitando ataques Cross-Site Scripting (XSS) e inyeccion de datos."
        ),
        "solucion": (
            "Configurar un reverse proxy (Nginx/Apache) delante de Streamlit y agregar:\n"
            "  add_header Content-Security-Policy \"default-src 'self'; script-src 'self' 'unsafe-inline';\";"
        ),
        "referencias": "OWASP Top 10 A05:2021 - Security Misconfiguration",
    },
    {
        "id": "10096",
        "nivel": "BAJO",
        "color": (180, 160, 0),
        "nombre": "Divulgacion de Marcas de Tiempo (Unix Timestamp)",
        "instancias": 2,
        "descripcion": (
            "El servidor expone timestamps en formato Unix en algunas respuestas HTTP. "
            "Esto puede revelar informacion sobre la infraestructura y facilitar ataques de reconocimiento."
        ),
        "solucion": "Filtrar o eliminar cabeceras que expongan timestamps internos desde el proxy.",
        "referencias": "CWE-200: Exposure of Sensitive Information",
    },
    {
        "id": "10036",
        "nivel": "BAJO",
        "color": (180, 160, 0),
        "nombre": "Filtracion de version en cabecera 'Server'",
        "instancias": 39,
        "descripcion": (
            "El encabezado HTTP 'Server' revela la version exacta del stack (Python/Tornado). "
            "Esta informacion permite a atacantes buscar exploits conocidos para esa version especifica."
        ),
        "solucion": (
            "En Nginx: server_tokens off;\n"
            "En Apache: ServerTokens Prod; ServerSignature Off;"
        ),
        "referencias": "CWE-200 / OWASP A05:2021",
    },
    {
        "id": "10021",
        "nivel": "BAJO",
        "color": (180, 160, 0),
        "nombre": "Falta encabezado X-Content-Type-Options",
        "instancias": 46,
        "descripcion": (
            "Ausencia del encabezado 'X-Content-Type-Options: nosniff'. Sin el, el navegador puede "
            "realizar MIME-type sniffing e interpretar archivos con tipo incorrecto, "
            "habilitando posibles ataques de ejecucion de contenido."
        ),
        "solucion": (
            "Agregar en el proxy:\n"
            "  add_header X-Content-Type-Options \"nosniff\" always;"
        ),
        "referencias": "OWASP Top 10 A05:2021",
    },
    {
        "id": "10109",
        "nivel": "INFORMATIVO",
        "color": (50, 100, 200),
        "nombre": "Aplicacion Web Moderna (SPA detectada)",
        "instancias": 3,
        "descripcion": (
            "ZAP detecto que la aplicacion es una Single Page Application (SPA) basada en React/Streamlit. "
            "El spider tradicional tiene cobertura limitada en SPAs. No es una vulnerabilidad."
        ),
        "solucion": "Considerar usar el spider AJAX de ZAP para mayor cobertura en futuros escaneos.",
        "referencias": "N/A",
    },
    {
        "id": "10027",
        "nivel": "INFORMATIVO",
        "color": (50, 100, 200),
        "nombre": "Comentarios sospechosos en codigo JavaScript",
        "instancias": 4,
        "descripcion": (
            "Se encontraron comentarios en el JavaScript del frontend (generados por Streamlit/React) "
            "que contienen palabras como TODO, FIXME o debug. No representan vulnerabilidad directa "
            "pero revelan informacion sobre el proceso de desarrollo."
        ),
        "solucion": "Minificar y ofuscar el JavaScript en produccion. En Streamlit esto ocurre automaticamente al desplegar.",
        "referencias": "CWE-615: Inclusion of Sensitive Information in Source Code Comments",
    },
]

pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "Detalle de Alertas", new_x="LMARGIN", new_y="NEXT")

for alert in alerts:
    # Encabezado de alerta
    pdf.set_fill_color(*alert["color"])
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(25, 8, s(f"  [{alert['nivel']}]"), fill=True, border=1)
    pdf.cell(0, 8, s(f"  {alert['nombre']}"), fill=True, border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", size=9)

    rows = [
        ("ID ZAP", alert["id"]),
        ("Instancias", str(alert["instancias"])),
        ("Descripcion", alert["descripcion"]),
        ("Solucion", alert["solucion"]),
        ("Referencia", alert["referencias"]),
    ]
    col_label = 32
    col_value = pdf.w - pdf.l_margin - pdf.r_margin - col_label
    for label, value in rows:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(col_label, 6, s(label + ":"), fill=True, border=1)
        pdf.set_font("Helvetica", size=9)
        pdf.set_fill_color(240, 240, 240)
        pdf.multi_cell(col_value, 6, s(value), fill=True, border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

# Conclusiones
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 8, "Conclusiones y Recomendaciones", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", size=10)
conclusiones = (
    "El escaneo no detecto vulnerabilidades de nivel Alto. Las 4 alertas accionables "
    "(1 media, 3 bajas) estan relacionadas con cabeceras HTTP de seguridad ausentes, "
    "un problema comun en aplicaciones Streamlit que no utilizan un reverse proxy.\n\n"
    "Accion prioritaria: antes del despliegue en infraestructura ESPOCH, configurar Nginx "
    "como reverse proxy con las cabeceras: Content-Security-Policy, X-Content-Type-Options, "
    "y suprimir la version en el encabezado Server. Estas 3 correcciones eliminan el 100% "
    "de las alertas accionables encontradas."
)
pdf.multi_cell(0, 6, s(conclusiones))

out_path = "C:/Users/jeffe/Documents/PAO7/Prácticas Laborales/DashboardLooker/zap_report.pdf"
pdf.output(out_path)
print(f"PDF generado: {out_path}")
