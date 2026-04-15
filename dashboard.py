import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ──────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard ETalent · ESPOCH",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# ESTILOS GLOBALES
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Fondo general */
[data-testid="stAppViewContainer"] { background-color: #EEF2F7; }
[data-testid="stHeader"]           { background: transparent; }
div.block-container                { padding: 0.6rem 1.8rem 0.6rem 1.8rem; }

/* Ocultar chrome de Streamlit */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1E3A5F 100%);
    border-right: 1px solid #2D4A6B;
}
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #F8FAFC !important; }
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background-color: #2563EB !important;
}
[data-testid="stSidebar"] hr { border-color: #2D4A6B !important; }

/* ── KPI cards ── */
.kpi-box {
    background: white;
    border-radius: 14px;
    padding: 16px 14px 12px;
    text-align: center;
    box-shadow: 0 2px 14px rgba(0,0,0,0.07);
}
.kpi-value { font-size: 28px; font-weight: 800; margin: 0; line-height: 1; font-family: Inter, sans-serif; }
.kpi-label { font-size: 10px; color: #6B7280; margin-top: 5px;
             text-transform: uppercase; letter-spacing: 0.7px; font-weight: 600; }
.kpi-sub   { font-size: 11px; color: #9CA3AF; margin-top: 2px; }

/* ── Encabezados de sección ── */
.sec-title {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.9px; color: #374151;
    margin: 8px 0 3px 0; padding-left: 9px;
    border-left: 3px solid #2563EB;
}

/* ── Contenedor blanco para gráficos ── */
.card {
    background: white; border-radius: 14px;
    padding: 14px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# CARGA DE DATOS
# ──────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_ettalent_clean.csv")

NUMERIC_COLS = [
    "PUNTAJE MÁXIMO",
    "AUTOEVALUACIÓN (FORMS)",
    "% AUTOEVALUACIÓN (FORMS)",
    "% AUTOEVALUACIÓN TOTAL",
    "VERIFICACIÓN (ESPOCH)",
    "%EVALUACIÓN",
    "PROMEDIO",
    "%PROMEDIO TOTAL DIMENSIÓN",
]

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=["IES ANONIMIZADA", "%PROMEDIO TOTAL DIMENSIÓN"], inplace=True)
    return df

df_raw = load_data(CSV_PATH)

# ──────────────────────────────────────────────────────────────
# SIDEBAR — FILTROS
# Estructura lista para recibir nuevas dimensiones en el futuro
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 ETalent")
    st.markdown("**Evaluación de Transparencia Institucional**")
    st.markdown("---")
    st.markdown("### Filtros")

    dim_macro_opts = sorted(df_raw["DIMENSION_MACRO"].unique())
    uni_opts       = sorted(df_raw["IES ANONIMIZADA"].unique())
    subdim_opts    = sorted(df_raw["DIMENSIÓN"].unique())

    # Filtro 1: Dimensión macro — relevante cuando haya más hojas
    sel_macro  = st.multiselect(
        "Dimensión",
        dim_macro_opts,
        default=dim_macro_opts,
        help="Selecciona las dimensiones de evaluación a visualizar.",
    )

    # Filtro 2: Universidad
    sel_uni = st.multiselect(
        "Universidad",
        uni_opts,
        default=uni_opts,
        help="Filtra por universidad anonimizada.",
    )

    # Filtro 3: Sub-dimensión
    sel_subdim = st.multiselect(
        "Sub-Dimensión",
        subdim_opts,
        default=subdim_opts,
        help="Filtra por sub-dimensión de transparencia.",
    )

    st.markdown("---")
    st.markdown(f"**Dimensiones activas:** {len(sel_macro)}")
    st.markdown(f"**Universidades:** {len(sel_uni)}")
    st.markdown(f"**Sub-dimensiones:** {len(sel_subdim)}")
    st.markdown("---")
    st.markdown(
        "<div style='font-size:10px; color:#64748B;'>"
        "ETalent · ESPOCH · 2026<br>"
        "Jefferson Jordan"
        "</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────
# APLICAR FILTROS
# ──────────────────────────────────────────────────────────────
df = df_raw[
    df_raw["DIMENSION_MACRO"].isin(sel_macro) &
    df_raw["IES ANONIMIZADA"].isin(sel_uni) &
    df_raw["DIMENSIÓN"].isin(sel_subdim)
].copy()

# Guardia: si el filtro dejó vacío el df, mostrar aviso y detener
if df.empty:
    st.warning("No hay datos con los filtros seleccionados. Ajusta los filtros en la barra lateral.")
    st.stop()

# ──────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────
n_dims = df["DIMENSION_MACRO"].nunique()
n_unis = df["IES ANONIMIZADA"].nunique()
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #0F172A 0%, #1D4ED8 60%, #06B6D4 100%);
    border-radius: 14px; padding: 18px 28px; margin-bottom: 14px; color: white;">
  <h1 style="margin:0; font-size:21px; font-weight:800; letter-spacing:-0.3px; font-family:Inter,sans-serif;">
      🎓 Dashboard ETalent · Transparencia Institucional
  </h1>
  <p style="margin:5px 0 0 0; opacity:0.75; font-size:12px;">
      ESPOCH &nbsp;·&nbsp; {n_unis} Universidades Ecuatorianas &nbsp;·&nbsp; {n_dims} Dimensión(es) activa(s)
  </p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# PRECÁLCULOS GLOBALES
# ──────────────────────────────────────────────────────────────
# Un valor de %PROMEDIO TOTAL DIMENSIÓN por universidad (ya forward-filled en ETL)
eis_kpi = (
    df.groupby("IES ANONIMIZADA")["%PROMEDIO TOTAL DIMENSIÓN"]
    .first()
    .dropna()
)

prom_global = eis_kpi.mean()
mejor_eis   = eis_kpi.idxmax() if not eis_kpi.empty else "—"
peor_eis    = eis_kpi.idxmin() if not eis_kpi.empty else "—"
mejor_val   = eis_kpi.max()    if not eis_kpi.empty else 0.0
peor_val    = eis_kpi.min()    if not eis_kpi.empty else 0.0

# ──────────────────────────────────────────────────────────────
# KPI CARDS — 3 tarjetas
# ──────────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3, gap="large")

kpis = [
    (k1, f"{prom_global:.1f}%",  "Promedio Global",      "de cumplimiento general",         "#2563EB"),
    (k2, mejor_eis,              "Mayor Cumplimiento",   f"{mejor_val:.1f}% promedio total", "#10B981"),
    (k3, peor_eis,               "Menor Cumplimiento",   f"{peor_val:.1f}% promedio total",  "#EF4444"),
]

for col, val, label, sub, color in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-box" style="border-top: 4px solid {color};">
            <div class="kpi-value" style="color:{color};">{val}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# FILA 2: Ranking  +  Radar
# ──────────────────────────────────────────────────────────────
FONT = dict(family="Inter, system-ui, sans-serif", size=11, color="#1F2937")
BG   = dict(paper_bgcolor="white", plot_bgcolor="white")

col_l, col_r = st.columns([3, 2], gap="medium")

# ── Ranking ────────────────────────────────────────────────────
with col_l:
    st.markdown('<div class="sec-title">Ranking de Universidades — % Promedio Total</div>',
                unsafe_allow_html=True)

    rank_df = eis_kpi.reset_index().sort_values("%PROMEDIO TOTAL DIMENSIÓN")
    rank_df.columns = ["UNI", "PCT"]
    rank_df["COLOR"] = rank_df["PCT"].apply(
        lambda x: "#10B981" if x >= 70 else ("#F59E0B" if x >= 50 else "#EF4444")
    )

    fig_bar = go.Figure(go.Bar(
        x=rank_df["PCT"],
        y=rank_df["UNI"],
        orientation="h",
        marker_color=rank_df["COLOR"],
        text=rank_df["PCT"].apply(lambda x: f"  {x:.1f}%"),
        textposition="outside",
        cliponaxis=False,
    ))
    fig_bar.add_vline(
        x=70, line_dash="dot", line_color="#10B981",
        annotation_text="Meta 70%", annotation_position="top right",
        annotation_font_color="#10B981",
    )
    fig_bar.update_layout(
        height=265,
        margin=dict(l=0, r=55, t=8, b=8),
        xaxis=dict(range=[0, 115], showgrid=True, gridcolor="#F3F4F6",
                   zeroline=False, ticksuffix="%",
                   tickfont=dict(size=10, color="#1F2937")),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#1F2937")),
        showlegend=False,
        font=FONT, **BG,
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

# ── Radar ───────────────────────────────────────────────────────
with col_r:
    st.markdown('<div class="sec-title">Perfil por Sub-Dimensión — % Verificación ESPOCH</div>',
                unsafe_allow_html=True)

    radar_df = df.groupby("DIMENSIÓN")["%EVALUACIÓN"].mean().reset_index()
    cats = radar_df["DIMENSIÓN"].tolist()
    vals = radar_df["%EVALUACIÓN"].tolist()
    # Cerrar el polígono
    cats_closed = cats + [cats[0]]
    vals_closed = vals + [vals[0]]

    fig_radar = go.Figure(go.Scatterpolar(
        r=vals_closed, theta=cats_closed,
        fill="toself",
        fillcolor="rgba(37,99,235,0.12)",
        line=dict(color="#2563EB", width=2.5),
        marker=dict(size=7, color="#2563EB"),
        hovertemplate="%{theta}: <b>%{r:.1f}%</b><extra></extra>",
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="white",
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickformat=".0f", ticksuffix="%",
                tickfont=dict(size=9), gridcolor="#E5E7EB",
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color="#374151"),
                gridcolor="#E5E7EB",
            ),
        ),
        height=265,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor="white",
        showlegend=False,
        font=FONT,
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

# ──────────────────────────────────────────────────────────────
# FILA 3: Heatmap  (universidades × sub-dimensiones)
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Mapa de Calor — % Verificación ESPOCH por Universidad y Sub-Dimensión</div>',
            unsafe_allow_html=True)

heat_pivot = (
    df.pivot_table(
        index="IES ANONIMIZADA",
        columns="DIMENSIÓN",
        values="%EVALUACIÓN",
        aggfunc="mean",
    )
)
# Ordenar universidades por promedio descendente
heat_pivot = heat_pivot.loc[heat_pivot.mean(axis=1).sort_values(ascending=False).index]

z_vals  = np.round(heat_pivot.values.astype(float), 1)
text_vals = np.where(np.isnan(z_vals), "N/D", z_vals.astype(str) + "%")

fig_heat = go.Figure(go.Heatmap(
    z=z_vals,
    x=heat_pivot.columns.tolist(),
    y=heat_pivot.index.tolist(),
    colorscale=[
        [0.00, "#FEE2E2"], [0.33, "#EF4444"],
        [0.34, "#FEF3C7"], [0.66, "#10B981"],
        [1.00, "#064E3B"],
    ],
    zmin=0, zmax=100,
    text=text_vals,
    texttemplate="<b>%{text}</b>",
    textfont=dict(size=10),
    colorbar=dict(
        title=dict(text="% Verif.", side="right"),
        ticksuffix="%", thickness=12, len=0.85,
    ),
    hoverongaps=False,
))
n_eis = len(heat_pivot)
fig_heat.update_layout(
    height=max(240, n_eis * 36),
    margin=dict(l=0, r=0, t=30, b=10),
    xaxis=dict(side="top", tickfont=dict(size=11, color="#1F2937")),
    yaxis=dict(tickfont=dict(size=10, color="#374151"), autorange="reversed"),
    font=FONT, **BG,
)
st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})

