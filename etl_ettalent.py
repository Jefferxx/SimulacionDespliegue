"""
ETL — Dashboard ETalent · ESPOCH
Fuente: dataset_final.xlsx

Produce dos CSV:
  dataset_ettalent_clean.csv   — 42 filas (7 unis x 6 dims), nivel dimension desde Hoja1
                                  Usado por: KPIs, Ranking, Evaluacion por Dimension
  dataset_ettalent_detail.csv  — ~518 filas, nivel indicador desde Hoja3
                                  Usado por: Radar, Heatmap, Tabla
"""

import os
import pandas as pd

EXCEL_FILE = "dataset_final.xlsx"

# Mapeo Hoja3: SUBDIMENSION en mayusculas → DIMENSION_MACRO
HOJA3_SUBDIM_MAP = {
    "TRANSPARENCIA ACTIVA":                               "Transparencia",
    "TRANSPARENCIA PASIVA":                               "Transparencia",
    "TRANSPARENCIA FOCALIZADA":                           "Transparencia",
    "TRANSPARENCIA COLABORATIVA":                         "Transparencia",
    "COMUNICACIÓN Y RENDICIÓN DE CUENTAS":                "Comunicación",
    "COMUNICACION Y RENDICION DE CUENTAS":                "Comunicación",
    "PARTICIPACIÓN INFORMATIVA":                          "Participación",
    "PARTICIPACION INFORMATIVA":                          "Participación",
    "PARTICIPACIÓN CONSULTIVA":                           "Participación",
    "PARTICIPACION CONSULTIVA":                           "Participación",
    "PARTICIPACIÓN DECISORIA":                            "Participación",
    "PARTICIPACION DECISORIA":                            "Participación",
    "INFORMACIÓN ACADÉMICA TRANSPARENCIA":                "Información Académica",
    "INFORMACION ACADEMICA TRANSPARENCIA":                "Información Académica",
    "INFORMACIÓN ACADÉMICA ACCESIBILIDAD":                "Información Académica",
    "INFORMACION ACADEMICA ACCESIBILIDAD":                "Información Académica",
    "INFORMACIÓN ACADÉMICA SERVICIO AL ESTUDIANTE":       "Información Académica",
    "INFORMACION ACADEMICA SERVICIO AL ESTUDIANTE":       "Información Académica",
    "INFORMACIÓN ACADÉMICA ACTUALIZACION DE INFORMACIÓN": "Información Académica",
    "INFORMACIÓN ACADÉMICA ACTUALIZACIÓN DE INFORMACIÓN": "Información Académica",
    "INFORMACION ACADEMICA ACTUALIZACION DE INFORMACION": "Información Académica",
    "INFORMACIÓN ACADÉMICA DIFUSIÓN DE RESULTADOS":       "Información Académica",
    "INFORMACION ACADEMICA DIFUSION DE RESULTADOS":       "Información Académica",
    "INVESTIGACIÓN":                                      "Investigación",
    "INVESTIGACION":                                      "Investigación",
    "TRANSFORMACIÓN DIGITAL":                             "Transf. Digital",
    "TRANSFORMACION DIGITAL":                             "Transf. Digital",
}


def map_dimension_macro_hoja1(dim_str: str) -> str:
    """Mapea valores abreviados de Hoja1 (col DIMENSION) a DIMENSION_MACRO."""
    s = str(dim_str).strip().upper().replace("\n", " ").replace("  ", " ")
    if s.startswith("T.") or "TRANSPARENCIA" in s:
        return "Transparencia"
    if s.startswith("P.") or "PARTICIPAC" in s:
        return "Participación"
    if s.startswith("I.") or "INFORMAC" in s:
        return "Información Académica"
    if "COMUNICAC" in s or "RENDIC" in s:
        return "Comunicación"
    if "TRANSFORMAC" in s or "DIGITAL" in s:
        return "Transf. Digital"
    if "INVESTIGAC" in s:
        return "Investigación"
    return None


def extract_hoja1_summary(excel_path: str) -> pd.DataFrame:
    """
    Lee Hoja1 en formato raw (sin header) y extrae 42 filas dimension-nivel:
    7 universidades x 6 dimensiones, RESULTADO = %PROMEDIO DIMENSION de Hoja1.
    """
    raw = pd.read_excel(excel_path, sheet_name="Hoja1", header=None)

    # Estructura esperada: 11 columnas (indices 0-10)
    # col 0: IES (nombre real)  col 1: IES ANONIMIZADA  col 2: DIMENSION abrev
    # col 10: %PROMEDIO DIMENSION (solo en la primera sub-dim de cada bloque por universidad)
    if raw.shape[1] < 11:
        raise ValueError(f"Hoja1 tiene menos columnas de las esperadas ({raw.shape[1]} vs 11)")

    col_prom = pd.to_numeric(raw.iloc[:, 10], errors="coerce")

    # Filas con %PROMEDIO DIMENSION valido Y con "UNIVERSIDAD" en col 1
    col1_str = raw.iloc[:, 1].astype(str).str.strip().str.upper()
    valid_mask = col_prom.notna() & col1_str.str.contains("UNIVERSIDAD", na=False)

    valid = raw[valid_mask].copy()
    valid["IES ANONIMIZADA"] = (
        valid.iloc[:, 1].astype(str).str.strip()
        .str.upper().str.replace(r"\s+", " ", regex=True)
    )
    valid["RESULTADO"] = pd.to_numeric(valid.iloc[:, 10], errors="coerce").round(2)
    valid["DIMENSION_MACRO"] = valid.iloc[:, 2].apply(map_dimension_macro_hoja1)

    df = (
        valid[["DIMENSION_MACRO", "IES ANONIMIZADA", "RESULTADO"]]
        .dropna()
        .reset_index(drop=True)
    )
    return df


