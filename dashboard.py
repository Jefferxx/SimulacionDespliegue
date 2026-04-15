import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ──────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard ETalent",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta ESPOCH ──────────────────────────────────────────────
C_RED       = "#bc0712"
C_RED_DARK  = "#8b0000"
C_GREEN     = "#2e7d32"
C_ORANGE    = "#e65100"
C_BLUE      = "#1863dc"
C_DARK      = "#1a1a1a"
C_GRAY      = "#6b7280"
C_BG        = "#f2f2f2"
C_WHITE     = "#ffffff"
C_BORDER    = "#e0e0e0"

# Colores dinámicos para Universidades Anónimas
def get_eis_color(eis_name):
    # Paleta de 7 colores para las 7 universidades oficiales
    colors = [
        "#1863dc", "#00897b", "#7b1fa2", "#f57c00", "#bc0712", 
        "#455a64", "#2e7d32"
    ]
    try:
        # Extraer el número de "Universidad X"
        idx = int(eis_name.split(" ")[-1]) - 1
        return colors[idx % len(colors)]
    except:
        return C_GRAY

# ──────────────────────────────────────────────────────────────
# ESTILOS GLOBALES
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;600;700;800&display=swap');

html, body, * { font-family: 'Roboto', sans-serif !important; }

/* ── Ocultar chrome de Streamlit totalmente ── */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
[data-testid="stSidebar"] { display: none !important; }
footer                    { display: none !important; }

/* ── Sidebar columna personalizada ── */
/* Primer bloque horizontal = fila sidebar+main */
[data-testid="stHorizontalBlock"]:first-of-type {
    gap: 0 !important;
    align-items: stretch !important;
}
/* Primera columna = sidebar */
[data-testid="stHorizontalBlock"]:first-of-type
    > [data-testid="column"]:first-child {
    background: linear-gradient(180deg, #8b0000 0%, #bc0712 100%) !important;
    min-height: calc(100vh - 48px) !important;
    padding: 20px 14px 20px 14px !important;
    overflow-y: auto !important;
}
[data-testid="stHorizontalBlock"]:first-of-type
    > [data-testid="column"]:first-child * {
    color: white !important;
}
[data-testid="stHorizontalBlock"]:first-of-type
    > [data-testid="column"]:first-child hr {
    border-color: rgba(255,255,255,0.25) !important;
}
[data-testid="stHorizontalBlock"]:first-of-type
    > [data-testid="column"]:first-child label {
    font-size: 11px !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.6px !important;
}
[data-testid="stHorizontalBlock"]:first-of-type
    > [data-testid="column"]:first-child [data-baseweb="tag"] {
    background-color: rgba(255,255,255,0.2) !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
}
[data-testid="stHorizontalBlock"]:first-of-type
    > [data-testid="column"]:first-child [data-baseweb="tag"] span {
    color: white !important;
}
[data-testid="stHorizontalBlock"]:first-of-type
    > [data-testid="column"]:first-child [data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.12) !important;
    border-color: rgba(255,255,255,0.3) !important;
}
[data-testid="stHorizontalBlock"]:first-of-type
    > [data-testid="column"]:first-child input { color: white !important; }

/* Botón toggle dentro del sidebar */
[data-testid="stHorizontalBlock"]:first-of-type
    > [data-testid="column"]:first-child [data-testid="stButton"] button {
    background: rgba(255,255,255,0.15) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    font-size: 11px !important;
    width: 100% !important;
}
[data-testid="stHorizontalBlock"]:first-of-type
    > [data-testid="column"]:first-child [data-testid="stButton"] button:hover {
    background: rgba(255,255,255,0.25) !important;
}