# ──────────────────────────────────────────────────────────────
# FILA 4: Autoevaluación vs Verificación — ancho completo
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Autoevaluación vs Verificación ESPOCH — Promedio por Universidad</div>',
            unsafe_allow_html=True)

# Un valor por universidad (forward-filled en ETL → .first() es suficiente)
compare_df = (
    df.groupby("IES ANONIMIZADA")
    .agg(
        autoevaluacion=("% AUTOEVALUACIÓN TOTAL", "first"),
        verificacion  =("PROMEDIO",               "first"),
    )
    .reset_index()
    .sort_values("verificacion", ascending=False)
)

fig_grp = go.Figure()
fig_grp.add_trace(go.Bar(
    name="Autoevaluación (Forms)",
    x=compare_df["IES ANONIMIZADA"],
    y=compare_df["autoevaluacion"],
    marker_color="#2563EB",
    text=compare_df["autoevaluacion"].apply(lambda x: f"{x:.1f}%"),
    textposition="outside",
    cliponaxis=False,
))
fig_grp.add_trace(go.Bar(
    name="Verificación ESPOCH",
    x=compare_df["IES ANONIMIZADA"],
    y=compare_df["verificacion"],
    marker_color="#10B981",
    text=compare_df["verificacion"].apply(lambda x: f"{x:.1f}%"),
    textposition="outside",
    cliponaxis=False,
))
fig_grp.update_layout(
    barmode="group",
    height=260,
    margin=dict(l=0, r=10, t=10, b=10),
    yaxis=dict(range=[0, 118], ticksuffix="%", gridcolor="#F3F4F6",
               zeroline=False, tickfont=dict(size=10, color="#1F2937")),
    xaxis=dict(tickfont=dict(size=11, color="#1F2937")),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="right", x=1,
        font=dict(size=11, color="#1F2937"),
    ),
    font=FONT, **BG,
)
st.plotly_chart(fig_grp, use_container_width=True, config={"displayModeBar": False})

