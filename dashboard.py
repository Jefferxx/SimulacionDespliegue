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

EIS_COLORS = {
    "ESPOL":  "#1863dc",
    "UNL":    "#00897b",
    "EPN":    "#7b1fa2",
    "UTEQ":   "#f57c00",
    "ESPOCH": "#bc0712",
    "UNEMI":  "#455a64",
    "ESPE":   "#2e7d32",
}

CUMPL_COLORS = {
    "Cumple":              C_GREEN,
    "Cumple Parcialmente": C_ORANGE,
    "No Cumple":           C_RED,
}

# ──────────────────────────────────────────────────────────────
# ESTILOS GLOBALES
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;600;700;800&display=swap');

html, body, * { font-family: 'Roboto', sans-serif !important; }

/* Ocultar elementos Streamlit no deseados */
[data-testid="stHeader"]           { display: none !important; }
[data-testid="stToolbar"]          { display: none !important; }
/* Ocultar botón de colapso → sidebar siempre visible */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"]   { display: none !important; }
footer                             { display: none !important; }

/* Sidebar con identidad ESPOCH */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #8b0000 0%, #bc0712 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: white !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.25) !important; }

/* Etiquetas de filtro */
[data-testid="stSidebar"] label {
    color: rgba(255,255,255,0.85) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
}
/* Tags seleccionados en multiselect */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: rgba(255,255,255,0.2) !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span { color: white !important; }
/* Input box del multiselect */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.12) !important;
    border-color: rgba(255,255,255,0.3) !important;
}
/* Texto dentro del input */
[data-testid="stSidebar"] input { color: white !important; }

