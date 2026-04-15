import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard ETalent · ESPOCH",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# ESTILOS — Power BI / Looker institucional
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background-color: #F1F5F9;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
[data-testid="stHeader"]  { background: transparent !important; }
#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stSidebarCollapseButton"] { visibility: hidden !important; }
div.block-container { padding: 0.55rem 1.6rem 0.4rem 1.6rem; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(170deg, #0D1B2A 0%, #0F2744 55%, #1A3F6F 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #F8FAFC !important; font-weight: 700 !important; }
[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.1) !important;
    margin: 10px 0 !important;
}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background-color: #1D4ED8 !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] label {
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.7px !important;
    color: #94A3B8 !important;
}

/* ── KPI cards ── */
.kpi-box {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 16px 14px 13px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(15,23,42,0.06), 0 8px 24px rgba(15,23,42,0.04);
    transition: box-shadow .2s;
}
.kpi-box:hover { box-shadow: 0 4px 12px rgba(15,23,42,0.1), 0 12px 32px rgba(15,23,42,0.06); }
.kpi-value {
    font-size: 30px; font-weight: 800; margin: 0; line-height: 1;
    font-family: 'Inter', sans-serif; letter-spacing: -0.5px;
}
.kpi-label {
    font-size: 10px; color: #6B7280; margin-top: 6px;
    text-transform: uppercase; letter-spacing: 1px; font-weight: 600;
}
.kpi-sub { font-size: 11px; color: #94A3B8; margin-top: 3px; font-weight: 500; }

/* ── Encabezados de sección ── */
.sec-title {
    display: inline-block;
    font-size: 10.5px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: #1E3A5F;
    margin: 10px 0 3px 0; padding: 3px 10px 3px 10px;
    border-left: 3px solid #1D4ED8;
    background: rgba(29,78,216,0.05);
    border-radius: 0 6px 6px 0;
}

/* ── Tarjeta de gráfico ── */
.chart-card {
    background: #FFFFFF;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(15,23,42,0.06), 0 4px 16px rgba(15,23,42,0.04);
    overflow: hidden;
    margin-bottom: 2px;
}

/* ── Tabla ── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# PALETAS
# ──────────────────────────────────────────────────────────────────────────────
# 7 azules institucionales para universidades (fijos y distinguibles)
UNI_COLORS = {
    "UNIVERSIDAD 1": "#1D4ED8",
    "UNIVERSIDAD 2": "#2563EB",
    "UNIVERSIDAD 3": "#3B82F6",
    "UNIVERSIDAD 4": "#0EA5E9",
    "UNIVERSIDAD 5": "#0284C7",
    "UNIVERSIDAD 6": "#0369A1",
    "UNIVERSIDAD 7": "#075985",
}
UNI_FALLBACK = "#6B7280"

FONT  = dict(family="Inter, system-ui, sans-serif", size=11, color="#1E293B")
BG    = dict(paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF")
GRID  = "#F1F5F9"

PCFG  = {"displayModeBar": False}

# ──────────────────────────────────────────────────────────────────────────────
# CARGA DE DATOS
# ──────────────────────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_ettalent_clean.csv")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["RESULTADO"] = pd.to_numeric(df["RESULTADO"], errors="coerce")
    df.dropna(subset=["IES ANONIMIZADA", "RESULTADO"], inplace=True)
    return df

df_raw = load_data(CSV_PATH)

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR — FILTROS
# Estructura lista para todas las dimensiones; por ahora solo Transparencia
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 ETalent")
    st.markdown("**Evaluación de Transparencia Institucional**")
    st.markdown("---")

    st.markdown("### Filtros")

    dim_macro_opts = sorted(df_raw["DIMENSION_MACRO"].unique())
    uni_opts       = sorted(df_raw["IES ANONIMIZADA"].unique())
    subdim_opts    = sorted(df_raw["SUBDIMENSIÓN"].unique())

    sel_macro = st.multiselect(
        "Dimensión",
        dim_macro_opts,
        default=dim_macro_opts,
        help="Dimensiones de evaluación disponibles.",
    )
    sel_uni = st.multiselect(
        "Universidad",
        uni_opts,
        default=uni_opts,
        help="Universidades anonimizadas.",
    )
    sel_subdim = st.multiselect(
        "Sub-Dimensión",
        subdim_opts,
        default=subdim_opts,
        help="Sub-dimensiones de la hoja activa.",
    )

    st.markdown("---")

    # Contadores de estado del filtro
    n_dim   = len(sel_macro)
    n_uni   = len(sel_uni)
    n_sub   = len(sel_subdim)
    total_d = len(dim_macro_opts)
    total_u = len(uni_opts)
    total_s = len(subdim_opts)

    estado = "GENERAL" if (n_dim == total_d and n_uni == total_u and n_sub == total_s) else "PERSONALIZADO"
    color_estado = "#10B981" if estado == "GENERAL" else "#F59E0B"

    st.markdown(
        f'<div style="font-size:10px;font-weight:700;letter-spacing:1px;'
        f'color:{color_estado};margin-bottom:8px;">{estado}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="font-size:11px;color:#64748B;line-height:1.7;">'
        f'Dimensiones: <b style="color:#CBD5E1">{n_dim}/{total_d}</b><br>'
        f'Universidades: <b style="color:#CBD5E1">{n_uni}/{total_u}</b><br>'
        f'Sub-Dimensiones: <b style="color:#CBD5E1">{n_sub}/{total_s}</b>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        '<div style="font-size:10px;color:#475569;line-height:1.6;">'
        'ETalent · ESPOCH · 2026<br>Jefferson Jordan</div>',
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────────────
# APLICAR FILTROS
# ──────────────────────────────────────────────────────────────────────────────
df = df_raw[
    df_raw["DIMENSION_MACRO"].isin(sel_macro) &
    df_raw["IES ANONIMIZADA"].isin(sel_uni) &
    df_raw["SUBDIMENSIÓN"].isin(sel_subdim)
].copy()

if df.empty:
    st.warning("⚠️ No hay datos con los filtros seleccionados. Ajusta los filtros en la barra lateral.")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────
n_unis = df["IES ANONIMIZADA"].nunique()
n_dims = df["DIMENSION_MACRO"].nunique()
n_ind  = df["INDICADOR"].nunique()

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #0D1B2A 0%, #1D4ED8 55%, #0EA5E9 100%);
    border-radius: 14px; padding: 16px 28px; margin-bottom: 12px; color: white;
    display: flex; justify-content: space-between; align-items: center;">
  <div>
    <div style="font-size:20px; font-weight:800; letter-spacing:-0.4px; font-family:Inter,sans-serif;">
      Dashboard ETalent · Transparencia Institucional
    </div>
    <div style="margin-top:4px; opacity:0.72; font-size:12px; font-weight:500;">
      {n_unis} Universidades · {n_dims} Dimensión(es) · {n_ind} Indicadores
    </div>
  </div>
  <div style="
    background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.25);
    border-radius:8px; padding:6px 14px; font-size:11px; font-weight:700;
    letter-spacing:1.2px; color:white;">
    ESPOCH
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# PRECÁLCULOS
# ──────────────────────────────────────────────────────────────────────────────
eis_kpi     = df.groupby("IES ANONIMIZADA")["RESULTADO"].mean()
prom_global = df["RESULTADO"].mean()
mejor_eis   = eis_kpi.idxmax() if not eis_kpi.empty else "—"
peor_eis    = eis_kpi.idxmin() if not eis_kpi.empty else "—"
mejor_val   = eis_kpi.max()    if not eis_kpi.empty else 0.0
peor_val    = eis_kpi.min()    if not eis_kpi.empty else 0.0

# ──────────────────────────────────────────────────────────────────────────────
# KPI CARDS — 3 tarjetas
# ──────────────────────────────────────────────────────────────────────────────
k1, k2, k3 = st.columns(3, gap="large")
kpis = [
    (k1, f"{prom_global:.1f}%", "Resultado Global",       "promedio general de evaluación",          "#1D4ED8"),
    (k2, mejor_eis,             "Mayor Cumplimiento",      f"{mejor_val:.1f}% resultado promedio",    "#0EA5E9"),
    (k3, peor_eis,              "Menor Cumplimiento",      f"{peor_val:.1f}% resultado promedio",     "#EF4444"),
]
for col, val, label, sub, color in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-box" style="border-top:3px solid {color};">
          <div class="kpi-value" style="color:{color};">{val}</div>
          <div class="kpi-label">{label}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# FILA 2 — Ranking  +  Radar
# ──────────────────────────────────────────────────────────────────────────────
col_l, col_r = st.columns([3, 2], gap="medium")

with col_l:
    st.markdown('<div class="sec-title">Ranking de Universidades</div>', unsafe_allow_html=True)
    rank_df = eis_kpi.reset_index().sort_values("RESULTADO")
    rank_df.columns = ["UNI", "PCT"]
    rank_df["COLOR"] = rank_df["PCT"].apply(
        lambda x: "#10B981" if x >= 70 else ("#F59E0B" if x >= 50 else "#EF4444")
    )
    fig_bar = go.Figure(go.Bar(
        x=rank_df["PCT"], y=rank_df["UNI"],
        orientation="h",
        marker_color=rank_df["COLOR"],
        marker_line_width=0,
        text=rank_df["PCT"].apply(lambda x: f"  {x:.1f}%"),
        textposition="outside", textfont=dict(size=11, color="#374151"),
        cliponaxis=False,
    ))
    fig_bar.add_vline(
        x=70, line_dash="dot", line_color="#10B981", line_width=1.5,
        annotation_text="Meta 70%", annotation_position="top right",
        annotation_font=dict(color="#10B981", size=10),
    )
    fig_bar.update_layout(
        height=262, margin=dict(l=0, r=55, t=6, b=6),
        xaxis=dict(range=[0, 112], showgrid=True, gridcolor=GRID,
                   zeroline=False, ticksuffix="%",
                   tickfont=dict(size=10, color="#94A3B8"),
                   showline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#1E293B"), showline=False),
        showlegend=False, font=FONT, **BG,
    )
    st.plotly_chart(fig_bar, use_container_width=True, config=PCFG)

with col_r:
    st.markdown('<div class="sec-title">Perfil por Sub-Dimensión</div>', unsafe_allow_html=True)
    radar_df = df.groupby("SUBDIMENSIÓN")["RESULTADO"].mean().reset_index()
    cats = radar_df["SUBDIMENSIÓN"].tolist()
    vals = radar_df["RESULTADO"].tolist()
    fig_radar = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]], theta=cats + [cats[0]],
        fill="toself",
        fillcolor="rgba(29,78,216,0.10)",
        line=dict(color="#1D4ED8", width=2.5),
        marker=dict(size=7, color="#1D4ED8", line=dict(color="white", width=1.5)),
        hovertemplate="<b>%{theta}</b><br>%{r:.1f}%<extra></extra>",
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="white",
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickformat=".0f", ticksuffix="%",
                tickfont=dict(size=9, color="#94A3B8"),
                gridcolor=GRID, linecolor=GRID,
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color="#374151"),
                gridcolor=GRID, linecolor=GRID,
            ),
        ),
        height=262, margin=dict(l=35, r=35, t=18, b=18),
        paper_bgcolor="white", showlegend=False, font=FONT,
    )
    st.plotly_chart(fig_radar, use_container_width=True, config=PCFG)

# ──────────────────────────────────────────────────────────────────────────────
# FILA 3 — Heatmap
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Mapa de Calor — Resultado por Universidad y Sub-Dimensión</div>',
            unsafe_allow_html=True)

heat_pivot = df.pivot_table(
    index="IES ANONIMIZADA", columns="SUBDIMENSIÓN",
    values="RESULTADO", aggfunc="mean",
)
heat_pivot = heat_pivot.loc[heat_pivot.mean(axis=1).sort_values(ascending=False).index]

z = np.round(heat_pivot.values.astype(float), 1)
txt = np.where(np.isnan(z), "N/D", z.astype(str) + "%")

fig_heat = go.Figure(go.Heatmap(
    z=z, x=heat_pivot.columns.tolist(), y=heat_pivot.index.tolist(),
    colorscale=[
        [0.00, "#FEE2E2"], [0.30, "#FCA5A5"],
        [0.50, "#FEF3C7"], [0.70, "#6EE7B7"],
        [1.00, "#065F46"],
    ],
    zmin=0, zmax=100,
    text=txt, texttemplate="<b>%{text}</b>", textfont=dict(size=10),
    colorbar=dict(title=dict(text="%", side="right"),
                  ticksuffix="%", thickness=12, len=0.85,
                  tickfont=dict(size=9, color="#64748B")),
    hoverongaps=False,
    hovertemplate="<b>%{y}</b><br>%{x}<br><b>%{z:.1f}%</b><extra></extra>",
))
fig_heat.update_layout(
    height=max(220, len(heat_pivot) * 38),
    margin=dict(l=0, r=0, t=28, b=8),
    xaxis=dict(side="top", tickfont=dict(size=11, color="#1E293B"),
               showline=False, showgrid=False),
    yaxis=dict(tickfont=dict(size=10, color="#374151"),
               autorange="reversed", showline=False, showgrid=False),
    font=FONT, **BG,
)
st.plotly_chart(fig_heat, use_container_width=True, config=PCFG)

# ──────────────────────────────────────────────────────────────────────────────
# FILA 4 — Evaluación por Dimensión (ancho completo)
# Este gráfico crece a medida que Ing. Bernarda entrega más dimensiones
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Evaluación por Dimensión</div>', unsafe_allow_html=True)

dim_eis = (
    df.groupby(["DIMENSION_MACRO", "IES ANONIMIZADA"])["RESULTADO"]
    .mean()
    .reset_index()
    .sort_values("IES ANONIMIZADA")
)

fig_dim = go.Figure()
for uni in sorted(dim_eis["IES ANONIMIZADA"].unique()):
    sub = dim_eis[dim_eis["IES ANONIMIZADA"] == uni]
    fig_dim.add_trace(go.Bar(
        name=uni,
        x=sub["DIMENSION_MACRO"],
        y=sub["RESULTADO"],
        marker_color=UNI_COLORS.get(uni, UNI_FALLBACK),
        marker_line_width=0,
        text=sub["RESULTADO"].apply(lambda x: f"{x:.0f}%"),
        textposition="outside", textfont=dict(size=9, color="#374151"),
        cliponaxis=False,
        hovertemplate=f"<b>{uni}</b><br>%{{x}}<br><b>%{{y:.1f}}%</b><extra></extra>",
    ))
fig_dim.update_layout(
    barmode="group",
    height=258,
    margin=dict(l=0, r=10, t=6, b=6),
    yaxis=dict(range=[0, 115], ticksuffix="%", gridcolor=GRID,
               zeroline=False, tickfont=dict(size=10, color="#94A3B8"), showline=False),
    xaxis=dict(tickfont=dict(size=12, color="#1E293B"), showline=False, showgrid=False),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="right", x=1,
        font=dict(size=10, color="#374151"),
        bgcolor="rgba(0,0,0,0)",
    ),
    font=FONT, **BG,
)
st.plotly_chart(fig_dim, use_container_width=True, config=PCFG)

# ──────────────────────────────────────────────────────────────────────────────
# FILA 5 — Tabla: Resultados por Indicador
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Resultados por Indicador</div>', unsafe_allow_html=True)

tc1, tc2 = st.columns([3, 1])
with tc1:
    st.markdown(
        '<p style="color:#374151;font-weight:600;font-size:12px;margin-bottom:3px;">Ordenar por</p>',
        unsafe_allow_html=True,
    )
    orden = st.selectbox(
        "_orden",
        ["Resultado (↓)", "Universidad", "Sub-Dimensión", "Indicador"],
        index=0, label_visibility="collapsed",
    )
with tc2:
    st.markdown(
        '<p style="color:#374151;font-weight:600;font-size:12px;margin-bottom:3px;">Dimensión</p>',
        unsafe_allow_html=True,
    )
    macro_tabla = st.selectbox(
        "_macro",
        ["Todas"] + sorted(df["DIMENSION_MACRO"].unique().tolist()),
        index=0, label_visibility="collapsed",
    )

tabla_df = df.copy()
if macro_tabla != "Todas":
    tabla_df = tabla_df[tabla_df["DIMENSION_MACRO"] == macro_tabla]

tabla_display = pd.DataFrame({
    "Universidad":   tabla_df["IES ANONIMIZADA"],
    "Dimensión":     tabla_df["DIMENSION_MACRO"],
    "Sub-Dimensión": tabla_df["SUBDIMENSIÓN"],
    "Variable":      tabla_df["VARIABLE"],
    "Indicador":     tabla_df["INDICADOR"],
    "Resultado":     tabla_df["RESULTADO"].round(1).astype(str) + "%",
})

if orden == "Universidad":
    tabla_display = tabla_display.sort_values(["Universidad", "Sub-Dimensión", "Indicador"])
elif orden == "Sub-Dimensión":
    tabla_display = tabla_display.sort_values(["Sub-Dimensión", "Universidad"])
elif orden == "Indicador":
    tabla_display = tabla_display.sort_values(["Indicador", "Universidad"])
else:
    tabla_display = tabla_display.sort_values(
        "Resultado", ascending=False,
        key=lambda s: pd.to_numeric(s.str.replace("%", ""), errors="coerce"),
    )

st.dataframe(
    tabla_display,
    use_container_width=True,
    height=240,
    hide_index=True,
    column_config={
        "Universidad":   st.column_config.TextColumn("Universidad",    width="medium"),
        "Dimensión":     st.column_config.TextColumn("Dimensión",      width="small"),
        "Sub-Dimensión": st.column_config.TextColumn("Sub-Dimensión",  width="medium"),
        "Variable":      st.column_config.TextColumn("Variable",       width="large"),
        "Indicador":     st.column_config.TextColumn("Indicador",      width="large"),
        "Resultado":     st.column_config.TextColumn("Resultado",      width="small"),
    },
)
st.caption(
    f"{len(tabla_display)} registros · "
    f"Fuente: {', '.join(df['DIMENSION_MACRO'].unique())} · "
    f"datasetactualv2_2.xlsx"
)

# ──────────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    text-align:center; padding: 12px 0 2px 0; margin-top:10px;
    border-top: 1px solid #E2E8F0;
    color:#94A3B8; font-size:10.5px; font-family:Inter,sans-serif; font-weight:500;">
    Dashboard ETalent &nbsp;·&nbsp; ESPOCH &nbsp;·&nbsp;
    Prácticas Laborales &nbsp;·&nbsp; Jefferson Jordan &nbsp;·&nbsp; 2026
</div>
""", unsafe_allow_html=True)