/* ── Fondo general ── */
[data-testid="stAppViewContainer"] { background: #f2f2f2; }
div.block-container { padding: 0 !important; max-width: 100% !important; }

/* KPI cards */
.kpi-box {
    background: white;
    border-radius: 8px;
    padding: 12px 18px 10px 18px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.09);
    height: 100%;
}
.kpi-lbl {
    font-size: 10px; font-weight: 700; color: #9ca3af;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;
}
.kpi-val  { font-size: 28px; font-weight: 800; line-height: 1; margin: 0; }
.kpi-sub  { font-size: 10px; color: #6b7280; margin-top: 4px; }

/* Título de sección */
.sec-title {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: #1a1a1a; margin: 0 0 10px 0;
    padding-left: 8px; border-left: 3px solid #bc0712;
}

/* Tarjeta blanca */
.card {
    background: white; border-radius: 10px;
    padding: 15px 20px; box-shadow: 0 1px 6px rgba(0,0,0,0.07);
}

/* Tabla analítica — cabecera */
.tbl-header {
    background: #8b0000; color: white; padding: 10px 22px;
    border-radius: 10px 10px 0 0;
    font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
}

/* Tabla de resultados — fondo blanco garantizado */
[data-testid="stDataFrame"] {
    background: white !important;
    border-radius: 0 0 10px 10px !important;
    overflow: hidden;
}
[data-testid="stDataFrame"] iframe {
    background: white !important;
}

</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# CARGA DE DATOS
# ──────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "dataset_ettalent_clean.csv")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["PROMEDIO", "PUNTAJE_1", "PUNTAJE_2"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=["EIS", "PROMEDIO"], inplace=True)
    return df

df_raw = load_data(CSV_PATH)

# ── Session state para controlar visibilidad del sidebar ──────
if "sidebar_open" not in st.session_state:
    st.session_state["sidebar_open"] = True

# ──────────────────────────────────────────────────────────────
# HEADER (full-width)
# ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background: linear-gradient(90deg, {C_RED_DARK} 0%, {C_RED} 100%);
            padding: 0 28px; height:48px;
            display: flex; justify-content: space-between; align-items: center;">
  <div style="color:white; font-size:17px; font-weight:700; letter-spacing:-0.2px;">
    ETalent &nbsp;&middot;&nbsp; Evaluación de Transparencia Universitaria
  </div>
  <div style="color:rgba(255,255,255,0.78); font-size:9px; font-weight:600;
              letter-spacing:1px; text-transform:uppercase; text-align:right;">
    Business Intelligence Dashboard &nbsp;&middot;&nbsp; ESPOCH &nbsp;&middot;&nbsp; 2026
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# OPCIONES DE FILTRO
# ──────────────────────────────────────────────────────────────
# Asegurar orden numérico para "Universidad 1, Universidad 2..."
eis_opts  = sorted(df_raw["EIS"].unique(), key=lambda x: int(x.split(" ")[-1]) if "Universidad" in x else x)
hoja_opts = sorted(df_raw["HOJA"].unique())
dim_opts  = sorted(df_raw["DIMENSION"].unique())

# ──────────────────────────────────────────────────────────────
# LAYOUT PRINCIPAL: sidebar columna + contenido
# ──────────────────────────────────────────────────────────────
if st.session_state["sidebar_open"]:
    col_s, col_m = st.columns([1, 4.5], gap="small")

    with col_s:
        st.markdown("""
        <div style="text-align:center; padding:6px 0 14px 0;">
            <div style="font-size:18px; font-weight:800; letter-spacing:-0.5px;">Filtros</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Ocultar panel", key="btn_cerrar"):
            st.session_state["sidebar_open"] = False
            st.rerun()

        st.markdown("---")
        st.markdown('<div style="font-size:10px; font-weight:700; opacity:0.6; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">Universidades</div>', unsafe_allow_html=True)
        sel_eis = st.multiselect("_eis", eis_opts, default=eis_opts, key="f_eis", label_visibility="collapsed")

        st.markdown('<div style="font-size:10px; font-weight:700; opacity:0.6; text-transform:uppercase; letter-spacing:1px; margin:12px 0 8px 0;">Dimensión</div>', unsafe_allow_html=True)
        sel_hoja = st.multiselect("_hoja", hoja_opts, default=hoja_opts, key="f_hoja", label_visibility="collapsed")

        st.markdown('<div style="font-size:10px; font-weight:700; opacity:0.6; text-transform:uppercase; letter-spacing:1px; margin:12px 0 8px 0;">Sub-Dimensión</div>', unsafe_allow_html=True)
        sel_dim = st.multiselect("_dim", dim_opts, default=dim_opts, key="f_dim", label_visibility="collapsed")

        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:9px; opacity:0.55; line-height:1.8; margin-top:10px;">
            <b style="opacity:0.9;">Analizando:</b> {len(sel_eis)} instituciones<br>
            <b style="opacity:0.9;">Métricas:</b> {len(df_raw)} registros totales
        </div>
        """, unsafe_allow_html=True)

else:
    # Recuperar valores de session_state (última selección)
    sel_eis  = st.session_state.get("f_eis",  eis_opts)
    sel_hoja = st.session_state.get("f_hoja", hoja_opts)
    sel_dim  = st.session_state.get("f_dim",  dim_opts)
    
    col_m = st.container()
    with col_m:
        if st.button("Mostrar filtros", key="btn_abrir"):
            st.session_state["sidebar_open"] = True
            st.rerun()

# ── Aplicar filtros
df = df_raw[
    df_raw["EIS"].isin(sel_eis) &
    df_raw["HOJA"].isin(sel_hoja) &
    df_raw["DIMENSION"].isin(sel_dim)
].copy()

if df.empty:
    st.error("Sin datos. Ajusta los filtros.")
    st.stop()

# ──────────────────────────────────────────────────────────────
# PRE-CÁLCULOS GLOBALES
# ──────────────────────────────────────────────────────────────
eis_prom  = df.groupby("EIS")["PROMEDIO"].mean() * 100
prom_global = df["PROMEDIO"].mean() * 100
mejor_eis   = eis_prom.idxmax() if len(eis_prom) else "—"
peor_eis    = eis_prom.idxmin() if len(eis_prom) else "—"
mejor_val   = eis_prom.max()    if len(eis_prom) else 0
peor_val    = eis_prom.min()    if len(eis_prom) else 0

# ──────────────────────────────────────────────────────────────
# CONFIG COMPARTIDA DE PLOTLY
# ──────────────────────────────────────────────────────────────
PCFG = dict(displayModeBar=False)
BASE_LAYOUT = dict(
    paper_bgcolor=C_WHITE, plot_bgcolor=C_WHITE,
    font=dict(family="Roboto, sans-serif", size=11, color=C_DARK),
)

# ──────────────────────────────────────────────────────────────
# CONTENIDO PRINCIPAL (dentro de col_m)
# ──────────────────────────────────────────────────────────────
with col_m:
    st.markdown('<div style="padding: 15px 20px 0 20px;">', unsafe_allow_html=True)

    # ── KPIs (Simplificados a 3) ──────────────────────────────
    k1, k2, k3 = st.columns(3, gap="large")

    def kpi(col, label, val, sub, color):
        with col:
            st.markdown(f"""
            <div class="kpi-box" style="border-top:3px solid {color};">
                <div class="kpi-lbl">{label}</div>
                <div class="kpi-val" style="color:{color};">{val}</div>
                <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    kpi(k1, "PROMEDIO GLOBAL",    f"{prom_global:.1f}%", "Cumplimiento institucional", C_RED)
    kpi(k2, "MAYOR CUMPLIMIENTO", mejor_eis,             f"{mejor_val:.1f}% promedio",  C_GREEN)
    kpi(k3, "MENOR CUMPLIMIENTO", peor_eis,              f"{peor_val:.1f}% promedio",   C_ORANGE)

    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

    # ── FILA 2: Ranking + Radar ───────────────────────────────
    c_rank, c_radar = st.columns([3, 2], gap="medium")

    with c_rank:
        st.markdown('<div class="sec-title">Ranking de Universidades</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        bar_df = eis_prom.reset_index().sort_values("PROMEDIO")
        bar_df.columns = ["EIS", "PCT"]
        bar_df["COLOR"] = bar_df["PCT"].apply(
            lambda x: C_GREEN if x >= 70 else (C_ORANGE if x >= 50 else C_RED)
        )

        fig_bar = go.Figure(go.Bar(
            x=bar_df["PCT"], y=bar_df["EIS"],
            orientation="h",
            marker_color=bar_df["COLOR"],
            text=bar_df["PCT"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
            cliponaxis=False,
        ))
        fig_bar.update_layout(
            **BASE_LAYOUT,
            height=310,
            margin=dict(l=0, r=60, t=10, b=10),
            xaxis=dict(range=[0, 115], showgrid=True, gridcolor="#f5f5f5", zeroline=False),
            yaxis=dict(showgrid=False),
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True, config=PCFG)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_radar:
        st.markdown('<div class="sec-title">Perfil por Dimensión</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        radar_df = (df.groupby("HOJA")["PROMEDIO"].mean() * 100).reset_index()
        cats = radar_df["HOJA"].tolist()
        vals = radar_df["PROMEDIO"].tolist()
        cats_c = cats + [cats[0]]
        vals_c = vals + [vals[0]]

        fig_radar = go.Figure(go.Scatterpolar(
            r=vals_c, theta=cats_c,
            fill="toself",
            fillcolor="rgba(188,7,18,0.1)",
            line=dict(color=C_RED, width=2),
        ))
        fig_radar.update_layout(
            **BASE_LAYOUT,
            height=310,
            margin=dict(l=40, r=40, t=25, b=25),
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor=C_BORDER),
                angularaxis=dict(gridcolor=C_BORDER),
            ),
        )
        st.plotly_chart(fig_radar, use_container_width=True, config=PCFG)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

    # ── FILA 3: Heatmap ───────────────────────────────────────
    st.markdown('<div class="sec-title">Análisis de Desempeño por Sub-Dimensión</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)

    heat_df    = df.groupby(["EIS", "DIMENSION"])["PROMEDIO"].mean().reset_index()
    heat_pivot = heat_df.pivot(index="EIS", columns="DIMENSION", values="PROMEDIO") * 100
    eis_order  = eis_prom.sort_values(ascending=False).index.tolist()
    heat_pivot = heat_pivot.reindex([e for e in eis_order if e in heat_pivot.index])
    
    fig_heat = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=heat_pivot.columns.tolist(),
        y=heat_pivot.index.tolist(),
        colorscale="RdYlGn",
        zmin=0, zmax=100,
        text=np.vectorize(lambda v: f"{v:.0f}%" if not np.isnan(v) else "")(heat_pivot.values),
        texttemplate="%{text}",
        colorbar=dict(thickness=10, len=0.8),
        xgap=1, ygap=1,
    ))
    fig_heat.update_layout(
        **BASE_LAYOUT,
        height=max(220, len(heat_pivot) * 36),
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(side="top", tickangle=-25, tickfont=dict(size=9)),
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig_heat, use_container_width=True, config=PCFG)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

    # ── FILA 4: Comparativa de Dimensiones (Full Width) ───────
    st.markdown('<div class="sec-title">Comparativa por Dimensión Principal</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)

    grp = (df.groupby(["HOJA", "EIS"])["PROMEDIO"].mean() * 100).reset_index()
    fig_grp = go.Figure()
    # Ordenar universidades numéricamente para la leyenda
    sorted_eis = sorted(grp["EIS"].unique(), key=lambda x: int(x.split(" ")[-1]) if "Universidad" in x else x)
    for eis in sorted_eis:
        sub = grp[grp["EIS"] == eis]
        fig_grp.add_trace(go.Bar(
            name=eis, x=sub["HOJA"], y=sub["PROMEDIO"],
            marker_color=get_eis_color(eis),
        ))
    fig_grp.update_layout(
        **BASE_LAYOUT,
        barmode="group", height=300,
        margin=dict(l=0, r=0, t=10, b=40),
        yaxis=dict(range=[0, 110], ticksuffix="%"),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
    )
    st.plotly_chart(fig_grp, use_container_width=True, config=PCFG)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

    # ── FILA 5: Nueva Tabla Analítica ─────────────────────────
    st.markdown('<div class="tbl-header">Resultados por Variable</div>', unsafe_allow_html=True)
    
    table_df = df.groupby(["EIS", "HOJA", "DIMENSION", "VARIABLE"])["PROMEDIO"].mean().reset_index()
    table_df["PROMEDIO"] = (table_df["PROMEDIO"] * 100).round(1)
    
    st.dataframe(
        table_df.rename(columns={
            "EIS": "Universidad", "HOJA": "Dimensión", 
            "DIMENSION": "Sub-Dimensión", "VARIABLE": "Variable",
            "PROMEDIO": "Promedio %"
        }),
        use_container_width=True,
        height=240,
        hide_index=True,
        column_config={
            "Promedio %": st.column_config.ProgressColumn(
                "Promedio %", format="%f%%", min_value=0, max_value=100
            )
        }
    )

    # ── FOOTER ────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{C_DARK}; padding:10px 28px; margin-top:15px;
                display:flex; justify-content:space-between; align-items:center;">
        <div style="color:{C_RED}; font-style:italic; font-size:11px;">Hacemos historia</div>
        <div style="color:#9e9e9e; font-size:9px;">ESPOCH &middot; Prácticas Laborales &middot; 2026</div>
    </div>
    """, unsafe_allow_html=True)