def extract_hoja3_detail(excel_path: str) -> pd.DataFrame:
    """
    Lee Hoja3 y extrae datos a nivel indicador (~518 filas).
    RESULTADO = promedio (0-1) * 100.
    """
    raw = pd.read_excel(excel_path, sheet_name="Hoja3", header=0)
    raw.columns = raw.columns.str.strip().str.lower()

    raw = raw.rename(columns={
        "eis":       "IES ANONIMIZADA",
        "dimensión": "SUBDIMENSIÓN",
        "dimension": "SUBDIMENSIÓN",
        "variable":  "VARIABLE",
        "indicador": "INDICADOR",
        "promedio":  "PROMEDIO_RAW",
    })

    raw["PROMEDIO_RAW"] = pd.to_numeric(raw["PROMEDIO_RAW"], errors="coerce")
    raw.dropna(subset=["IES ANONIMIZADA", "SUBDIMENSIÓN", "VARIABLE",
                        "INDICADOR", "PROMEDIO_RAW"], inplace=True)

    for col in ("IES ANONIMIZADA", "SUBDIMENSIÓN", "VARIABLE", "INDICADOR"):
        raw[col] = (
            raw[col].astype(str).str.strip()
            .str.upper().str.replace(r"\s+", " ", regex=True)
        )

    df = (
        raw.groupby(
            ["IES ANONIMIZADA", "SUBDIMENSIÓN", "VARIABLE", "INDICADOR"],
            as_index=False,
        )["PROMEDIO_RAW"].mean()
    )

    df["RESULTADO"] = (df["PROMEDIO_RAW"] * 100).round(2)
    df.drop(columns=["PROMEDIO_RAW"], inplace=True)

    df["DIMENSION_MACRO"] = df["SUBDIMENSIÓN"].map(HOJA3_SUBDIM_MAP)

    unmapped = df[df["DIMENSION_MACRO"].isna()]["SUBDIMENSIÓN"].unique()
    if len(unmapped) > 0:
        print(f"[ADVERTENCIA] Subdimensiones sin mapeo (se excluiran): {unmapped.tolist()}")

    df.dropna(subset=["DIMENSION_MACRO"], inplace=True)
    df = df[["DIMENSION_MACRO", "IES ANONIMIZADA", "SUBDIMENSIÓN",
              "VARIABLE", "INDICADOR", "RESULTADO"]].reset_index(drop=True)
    return df


def main():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), EXCEL_FILE)

    if not os.path.exists(file_path):
        print(f"[ERROR] No se encontro: {file_path}")
        return

    # === CSV 1: resumen dimension-nivel desde Hoja1 ===
    print(f"Procesando Hoja1 (resumen por dimension)...")
    df_summary = extract_hoja1_summary(file_path)
    print(f"  -> {len(df_summary)} registros (esperado: 42)")
    print(f"  Dimensiones: {sorted(df_summary['DIMENSION_MACRO'].unique())}")
    print(f"  Universidades: {sorted(df_summary['IES ANONIMIZADA'].unique())}")

    print("\n== Ranking global (valores oficiales Hoja1) ==")
    ranking = (
        df_summary.groupby("IES ANONIMIZADA")["RESULTADO"]
        .mean()
        .sort_values(ascending=False)
    )
    for uni, val in ranking.items():
        print(f"  {uni:<22} {val:.1f}%")

    print(f"\nPromedio global: {df_summary['RESULTADO'].mean():.1f}%")
    print(f"RESULTADO rango: {df_summary['RESULTADO'].min():.1f}% - {df_summary['RESULTADO'].max():.1f}%")

    out_dir = os.path.dirname(file_path)
    summary_path = os.path.join(out_dir, "dataset_ettalent_clean.csv")
    df_summary.to_csv(summary_path, index=False, encoding="utf-8-sig")
    print(f"\nCSV resumen -> {summary_path}")

    # === CSV 2: detalle indicador-nivel desde Hoja3 ===
    print("\nProcesando Hoja3 (detalle por indicador)...")
    df_detail = extract_hoja3_detail(file_path)
    print(f"  -> {len(df_detail)} registros")
    print(f"  Subdimensiones: {df_detail['SUBDIMENSION'].nunique() if 'SUBDIMENSION' in df_detail.columns else df_detail['SUBDIMENSIÓN'].nunique()}")
    print(f"  Indicadores unicos: {df_detail['INDICADOR'].nunique()}")

    detail_path = os.path.join(out_dir, "dataset_ettalent_detail.csv")
    df_detail.to_csv(detail_path, index=False, encoding="utf-8-sig")
    print(f"CSV detalle -> {detail_path}")


if __name__ == "__main__":
    main()
