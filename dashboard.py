import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ──────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard ETalent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# ESTILOS GLOBALES
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Fondo general */
[data-testid="stAppViewContainer"] { background-color: #EEF2F7; }
[data-testid="stHeader"] { background: transparent; }
div.block-container { padding: 0.8rem 2rem 1rem 2rem; }

/* Sidebar */
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

/* KPI cards */
.kpi-box {
    background: white;
    border-radius: 14px;
    padding: 18px 16px 14px 16px;
    text-align: center;
    box-shadow: 0 2px 14px rgba(0,0,0,0.07);
}
.kpi-value { font-size: 30px; font-weight: 800; margin: 0; line-height: 1; }
.kpi-label { font-size: 11px; color: #6B7280; margin-top: 6px;
             text-transform: uppercase; letter-spacing: 0.6px; font-weight: 600; }
.kpi-sub   { font-size: 11px; color: #9CA3AF; margin-top: 2px; }

/* Encabezado de sección */
.sec-title {
    font-size: 12px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.9px; color: #374151;
    margin: 12px 0 4px 0; padding-left: 9px;
    border-left: 3px solid #2563EB;
}

/* Tarjeta blanca para gráficos */
.card {
    background: white; border-radius: 14px;
    padding: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# CARGA DE DATOS
# ──────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_ettalent_clean.csv")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["PROMEDIO", "PUNTAJE_1", "PUNTAJE_2"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=["EIS", "PROMEDIO"], inplace=True)
    df["CUMPLIMIENTO"] = pd.cut(
        df["PROMEDIO"],
        bins=[-0.01, 0.499, 0.749, 1.01],
        labels=["No Cumple", "Cumple Parcialmente", "Cumple"],
    )
    return df

df_raw = load_data(CSV_PATH)

# ──────────────────────────────────────────────────────────────
# SIDEBAR — FILTROS
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ETalent")
    st.markdown("**Evaluación de Transparencia Institucional**")
    st.markdown("---")
    st.markdown("### Filtros")

    eis_opts  = sorted(df_raw["EIS"].unique())
    hoja_opts = sorted(df_raw["HOJA"].unique())
    dim_opts  = sorted(df_raw["DIMENSION"].unique())

    sel_eis  = st.multiselect("Universidad (EIS)", eis_opts,  default=eis_opts)
    sel_hoja = st.multiselect("Dimensión principal", hoja_opts, default=hoja_opts)
    sel_dim  = st.multiselect("Sub-dimensión", dim_opts, default=dim_opts)

    # Guardia: si el usuario desmarca todo, restaurar selección completa
    if not sel_eis:
        st.warning("Selecciona al menos una universidad.")
        sel_eis = eis_opts
    if not sel_hoja:
        st.warning("Selecciona al menos una dimensión.")
        sel_hoja = hoja_opts
    if not sel_dim:
        st.warning("Selecciona al menos una sub-dimensión.")
        sel_dim = dim_opts

    st.markdown("---")
    st.markdown("**Proyecto:** ETalent — ESPOCH")
    st.markdown(f"**Universidades:** {len(eis_opts)}")
    st.markdown(f"**Dimensiones:** {len(hoja_opts)}")
    st.markdown(f"**Sub-dimensiones:** {len(dim_opts)}")

# ──────────────────────────────────────────────────────────────
# APLICAR FILTROS
# ──────────────────────────────────────────────────────────────
df = df_raw[
    df_raw["EIS"].isin(sel_eis) &
    df_raw["HOJA"].isin(sel_hoja) &
    df_raw["DIMENSION"].isin(sel_dim)
].copy()

# Guardia global: si los filtros devuelven vacío, detener renderizado
if df.empty:
    st.error("La combinación de filtros seleccionada no tiene datos. Ajusta los filtros.")
    st.stop()

# ──────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #0F172A 0%, #1D4ED8 60%, #06B6D4 100%);
    border-radius: 16px; padding: 22px 32px; margin-bottom: 18px; color: white;">
  <h1 style="margin:0; font-size:24px; font-weight:800; letter-spacing:-0.3px;">
      🎓 Dashboard ETalent · Transparencia Institucional
  </h1>
  <p style="margin:6px 0 0 0; opacity:0.75; font-size:13px;">
      ESPOCH · 7 Universidades Ecuatorianas · 6 Dimensiones · ~1 600 Indicadores
  </p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# KPIs
# ──────────────────────────────────────────────────────────────
prom_global   = df["PROMEDIO"].mean() * 100
total_ind     = len(df)
cumple_pct    = (df["CUMPLIMIENTO"] == "Cumple").mean() * 100
no_cumple_pct = (df["CUMPLIMIENTO"] == "No Cumple").mean() * 100

eis_prom  = df.groupby("EIS")["PROMEDIO"].mean() * 100
mejor_eis = eis_prom.idxmax() if len(eis_prom) else "—"
peor_eis  = eis_prom.idxmin() if len(eis_prom) else "—"
mejor_val = eis_prom.max() if len(eis_prom) else 0
peor_val  = eis_prom.min() if len(eis_prom) else 0

k1, k2, k3, k4, k5 = st.columns(5)

kpis = [
    (k1, f"{prom_global:.1f}%",   "Promedio Global",        "de cumplimiento",          "#2563EB"),
    (k2, mejor_eis,               "Mayor Cumplimiento",     f"{mejor_val:.1f}% promedio","#10B981"),
    (k3, peor_eis,                "Menor Cumplimiento",     f"{peor_val:.1f}% promedio", "#EF4444"),
    (k4, f"{cumple_pct:.1f}%",    "Indicadores Cumplidos",  f"{total_ind:,} evaluados",  "#8B5CF6"),
    (k5, f"{no_cumple_pct:.1f}%", "No Cumplen",             "requieren atención",        "#F59E0B"),
]

for col, val, label, sub, color in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-box" style="border-top: 4px solid {color};">
            <div class="kpi-value" style="color:{color};">{val}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# FILA 2: Ranking EIS  +  Radar por dimensión
# ──────────────────────────────────────────────────────────────
COLORES_EIS = {
    "EPN":    "#3B82F6",
    "ESPE":   "#10B981",
    "ESPOCH": "#8B5CF6",
    "ESPOL":  "#F59E0B",
    "UNEMI":  "#EF4444",
    "UNL":    "#06B6D4",
    "UTEQ":   "#EC4899",
}
COLORES_CUMPL = {
    "Cumple":               "#10B981",
    "Cumple Parcialmente":  "#F59E0B",
    "No Cumple":            "#EF4444",
}

col_l, col_r = st.columns([3, 2], gap="medium")

with col_l:
    st.markdown('<div class="sec-title">Ranking de Universidades por Promedio de Cumplimiento</div>',
                unsafe_allow_html=True)
    bar_df = (df.groupby("EIS")["PROMEDIO"].mean() * 100).reset_index().sort_values("PROMEDIO")
    bar_df.columns = ["EIS", "PCT"]
    bar_df["COLOR"] = bar_df["PCT"].apply(
        lambda x: "#10B981" if x >= 70 else ("#F59E0B" if x >= 50 else "#EF4444")
    )
    fig_bar = go.Figure(go.Bar(
        x=bar_df["PCT"], y=bar_df["EIS"],
        orientation="h",
        marker_color=bar_df["COLOR"],
        text=bar_df["PCT"].apply(lambda x: f"  {x:.1f}%"),
        textposition="outside",
        cliponaxis=False,
    ))
    fig_bar.add_vline(x=70, line_dash="dot", line_color="#10B981",
                      annotation_text="Meta 70%", annotation_position="top right",
                      annotation_font_color="#10B981")
    fig_bar.update_layout(
        height=310, margin=dict(l=0, r=50, t=10, b=10),
        xaxis=dict(range=[0, 112], showgrid=True, gridcolor="#F3F4F6",
                   zeroline=False, ticksuffix="%", title="",
                   tickfont=dict(size=11, color="#1F2937")),
        yaxis=dict(showgrid=False, tickfont=dict(size=13, color="#1F2937")),
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter, system-ui, sans-serif", size=12, color="#1F2937"),
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_r:
    st.markdown('<div class="sec-title">Perfil Global por Dimensión Principal</div>',
                unsafe_allow_html=True)
    radar_df = (df.groupby("HOJA")["PROMEDIO"].mean() * 100).reset_index()
    cats   = radar_df["HOJA"].tolist()
    vals   = radar_df["PROMEDIO"].tolist()
    cats  += [cats[0]]
    vals  += [vals[0]]

    fig_radar = go.Figure(go.Scatterpolar(
        r=vals, theta=cats,
        fill="toself",
        fillcolor="rgba(37,99,235,0.12)",
        line=dict(color="#2563EB", width=2.5),
        marker=dict(size=7, color="#2563EB"),
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="white",
            radialaxis=dict(visible=True, range=[0, 100],
                            tickformat=".0f", ticksuffix="%",
                            tickfont=dict(size=9), gridcolor="#E5E7EB"),
            angularaxis=dict(tickfont=dict(size=10, color="#374151"),
                             gridcolor="#E5E7EB"),
        ),
        height=310, margin=dict(l=50, r=50, t=20, b=20),
        paper_bgcolor="white", showlegend=False,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# FILA 3: Heatmap EIS × DIMENSION
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Mapa de Calor — Cumplimiento por Universidad y Sub-Dimensión</div>',
            unsafe_allow_html=True)

heat_df    = df.groupby(["EIS", "DIMENSION"])["PROMEDIO"].mean().reset_index()
heat_pivot = heat_df.pivot(index="DIMENSION", columns="EIS", values="PROMEDIO") * 100

# Ordenar filas por promedio descendente
heat_pivot = heat_pivot.loc[heat_pivot.mean(axis=1).sort_values(ascending=True).index]

fig_heat = go.Figure(go.Heatmap(
    z=heat_pivot.values,
    x=heat_pivot.columns.tolist(),
    y=heat_pivot.index.tolist(),
    colorscale=[
        [0.00, "#FEE2E2"], [0.25, "#EF4444"],
        [0.50, "#FEF3C7"], [0.75, "#10B981"],
        [1.00, "#064E3B"],
    ],
    zmin=0, zmax=100,
    text=np.round(heat_pivot.values, 1),
    texttemplate="<b>%{text}%</b>",
    textfont=dict(size=10, color="white"),
    colorbar=dict(
        title=dict(text="Promedio %", side="right"),
        ticksuffix="%", thickness=14, len=0.9,
    ),
    hoverongaps=False,
))
fig_heat.update_layout(
    height=max(320, len(heat_pivot) * 28),
    margin=dict(l=0, r=0, t=30, b=10),
    paper_bgcolor="white", plot_bgcolor="white",
    xaxis=dict(side="top", tickfont=dict(size=12, color="#1F2937")),
    yaxis=dict(tickfont=dict(size=10, color="#374151"), autorange="reversed"),
    font=dict(family="Inter, system-ui, sans-serif"),
)
st.plotly_chart(fig_heat, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# FILA 4: Barras agrupadas por HOJA  +  Donut cumplimiento
# ──────────────────────────────────────────────────────────────
col_m, col_d = st.columns([3, 2], gap="medium")

with col_m:
    st.markdown('<div class="sec-title">Comparativa por Dimensión y Universidad</div>',
                unsafe_allow_html=True)
    stacked = (df.groupby(["HOJA", "EIS"])["PROMEDIO"].mean() * 100).reset_index()
    stacked.columns = ["HOJA", "EIS", "PCT"]

    fig_grp = go.Figure()
    for eis in sorted(stacked["EIS"].unique()):
        sub = stacked[stacked["EIS"] == eis]
        fig_grp.add_trace(go.Bar(
            name=eis,
            x=sub["HOJA"], y=sub["PCT"],
            marker_color=COLORES_EIS.get(eis, "#6B7280"),
            text=sub["PCT"].apply(lambda x: f"{x:.0f}"),
            textposition="outside",
            cliponaxis=False,
        ))
    fig_grp.update_layout(
        barmode="group", height=330,
        margin=dict(l=0, r=10, t=10, b=70),
        paper_bgcolor="white", plot_bgcolor="white",
        yaxis=dict(range=[0, 118], ticksuffix="%",
                   gridcolor="#F3F4F6", zeroline=False,
                   tickfont=dict(size=10, color="#1F2937")),
        xaxis=dict(tickangle=-25, tickfont=dict(size=10, color="#1F2937")),
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    xanchor="right", x=1, font=dict(size=10, color="#1F2937")),
        font=dict(family="Inter, system-ui, sans-serif", size=11, color="#1F2937"),
    )
    st.plotly_chart(fig_grp, use_container_width=True)

with col_d:
    st.markdown('<div class="sec-title">Distribución Global de Cumplimiento</div>',
                unsafe_allow_html=True)
    cumpl_counts = df["CUMPLIMIENTO"].value_counts()
    labels  = cumpl_counts.index.tolist()
    values  = cumpl_counts.values.tolist()
    colors  = [COLORES_CUMPL.get(l, "#9CA3AF") for l in labels]

    fig_donut = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.58,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#1F2937"),
        pull=[0.03 if l == "No Cumple" else 0 for l in labels],
    ))
    fig_donut.add_annotation(
        text=f"<b>{total_ind:,}</b><br><span style='font-size:10px'>indicadores</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=13, color="#1F2937"), align="center",
    )
    fig_donut.update_layout(
        height=330, margin=dict(l=10, r=10, t=10, b=30),
        paper_bgcolor="white", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.12,
                    xanchor="center", x=0.5,
                    font=dict(size=11, color="#1F2937")),
        font=dict(family="Inter, system-ui, sans-serif", color="#1F2937"),
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ──────────────────────────────────────────────────────────────
# FILA 5: Indicadores críticos
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Indicadores Críticos — Promedio por debajo del 50 %</div>',
            unsafe_allow_html=True)

KEY_COLS = ["EIS", "HOJA", "DIMENSION", "VARIABLE", "INDICADOR"]

# Agrupar: cada indicador tiene múltiples criterios en el CSV → promediar
agg = df.groupby(KEY_COLS, as_index=False).agg(
    PROMEDIO=("PROMEDIO", "mean"),
    N_CRITERIOS=("PROMEDIO", "count"),
    N_FALLIDOS=("PROMEDIO", lambda s: (s < 0.5).sum()),
)

criticos_raw = agg[agg["PROMEDIO"] < 0.5].sort_values(["PROMEDIO", "EIS"]).reset_index(drop=True)

# ── controles de la tabla ──────────────────────────────────────
UMBRAL = 0.5   # fijo en 50 %

criticos_raw = agg[agg["PROMEDIO"] < UMBRAL].sort_values(["PROMEDIO", "EIS"]).reset_index(drop=True)

st.markdown("""
<style>
/* Hace visible el texto de los controles de la tabla críticos */
.crit-ctrl label, .crit-ctrl .stSelectbox label,
.crit-ctrl .stNumberInput label { color: #1F2937 !important; font-weight: 600; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

fc2, fc3 = st.columns([3, 1])
with fc2:
    st.markdown('<p style="color:#1F2937;font-weight:600;font-size:13px;margin-bottom:4px;">Ordenar por</p>',
                unsafe_allow_html=True)
    ORDEN_OPTS = ["Promedio", "Universidad", "Sub-Dimensión", "Criterios fallidos"]
    orden = st.selectbox("_orden", ORDEN_OPTS, index=0, label_visibility="collapsed")

with fc3:
    st.markdown('<p style="color:#1F2937;font-weight:600;font-size:13px;margin-bottom:4px;">Mostrar top N</p>',
                unsafe_allow_html=True)
    top_n = st.number_input("_topn", min_value=5, max_value=200, value=30, step=5,
                            label_visibility="collapsed")

# Defensa: clamp top_n por si acaso, y validar orden contra lista permitida
top_n = int(max(5, min(200, top_n)))
if orden not in ORDEN_OPTS:
    orden = "Promedio"

# Aplicar orden
if orden == "Universidad":
    criticos_raw = criticos_raw.sort_values(["EIS", "PROMEDIO"])
elif orden == "Sub-Dimensión":
    criticos_raw = criticos_raw.sort_values(["DIMENSION", "PROMEDIO"])
elif orden == "Criterios fallidos":
    criticos_raw = criticos_raw.sort_values("N_FALLIDOS", ascending=False)
# "Promedio" ya viene ordenado por default (sort_values PROMEDIO, EIS)

criticos_raw = criticos_raw.head(top_n)

if criticos_raw.empty:
    st.success("No hay indicadores críticos con los filtros actuales.")
else:
    # Columna de semáforo según severidad
    def semaforo(p):
        if p == 0:
            return "Sin cumplimiento"
        elif p < 0.25:
            return "Crítico"
        else:
            return "En riesgo"

    # Columna de brecha: cuánto falta para alcanzar el umbral
    def brecha(p, u):
        gap = (u - p) * 100
        return f"−{gap:.1f} pp"

    criticos_display = pd.DataFrame({
        "Estado":         criticos_raw["PROMEDIO"].apply(lambda p: semaforo(p)),
        "Universidad":    criticos_raw["EIS"],
        "Dimensión":      criticos_raw["HOJA"],
        "Sub-Dimensión":  criticos_raw["DIMENSION"],
        "Variable":       criticos_raw["VARIABLE"],
        "Indicador":      criticos_raw["INDICADOR"],
        "Promedio":       (criticos_raw["PROMEDIO"] * 100).round(1).astype(str) + "%",
        "Brecha":         criticos_raw.apply(lambda r: brecha(r["PROMEDIO"], UMBRAL), axis=1),
        "Criterios":      criticos_raw["N_CRITERIOS"].astype(str),
        "Fallidos":       criticos_raw["N_FALLIDOS"].astype(str),
    })

    st.dataframe(
        criticos_display,
        use_container_width=True,
        height=300,
        hide_index=True,
        column_config={
            "Estado":    st.column_config.TextColumn("Estado", width="medium"),
            "Promedio":  st.column_config.TextColumn("Promedio", width="small"),
            "Brecha":    st.column_config.TextColumn("Brecha al umbral", width="small",
                             help="Puntos porcentuales que faltan para alcanzar el umbral"),
            "Criterios": st.column_config.TextColumn("# Criterios", width="small"),
            "Fallidos":  st.column_config.TextColumn("# Fallidos", width="small"),
        },
    )
    st.caption(f"Mostrando {len(criticos_display)} indicadores únicos con promedio < {int(UMBRAL*100)}%")

# ──────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 18px 0 4px 0;
            color:#9CA3AF; font-size:11px; border-top: 1px solid #E5E7EB; margin-top:16px;">
    Dashboard ETalent · ESPOCH · Prácticas Laborales · Jefferson Jordan 2026
</div>
""", unsafe_allow_html=True)