/* Fondo general */
[data-testid="stAppViewContainer"] { background: #f2f2f2; }
div.block-container { padding: 0 !important; max-width: 100% !important; }

/* KPI cards */
.kpi-box {
    background: white;
    border-radius: 8px;
    padding: 16px 18px 14px 18px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.09);
    height: 100%;
}
.kpi-lbl {
    font-size: 9px; font-weight: 700; color: #9ca3af;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;
}
.kpi-val  { font-size: 30px; font-weight: 800; line-height: 1; margin: 0; }
.kpi-sub  { font-size: 11px; color: #6b7280; margin-top: 5px; }

/* Título de sección */
.sec-title {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: #1a1a1a; margin: 0 0 14px 0;
    padding-left: 8px; border-left: 3px solid #bc0712;
}

/* Tarjeta blanca */
.card {
    background: white; border-radius: 10px;
    padding: 20px 22px; box-shadow: 0 1px 6px rgba(0,0,0,0.07);
}

/* Tabla criticos — cabecera */
.tbl-header {
    background: #8b0000; color: white; padding: 12px 22px;
    border-radius: 10px 10px 0 0;
    font-size: 11px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
}

/* Leyenda donut */
.legend-row {
    display: flex; align-items: center; gap: 8px;
    margin: 5px 0; font-size: 12px;
}
.legend-sq {
    width: 11px; height: 11px; border-radius: 2px; flex-shrink: 0;
}

/* Tabla de indicadores críticos — fondo blanco garantizado */
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
    # Filtrar EIS válidas
    EIS_VALIDAS = {"ESPOL", "UNL", "EPN", "UTEQ", "ESPOCH", "UNEMI", "ESPE"}
    df = df[df["EIS"].isin(EIS_VALIDAS)].copy()
    return df

df_raw = load_data(CSV_PATH)

# ──────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background: linear-gradient(90deg, {C_RED_DARK} 0%, {C_RED} 100%);
            padding: 14px 28px;
            display: flex; justify-content: space-between; align-items: center;">
  <div style="color:white; font-size:17px; font-weight:700; letter-spacing:-0.2px;">
    ETalent &nbsp;&middot;&nbsp; Evaluacion de Transparencia Institucional
  </div>
  <div style="color:rgba(255,255,255,0.78); font-size:9px; font-weight:600;
              letter-spacing:1px; text-transform:uppercase; text-align:right;">
    Dashboard ETalent &nbsp;&middot;&nbsp; ESPOCH &nbsp;&middot;&nbsp;
    Practicas Laborales &nbsp;&middot;&nbsp; Jefferson Jordan 2026
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SIDEBAR — FILTROS (menú lateral izquierdo)
# ──────────────────────────────────────────────────────────────
eis_opts  = sorted(df_raw["EIS"].unique())
hoja_opts = sorted(df_raw["HOJA"].unique())
dim_opts  = sorted(df_raw["DIMENSION"].unique())

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px 0 16px 0;">
        <div style="font-size:20px; font-weight:800; color:white;
                    letter-spacing:-0.5px;">ETalent</div>
        <div style="font-size:9px; color:rgba(255,255,255,0.7);
                    letter-spacing:1px; text-transform:uppercase; margin-top:4px;">
            Evaluacion de Transparencia
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:10px; font-weight:700; color:rgba(255,255,255,0.6);
                text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">
        Filtros
    </div>
    """, unsafe_allow_html=True)

    sel_eis  = st.multiselect("Universidad (EIS)",  eis_opts,  default=eis_opts,  key="f_eis")
    sel_hoja = st.multiselect("Dimension Principal",hoja_opts, default=hoja_opts, key="f_hoja")
    sel_dim  = st.multiselect("Sub-Dimension",      dim_opts,  default=dim_opts,  key="f_dim")

    st.markdown("---")

    # Indicador de estado de filtros
    n_active = sum([
        len(sel_eis)  < len(eis_opts),
        len(sel_hoja) < len(hoja_opts),
        len(sel_dim)  < len(dim_opts),
    ])
    filtro_txt = "PERSONALIZADO" if n_active else "GENERAL"
    filtro_col = "rgba(255,255,255,0.5)" if not n_active else "white"
    st.markdown(f"""
    <div style="font-size:9px; color:{filtro_col}; text-transform:uppercase;
                letter-spacing:0.8px; font-weight:600;">
        Filtros activos: {filtro_txt}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:9px; color:rgba(255,255,255,0.55); line-height:1.7;">
        <b style="color:rgba(255,255,255,0.8);">Proyecto:</b> ETalent — ESPOCH<br>
        <b style="color:rgba(255,255,255,0.8);">Universidades:</b> {len(eis_opts)}<br>
        <b style="color:rgba(255,255,255,0.8);">Dimensiones:</b> {len(hoja_opts)}<br>
        <b style="color:rgba(255,255,255,0.8);">Sub-dimensiones:</b> {len(dim_opts)}
    </div>
    """, unsafe_allow_html=True)

# ── Guardia: si vacío, restaurar selección completa
if not sel_eis:   sel_eis   = eis_opts
if not sel_hoja:  sel_hoja  = hoja_opts
if not sel_dim:   sel_dim   = dim_opts

# ── Aplicar filtros
df = df_raw[
    df_raw["EIS"].isin(sel_eis) &
    df_raw["HOJA"].isin(sel_hoja) &
    df_raw["DIMENSION"].isin(sel_dim)
].copy()

if df.empty:
    st.error("La combinacion de filtros no tiene datos. Ajusta los filtros en la barra superior.")
    st.stop()

# ──────────────────────────────────────────────────────────────
# PRE-CÁLCULOS GLOBALES
# ──────────────────────────────────────────────────────────────
KEY_COLS = ["EIS", "HOJA", "DIMENSION", "VARIABLE", "INDICADOR"]

# Agregar a nivel de indicador único (evita duplicados por criterio)
ind_agg = (
    df.groupby(KEY_COLS, as_index=False)["PROMEDIO"].mean()
)
ind_agg["CUMPLIMIENTO"] = pd.cut(
    ind_agg["PROMEDIO"],
    bins=[-0.01, 0.499, 0.749, 1.01],
    labels=["No Cumple", "Cumple Parcialmente", "Cumple"],
)

total_indicadores = len(ind_agg)
cumpl_counts = ind_agg["CUMPLIMIENTO"].value_counts()
cumple_n      = cumpl_counts.get("Cumple", 0)
parcial_n     = cumpl_counts.get("Cumple Parcialmente", 0)
no_cumple_n   = cumpl_counts.get("No Cumple", 0)
cumple_pct    = cumple_n    / total_indicadores * 100
no_cumple_pct = no_cumple_n / total_indicadores * 100

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
    font=dict(family="Roboto, sans-serif", size=12, color=C_DARK),
)

# ──────────────────────────────────────────────────────────────
# CONTENIDO PRINCIPAL
# ──────────────────────────────────────────────────────────────
st.markdown('<div style="padding: 20px 28px 0 28px;">', unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5, gap="small")

def kpi(col, label, val, sub, color):
    with col:
        st.markdown(f"""
        <div class="kpi-box" style="border-top:3px solid {color};">
            <div class="kpi-lbl">{label}</div>
            <div class="kpi-val" style="color:{color};">{val}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

kpi(k1, "PROMEDIO GLOBAL",       f"{prom_global:.1f}%",    "promedio de cumplimiento",          C_RED)
kpi(k2, "MAYOR CUMPLIMIENTO",    mejor_eis,                f"{mejor_val:.1f}% promedio",         C_GREEN)
kpi(k3, "MENOR CUMPLIMIENTO",    peor_eis,                 f"{peor_val:.1f}% promedio",          C_RED)
kpi(k4, "INDICADORES CUMPLIDOS", f"{cumple_pct:.1f}%",     f"{cumple_n} / {total_indicadores} indicadores", C_BLUE)
kpi(k5, "NO CUMPLE",             f"{no_cumple_pct:.1f}%",  f"{no_cumple_n} / {total_indicadores} indicadores", C_ORANGE)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── FILA 2: Ranking + Radar ────────────────────────────────────
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
        textfont=dict(size=12, color=C_DARK),
    ))
    fig_bar.add_vline(
        x=70, line_dash="dot", line_color=C_GREEN, line_width=1.5,
        annotation_text="META 70%",
        annotation_position="top right",
        annotation_font=dict(color=C_GREEN, size=9, family="Roboto"),
    )
    fig_bar.update_layout(
        **BASE_LAYOUT,
        height=310,
        margin=dict(l=0, r=65, t=20, b=10),
        xaxis=dict(
            range=[0, 115], showgrid=True, gridcolor="#f0f0f0",
            zeroline=False, ticksuffix="%",
            tickfont=dict(size=10, color=C_DARK),
        ),
        yaxis=dict(showgrid=False, tickfont=dict(size=13, color=C_DARK)),
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True, config=PCFG)
    st.markdown('</div>', unsafe_allow_html=True)