# ──────────────────────────────────────────────────────────────
# FILA 5: Tabla analítica
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Resultados por Sub-Dimensión</div>',
            unsafe_allow_html=True)

tc1, tc2 = st.columns([3, 1])
with tc1:
    st.markdown(
        '<p style="color:#1F2937;font-weight:600;font-size:12px;margin-bottom:3px;">Ordenar por</p>',
        unsafe_allow_html=True,
    )
    orden = st.selectbox(
        "_orden",
        ["% Promedio Total (↓)", "Universidad", "Sub-Dimensión", "% Verificación (↓)"],
        index=0,
        label_visibility="collapsed",
    )
with tc2:
    st.markdown(
        '<p style="color:#1F2937;font-weight:600;font-size:12px;margin-bottom:3px;">Dimensión</p>',
        unsafe_allow_html=True,
    )
    # Mini-filtro de dimensión macro para la tabla (útil cuando haya varias)
    macro_tabla = st.selectbox(
        "_macro_tabla",
        ["Todas"] + sorted(df["DIMENSION_MACRO"].unique().tolist()),
        index=0,
        label_visibility="collapsed",
    )

# Construir tabla
tabla_df = df.copy()
if macro_tabla != "Todas":
    tabla_df = tabla_df[tabla_df["DIMENSION_MACRO"] == macro_tabla]

