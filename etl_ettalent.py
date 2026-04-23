"""
ETL — Dashboard ETalent · ESPOCH
Fuente: dataset_final.xlsx (Hoja3)

Estrategia: leer todos los datos desde una sola hoja que contiene las 6 dimensiones,
agregar al nivel de INDICADOR por universidad y exportar a CSV.
"""

import os
import pandas as pd

# ── Archivo fuente ────────────────────────────────────────────────────────────
EXCEL_FILE = "dataset_final.xlsx"
SHEET_NAME = "Hoja3"

# ── Mapeo de nombres de columna a estándar interno ────────────────────────────
COLUMN_MAP = {
    "eis":        "IES ANONIMIZADA",
    "dimensión":  "SUBDIMENSIÓN",
    "dimension":  "SUBDIMENSIÓN",
    "variable":   "VARIABLE",
    "indicador":  "INDICADOR",
    "promedio":   "PROMEDIO_RAW",   # escala 0–1; se convierte a 0–100 → RESULTADO
}

# ── Mapeo de sub-dimensión → dimensión macro ──────────────────────────────────
DIMENSION_MACRO_MAP = {
    "TRANSPARENCIA ACTIVA":                               "Transparencia",
    "TRANSPARENCIA PASIVA":                               "Transparencia",
    "TRANSPARENCIA FOCALIZADA":                           "Transparencia",
    "TRANSPARENCIA COLABORATIVA":                         "Transparencia",
    "COMUNICACIÓN Y RENDICIÓN DE CUENTAS":                "Comunicación",
    "PARTICIPACIÓN INFORMATIVA":                          "Participación",
    "PARTICIPACIÓN CONSULTIVA":                           "Participación",
    "PARTICIPACIÓN DECISORIA":                            "Participación",
    "INFORMACIÓN ACADÉMICA TRANSPARENCIA":                "Información Académica",
    "INFORMACIÓN ACADÉMICA ACCESIBILIDAD":                "Información Académica",
    "INFORMACIÓN ACADÉMICA SERVICIO AL ESTUDIANTE":       "Información Académica",
    "INFORMACIÓN ACADÉMICA ACTUALIZACION DE INFORMACIÓN":  "Información Académica",
    "INFORMACIÓN ACADÉMICA ACTUALIZACIÓN DE INFORMACIÓN":  "Información Académica",
    "INFORMACIÓN ACADÉMICA DIFUSIÓN DE RESULTADOS":       "Información Académica",
    "INVESTIGACIÓN":                                      "Investigación",
    "TRANSFORMACIÓN DIGITAL":                             "Transf. Digital",
}


def normalize_eis(series: pd.Series) -> pd.Series:
    """Normaliza la columna IES: elimina espacios extra y estandariza mayúsculas."""
    return (
        series.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.upper()
    )


def main():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), EXCEL_FILE)

    if not os.path.exists(file_path):
        print(f"[ERROR] No se encontró: {file_path}")
        return

    print(f"Leyendo '{EXCEL_FILE}' — hoja '{SHEET_NAME}' ...")
    raw = pd.read_excel(file_path, sheet_name=SHEET_NAME, header=0)
    print(f"  -> {len(raw)} filas crudas, {raw.shape[1]} columnas")

    # Normalizar nombres de columna (strip + lower — elimina el espacio en "promedio ")
    raw.columns = raw.columns.str.strip().str.lower()
    rename = {c: COLUMN_MAP[c] for c in raw.columns if c in COLUMN_MAP}
    raw.rename(columns=rename, inplace=True)

    # Verificar columnas necesarias
    required = {"IES ANONIMIZADA", "SUBDIMENSIÓN", "VARIABLE", "INDICADOR", "PROMEDIO_RAW"}
    missing = required - set(raw.columns)
    if missing:
        print(f"[ERROR] Columnas faltantes: {missing}")
        print(f"  Columnas encontradas: {raw.columns.tolist()}")
        return

    # Convertir PROMEDIO_RAW a numérico
    raw["PROMEDIO_RAW"] = pd.to_numeric(raw["PROMEDIO_RAW"], errors="coerce")

    # Eliminar filas sin datos clave
    raw.dropna(subset=["IES ANONIMIZADA", "SUBDIMENSIÓN", "VARIABLE",
                        "INDICADOR", "PROMEDIO_RAW"], inplace=True)

    # Normalizar texto de columnas clave
    raw["IES ANONIMIZADA"] = normalize_eis(raw["IES ANONIMIZADA"])
    for col in ("SUBDIMENSIÓN", "VARIABLE", "INDICADOR"):
        raw[col] = (
            raw[col].astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .str.upper()
        )

    # Agregar al nivel INDICADOR (promedio de todas las preguntas del indicador)
    df = (
        raw.groupby(
            ["IES ANONIMIZADA", "SUBDIMENSIÓN", "VARIABLE", "INDICADOR"],
            as_index=False,
        )["PROMEDIO_RAW"]
        .mean()
    )

    # Escala 0–1 → 0–100
    df["RESULTADO"] = (df["PROMEDIO_RAW"] * 100).round(2)
    df.drop(columns=["PROMEDIO_RAW"], inplace=True)

    # Derivar DIMENSION_MACRO desde SUBDIMENSIÓN
    df["DIMENSION_MACRO"] = df["SUBDIMENSIÓN"].map(DIMENSION_MACRO_MAP)

    # Advertir sobre sub-dimensiones sin mapeo
    sin_mapeo = df[df["DIMENSION_MACRO"].isna()]["SUBDIMENSIÓN"].unique()
    if len(sin_mapeo) > 0:
        print(f"[ADVERTENCIA] Sub-dimensiones sin mapeo (se excluirán): {sin_mapeo.tolist()}")

    df.dropna(subset=["DIMENSION_MACRO", "IES ANONIMIZADA", "RESULTADO"], inplace=True)

    # Reordenar columnas al formato esperado por el dashboard
    df = df[["DIMENSION_MACRO", "IES ANONIMIZADA", "SUBDIMENSIÓN", "VARIABLE", "INDICADOR", "RESULTADO"]]
    df.reset_index(drop=True, inplace=True)

    # ── Reporte de verificación ──────────────────────────────────────────────
    print("\n== Resumen del CSV generado ==")
    print(f"Total registros      : {len(df)}")
    print(f"Dimensiones macro    : {sorted(df['DIMENSION_MACRO'].unique().tolist())}")
    print(f"Sub-dimensiones      : {df['SUBDIMENSIÓN'].nunique()}")
    print(f"Universidades        : {sorted(df['IES ANONIMIZADA'].unique().tolist())}")
    print(f"Indicadores únicos   : {df['INDICADOR'].nunique()}")
    print(f"RESULTADO rango      : {df['RESULTADO'].min():.1f}% – {df['RESULTADO'].max():.1f}%")

    print("\nPromedio por universidad (desc):")
    ranking = (
        df.groupby("IES ANONIMIZADA")["RESULTADO"]
        .mean()
        .sort_values(ascending=False)
    )
    for uni, val in ranking.items():
        print(f"  {uni:<22} {val:.1f}%")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_ettalent_clean.csv")
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nCSV exportado -> {out_path}")


if __name__ == "__main__":
    main()