with c_radar:
    st.markdown('<div class="sec-title">Perfil por Dimension</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)

    radar_df = (df.groupby("HOJA")["PROMEDIO"].mean() * 100).reset_index()
    cats = radar_df["HOJA"].tolist()
    vals = radar_df["PROMEDIO"].tolist()
    # Cerrar polígono
    cats_c = cats + [cats[0]]
    vals_c = vals + [vals[0]]

    fig_radar = go.Figure(go.Scatterpolar(
        r=vals_c, theta=cats_c,
        fill="toself",
        fillcolor="rgba(188,7,18,0.12)",
        line=dict(color=C_RED, width=2),
        marker=dict(size=5, color=C_RED),
    ))
    fig_radar.update_layout(
        **BASE_LAYOUT,
        height=310,
        margin=dict(l=50, r=50, t=30, b=30),
        polar=dict(
            bgcolor=C_WHITE,
            radialaxis=dict(
                visible=True, range=[0, 100], tickformat=".0f",
                tickfont=dict(size=8, color=C_GRAY), gridcolor=C_BORDER,
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color=C_DARK), gridcolor=C_BORDER,
            ),
        ),
        showlegend=False,
    )
    st.plotly_chart(fig_radar, use_container_width=True, config=PCFG)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── FILA 3: Heatmap ───────────────────────────────────────────
