"""
ETL — Dashboard ETalent · ESPOCH
Fuente de datos: datset actual.xlsx

Estrategia: leer la tabla resumen pre-agregada y anonimizada de cada hoja.

Estructura esperada por hoja (tabla resumen a la derecha de los datos crudos):
  Columnas: IES | IES ANONIMIZADA | DIMENSIÓN | PUNTAJE MÁXIMO |
            AUTOEVALUACIÓN (FORMS) | % AUTOEVALUACIÓN (FORMS) |
            % AUTOEVALUACIÓN TOTAL | VERIFICACIÓN (ESPOCH) |
            %EVALUACIÓN | PROMEDIO | %PROMEDIO TOTAL DIMENSIÓN
  - 4 filas por universidad (una por sub-dimensión)
  - Celdas combinadas en IES, IES ANONIMIZADA, % AUTOEVALUACIÓN TOTAL,
    PROMEDIO y %PROMEDIO TOTAL DIMENSIÓN → se resuelven con forward-fill

Para agregar una nueva hoja cuando Ing. Bernarda entregue los datos:
  1. Añadir una entrada a SHEETS_CONFIG indicando nombre de hoja,
     fila de encabezado, columna de inicio y número de filas de datos.
  2. Volver a ejecutar el script. El CSV se actualizará automáticamente.
"""

import os
import pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE HOJAS
# Cada entrada define:
#   name       → nombre exacto de la hoja en el Excel
#   header_row → fila (índice 0) que contiene los encabezados de la tabla resumen
#   col_start  → columna (índice 0) donde empieza "IES" en la tabla resumen
#   n_rows     → número de filas de datos (universidades × sub-dimensiones)
#   dimension  → etiqueta de dimensión macro para identificar el origen
# ──────────────────────────────────────────────────────────────────────────────
SHEETS_CONFIG = [
    {
        "name":       "d_transparencia",
        "header_row": 9,    # fila 10 en Excel (índice 0 base)
        "col_start":  11,   # columna L (índice 0 base)
        "n_rows":     28,   # 7 universidades × 4 sub-dimensiones
        "dimension":  "Transparencia",
    },
    # Cuando lleguen las demás hojas evaluadas, agregar aquí:
    # {
    #     "name":       "d_participacion",
    #     "header_row": ...,
    #     "col_start":  ...,
    #     "n_rows":     ...,
    #     "dimension":  "Participación",
    # },
    # {
    #     "name":       "d_informacion_academica",
    #     "header_row": ...,
    #     "col_start":  ...,
    #     "n_rows":     ...,
    #     "dimension":  "Información Académica",
    # },
]

# Número de columnas de la tabla resumen (L a V = 11 columnas)
N_COLS = 11

# Columnas que solo aparecen en la primera fila de cada universidad
# (celdas combinadas en Excel) y deben propagarse hacia abajo
UNIVERSITY_LEVEL_COLS = [
    "% AUTOEVALUACIÓN TOTAL",
    "PROMEDIO",
    "%PROMEDIO TOTAL DIMENSIÓN",
]

# Columnas numéricas
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


def load_sheet_summary(file_path: str, config: dict) -> pd.DataFrame:
    """
    Lee la tabla resumen pre-agregada de una hoja del Excel y la devuelve
    como DataFrame limpio.
    """
    raw = pd.read_excel(file_path, sheet_name=config["name"], header=None)

    hr = config["header_row"]
    cs = config["col_start"]
    ce = cs + N_COLS

    # Extraer y limpiar nombres de columna
    headers = [str(h).strip() for h in raw.iloc[hr, cs:ce].tolist()]

    # Extraer filas de datos
    df = raw.iloc[hr + 1 : hr + 1 + config["n_rows"], cs:ce].copy()
    df.columns = headers
    df = df.reset_index(drop=True)

    # Forward-fill identificadores (celdas combinadas en Excel)
    df["IES"] = df["IES"].ffill()
    df["IES ANONIMIZADA"] = (
        df["IES ANONIMIZADA"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)  # colapsar dobles espacios
        .replace("nan", pd.NA)
        .ffill()
    )

    # Convertir columnas numéricas
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Forward-fill agregados de universidad (solo en fila T.ACTIVA por las celdas combinadas)
    for col in UNIVERSITY_LEVEL_COLS:
        if col in df.columns:
            df[col] = df.groupby("IES")[col].transform("first")

    # Normalizar texto de sub-dimensión
    df["DIMENSIÓN"] = (
        df["DIMENSIÓN"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    )

    # Eliminar filas vacías o sin sub-dimensión válida
    df = df[df["DIMENSIÓN"].notna() & (df["DIMENSIÓN"] != "nan")].copy()

    # Agregar columna de dimensión macro (útil cuando haya múltiples hojas)
    df.insert(0, "DIMENSION_MACRO", config["dimension"])

    return df.reset_index(drop=True)


def main():
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "datset actual.xlsx"
    )

    if not os.path.exists(file_path):
        print(f"[ERROR] No se encontró el archivo: {file_path}")
        return

    frames = []
    for cfg in SHEETS_CONFIG:
        print(f"Procesando: {cfg['name']} ({cfg['dimension']}) ...")
        try:
            df = load_sheet_summary(file_path, cfg)
            frames.append(df)
            print(f"  → {len(df)} filas | {df['IES ANONIMIZADA'].nunique()} universidades")
        except Exception as exc:
            print(f"  [ERROR] {cfg['name']}: {exc}")

    if not frames:
        print("[ERROR] No se procesó ninguna hoja.")
        return

    result = pd.concat(frames, ignore_index=True)

    # ── Reporte de verificación ─────────────────────────────────────────────
    print("\n══ Resumen del CSV generado ══")
    print(f"Total filas          : {len(result)}")
    print(f"Dimensiones macro    : {result['DIMENSION_MACRO'].unique().tolist()}")
    print(f"Universidades        : {sorted(result['IES ANONIMIZADA'].unique().tolist())}")
    print(f"Sub-dimensiones      : {result['DIMENSIÓN'].unique().tolist()}")
    print("\n%PROMEDIO TOTAL DIMENSIÓN por universidad (ordenado ↓):")
    kpi = (
        result.groupby("IES ANONIMIZADA")["%PROMEDIO TOTAL DIMENSIÓN"]
        .first()
        .sort_values(ascending=False)
    )
    for uni, val in kpi.items():
        print(f"  {uni:<22} {val:.2f}%")

    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "dataset_ettalent_clean.csv"
    )
    result.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nCSV exportado → {out_path}")
    print(f"Columnas: {result.columns.tolist()}")


if __name__ == "__main__":
    main()