tabla_display = pd.DataFrame({
    "Universidad":     tabla_df["IES ANONIMIZADA"],
    "Dimensión":       tabla_df["DIMENSION_MACRO"],
    "Sub-Dimensión":   tabla_df["DIMENSIÓN"],
    "% Autoevaluación": tabla_df["% AUTOEVALUACIÓN (FORMS)"].round(1).astype(str) + "%",
    "% Verificación":  tabla_df["%EVALUACIÓN"].round(1).astype(str) + "%",
    "% Promedio Total": tabla_df["%PROMEDIO TOTAL DIMENSIÓN"].round(1).astype(str) + "%",
})

# Aplicar orden
if orden == "Universidad":
    tabla_display = tabla_display.sort_values(["Universidad", "Sub-Dimensión"])
elif orden == "Sub-Dimensión":
    tabla_display = tabla_display.sort_values(["Sub-Dimensión", "Universidad"])
elif orden == "% Verificación (↓)":
    tabla_display = tabla_display.sort_values(
        "% Verificación", ascending=False,
        key=lambda s: s.str.replace("%", "").astype(float),
    )
else:  # % Promedio Total (↓)
    tabla_display = tabla_display.sort_values(
        "% Promedio Total", ascending=False,
        key=lambda s: s.str.replace("%", "").astype(float),
    )

st.dataframe(
    tabla_display,
    use_container_width=True,
    height=240,
    hide_index=True,
    column_config={
        "Universidad":      st.column_config.TextColumn("Universidad",    width="medium"),
        "Dimensión":        st.column_config.TextColumn("Dimensión",      width="small"),
        "Sub-Dimensión":    st.column_config.TextColumn("Sub-Dimensión",  width="medium"),
        "% Autoevaluación": st.column_config.TextColumn("% Autoevaluación", width="small"),
        "% Verificación":   st.column_config.TextColumn("% Verificación",   width="small"),
        "% Promedio Total": st.column_config.TextColumn("% Promedio Total", width="small"),
    },
)
st.caption(f"Mostrando {len(tabla_display)} registros · Fuente: {', '.join(df['DIMENSION_MACRO'].unique())}")

# ──────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 14px 0 2px 0;
            color:#9CA3AF; font-size:11px;
            border-top: 1px solid #E5E7EB; margin-top:12px;">
    Dashboard ETalent &nbsp;·&nbsp; ESPOCH &nbsp;·&nbsp;
    Prácticas Laborales &nbsp;·&nbsp; Jefferson Jordan 2026
</div>
""", unsafe_allow_html=True)