st.markdown('<div class="sec-title">Mapa de Calor · Universidad por Sub-Dimension</div>',
            unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

# EIS como filas, DIMENSION como columnas
heat_df    = df.groupby(["EIS", "DIMENSION"])["PROMEDIO"].mean().reset_index()
heat_pivot = heat_df.pivot(index="EIS", columns="DIMENSION", values="PROMEDIO") * 100

# Ordenar EIS igual que el ranking (mayor a menor)
eis_order = eis_prom.sort_values(ascending=False).index.tolist()
heat_pivot = heat_pivot.reindex([e for e in eis_order if e in heat_pivot.index])

# Manejar NaN (combinaciones sin datos)
heat_vals = heat_pivot.values
heat_text = np.vectorize(
    lambda v: "N/D" if np.isnan(v) else f"{int(round(v))}%"
)(heat_vals)

fig_heat = go.Figure(go.Heatmap(
    z=heat_vals,
    x=heat_pivot.columns.tolist(),
    y=heat_pivot.index.tolist(),
    colorscale=[
        [0.00, "#ffcdd2"], [0.33, "#ef9a9a"],
        [0.34, "#fff9c4"], [0.66, "#fff59d"],
        [0.67, "#c8e6c9"], [1.00, "#388e3c"],
    ],
    zmin=0, zmax=100,
    text=heat_text,
    texttemplate="%{text}",
    textfont=dict(size=9, color=C_DARK),
    colorbar=dict(
        ticksuffix="%", thickness=12, len=0.9,
        tickfont=dict(size=9, color=C_DARK),
        title=dict(text="", side="right"),
    ),
    hoverongaps=False,
    xgap=2, ygap=2,
))
fig_heat.update_layout(
    **BASE_LAYOUT,
    height=max(260, len(heat_pivot) * 42),
    margin=dict(l=0, r=60, t=40, b=10),
    xaxis=dict(
        side="top",
        tickfont=dict(size=9, color=C_RED),
        tickangle=-35,
    ),
    yaxis=dict(
        tickfont=dict(size=11, color=C_DARK),
        autorange="reversed",
    ),
)
st.plotly_chart(fig_heat, use_container_width=True, config=PCFG)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── FILA 4: Barras agrupadas + Donut ──────────────────────────
c_bars, c_donut = st.columns([3, 2], gap="medium")

with c_bars:
    st.markdown('<div class="sec-title">Comparativa por Dimension y Universidad</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)

    grp = (df.groupby(["HOJA", "EIS"])["PROMEDIO"].mean() * 100).reset_index()
    grp.columns = ["HOJA", "EIS", "PCT"]

    fig_grp = go.Figure()
    for eis in sorted(grp["EIS"].unique()):
        sub = grp[grp["EIS"] == eis]
        fig_grp.add_trace(go.Bar(
            name=eis,
            x=sub["HOJA"], y=sub["PCT"],
            marker_color=EIS_COLORS.get(eis, C_GRAY),
        ))
    fig_grp.update_layout(
        **BASE_LAYOUT,
        barmode="group", height=330,
        margin=dict(l=0, r=10, t=10, b=90),
        yaxis=dict(
            range=[0, 115], ticksuffix="%", gridcolor="#f0f0f0",
            zeroline=False, tickfont=dict(size=10, color=C_DARK),
        ),
        xaxis=dict(
            tickangle=0,
            tickfont=dict(size=9, color=C_DARK),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.4,
            xanchor="center", x=0.5,
            font=dict(size=10, color=C_DARK),
        ),
    )
    st.plotly_chart(fig_grp, use_container_width=True, config=PCFG)
    st.markdown('</div>', unsafe_allow_html=True)

with c_donut:
    st.markdown('<div class="sec-title">Distribucion de Cumplimiento</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)

    d_labels = cumpl_counts.index.tolist()
    d_values = cumpl_counts.values.tolist()
    d_colors = [CUMPL_COLORS.get(l, C_GRAY) for l in d_labels]

    fig_donut = go.Figure(go.Pie(
        labels=d_labels, values=d_values,
        hole=0.60,
        marker=dict(colors=d_colors, line=dict(color=C_WHITE, width=2)),
        textinfo="none",
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    ))
    fig_donut.add_annotation(
        text=(f"<b style='font-size:20px'>{total_indicadores}</b>"
              f"<br><span style='font-size:11px;color:{C_GRAY}'>indicadores</span>"),
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color=C_DARK), align="center",
    )
    fig_donut.update_layout(
        **BASE_LAYOUT,
        height=260,
        margin=dict(l=20, r=20, t=10, b=10),
        showlegend=False,
    )
    st.plotly_chart(fig_donut, use_container_width=True, config=PCFG)

    # Leyenda personalizada con texto siempre visible
    for lbl, val, color in zip(d_labels, d_values, d_colors):
        pct = val / total_indicadores * 100 if total_indicadores else 0
        st.markdown(f"""
        <div class="legend-row">
            <div class="legend-sq" style="background:{color};"></div>
            <span style="color:{C_DARK};">{lbl}</span>
            <span style="color:{C_GRAY}; margin-left:auto;">
                {val} ({pct:.0f}%)
            </span>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── FILA 5: Tabla de indicadores críticos ─────────────────────
st.markdown(f"""
<div class="tbl-header">
    Indicadores Criticos &nbsp;&middot;&nbsp; Promedio por debajo del 50%
</div>""", unsafe_allow_html=True)

# Controles encima de la tabla
tc_space, tc_ord, tc_n = st.columns([4, 2, 1], gap="small")

with tc_ord:
    st.markdown(
        f'<p style="color:{C_DARK};font-weight:600;font-size:12px;'
        f'margin:8px 0 2px 0;">Ordenar por</p>',
        unsafe_allow_html=True,
    )
    ORDEN_OPTS = ["Promedio", "Universidad", "Sub-Dimension", "Criterios fallidos"]
    orden = st.selectbox("_ord", ORDEN_OPTS, index=0, label_visibility="collapsed")

with tc_n:
    st.markdown(
        f'<p style="color:{C_DARK};font-weight:600;font-size:12px;'
        f'margin:8px 0 2px 0;">Top N</p>',
        unsafe_allow_html=True,
    )
    top_n = int(max(5, min(200, st.number_input(
        "_topn", min_value=5, max_value=200, value=30, step=5,
        label_visibility="collapsed",
    ))))

# Validar orden contra lista permitida (no confiar en el cliente)
if orden not in ORDEN_OPTS:
    orden = "Promedio"

# Construir tabla de críticos
crit_agg = df.groupby(KEY_COLS, as_index=False).agg(
    PROMEDIO   =("PROMEDIO", "mean"),
    N_CRITERIOS=("PROMEDIO", "count"),
    N_FALLIDOS =("PROMEDIO", lambda s: (s < 0.5).sum()),
)

UMBRAL = 0.5
criticos = (
    crit_agg[crit_agg["PROMEDIO"] < UMBRAL]
    .sort_values(["PROMEDIO", "EIS"])
    .reset_index(drop=True)
)

# Aplicar orden seleccionado
if   orden == "Universidad":        criticos = criticos.sort_values(["EIS", "PROMEDIO"])
elif orden == "Sub-Dimension":      criticos = criticos.sort_values(["DIMENSION", "PROMEDIO"])
elif orden == "Criterios fallidos": criticos = criticos.sort_values("N_FALLIDOS", ascending=False)
# "Promedio" -> ya ordenado por default

criticos = criticos.head(top_n)

def estado_label(p: float) -> str:
    if p == 0.0:   return "Sin cumplimiento"
    if p < 0.25:   return "Critico"
    return "En riesgo"

if criticos.empty:
    st.info("No hay indicadores criticos con los filtros actuales.")
else:
    tabla = pd.DataFrame({
        "Universidad":   criticos["EIS"],
        "Dimension":     criticos["HOJA"],
        "Sub-Dimension": criticos["DIMENSION"],
        "Variable":      criticos["VARIABLE"],
        "Indicador":     criticos["INDICADOR"],
        "Promedio":      (criticos["PROMEDIO"] * 100).round(1).astype(str) + "%",
        "Brecha":        criticos["PROMEDIO"].apply(
                             lambda p: f"-{(UMBRAL - p) * 100:.1f} pp"
                         ),
        "Criterios":     criticos["N_CRITERIOS"].astype(str),
        "Fallidos":      criticos["N_FALLIDOS"].astype(str),
        "Estado":        criticos["PROMEDIO"].apply(estado_label),
    })

    st.dataframe(
        tabla,
        use_container_width=True,
        height=300,
        hide_index=True,
        column_config={
            "Promedio":     st.column_config.TextColumn(width="small"),
            "Brecha":       st.column_config.TextColumn("Brecha",   width="small"),
            "Criterios":    st.column_config.TextColumn("Criterios",width="small"),
            "Fallidos":     st.column_config.TextColumn("Fallidos", width="small"),
            "Estado":       st.column_config.TextColumn(width="medium"),
        },
    )
    st.caption(
        f"Mostrando {len(tabla)} indicadores unicos con promedio "
        f"< {int(UMBRAL * 100)}%"
    )

st.markdown("</div>", unsafe_allow_html=True)  # cierre padding principal

# ──────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{C_DARK}; padding:14px 28px; margin-top:24px;
            display:flex; justify-content:space-between; align-items:center;">
    <div style="color:{C_RED}; font-style:italic; font-size:12px;">
        Hacemos historia
    </div>
    <div style="color:#9e9e9e; font-size:10px; text-align:center;">
        Dashboard ETalent &nbsp;&middot;&nbsp; ESPOCH &nbsp;&middot;&nbsp;
        Practicas Laborales &nbsp;&middot;&nbsp; Jefferson Jordan 2026
    </div>
    <div style="color:#9e9e9e; font-size:10px;">
        2026 Escuela Superior Politecnica de Chimborazo
    </div>
</div>
""", unsafe_allow_html=True)
