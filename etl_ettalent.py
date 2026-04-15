"""
ETL — Dashboard ETalent · ESPOCH
Fuente: datasetactualv2_2.xlsx

Estrategia: leer datos crudos (nivel pregunta) de cada hoja activa,
agregar al nivel de INDICADOR por universidad y exportar a CSV.

Para activar una nueva hoja cuando Ing. Bernarda entregue los datos:
  1. Localizar la hoja en SHEETS_CONFIG
  2. Cambiar 'active': False  →  'active': True
  3. Ajustar 'skiprows' si la hoja tiene filas en blanco antes del header
  4. Volver a ejecutar el script
"""

import os
import pandas as pd

# ── Archivo fuente ────────────────────────────────────────────────────────────
EXCEL_FILE = "datasetactualv2_2.xlsx"

# ── Mapeo de nombres de columna a estándar interno ────────────────────────────
# Cubre variantes con y sin tilde, con espacios, etc.
COLUMN_MAP = {
    "eis":        "IES ANONIMIZADA",
    "dimensión":  "SUBDIMENSIÓN",
    "dimension":  "SUBDIMENSIÓN",
    "variable":   "VARIABLE",
    "indicador":  "INDICADOR",
    "promedio":   "PROMEDIO_RAW",   # escala 0–1; se convierte a 0–100 → RESULTADO
}

# ── Configuración de hojas ────────────────────────────────────────────────────
# active: True  → se procesa
# active: False → estructura lista, esperando datos de Ing. Bernarda
SHEETS_CONFIG = [
    {
        "name":      "d_transparencia",
        "skiprows":  0,        # header en fila 0
        "dimension": "Transparencia",
        "active":    True,
    },
    {
        "name":      "d_participacion",
        "skiprows":  0,
        "dimension": "Participación",
        "active":    False,    # activar cuando se reciban datos completos
    },
    {
        "name":      "d_informacion_academica",
        "skiprows":  2,        # 2 filas en blanco antes del header
        "dimension": "Información Académica",
        "active":    False,
    },
    {
        "name":      "d_comunicación",
        "skiprows":  1,
        "dimension": "Comunicación",
        "active":    False,
    },
    {
        "name":      "d_transformacion digital",
        "skiprows":  1,
        "dimension": "Transf. Digital",
        "active":    False,
    },
    {
        "name":      "d_investigacion",
        "skiprows":  0,
        "dimension": "Investigación",
        "active":    False,
    },
]

# ── Universidades conocidas con nombres reales (para otras hojas futuras) ─────
# Orden alfabético → mapeo determinístico a "UNIVERSIDAD N"
KNOWN_REAL_NAMES = ["EPN", "ESPE", "ESPOCH", "ESPOL", "UCSG", "UNEMI", "UNITA", "UNL", "UTEQ"]


def normalize_eis(series: pd.Series) -> pd.Series:
    """
    Normaliza la columna IES ANONIMIZADA:
    - Elimina espacios dobles y saltos de línea
    - Si encuentra nombres reales, los mapea a 'UNIVERSIDAD N'
    """
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.upper()
    )

    unique_vals = cleaned.dropna().unique()
    real_names_found = [v for v in unique_vals if v in KNOWN_REAL_NAMES]

    if real_names_found:
        anon_map = {
            name: f"UNIVERSIDAD {i + 1}"
            for i, name in enumerate(sorted(real_names_found))
        }
        cleaned = cleaned.map(lambda x: anon_map.get(x, x))
        print(f"    Anonimización aplicada: {anon_map}")

    return cleaned


def load_sheet_raw(file_path: str, config: dict) -> pd.DataFrame:
    """
    Lee una hoja del Excel (datos crudos nivel pregunta),
    normaliza columnas y agrega al nivel INDICADOR.

    Retorna DataFrame con columnas:
      DIMENSION_MACRO, IES ANONIMIZADA, SUBDIMENSIÓN, VARIABLE, INDICADOR, RESULTADO
    """
    raw = pd.read_excel(
        file_path,
        sheet_name=config["name"],
        skiprows=config["skiprows"],
        header=0,
    )

    # Normalizar nombres de columna (strip + lower para matching)
    raw.columns = [str(c).strip() for c in raw.columns]
    rename = {c: COLUMN_MAP[c.lower()] for c in raw.columns if c.lower() in COLUMN_MAP}
    raw.rename(columns=rename, inplace=True)

    # Verificar columnas necesarias
    required = {"IES ANONIMIZADA", "SUBDIMENSIÓN", "VARIABLE", "INDICADOR", "PROMEDIO_RAW"}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"Columnas faltantes en '{config['name']}': {missing}")

    # Convertir PROMEDIO_RAW a numérico (coerce errores de texto como 'cumple')
    raw["PROMEDIO_RAW"] = pd.to_numeric(raw["PROMEDIO_RAW"], errors="coerce")

    # Eliminar filas sin datos clave
    raw.dropna(subset=["IES ANONIMIZADA", "SUBDIMENSIÓN", "VARIABLE",
                        "INDICADOR", "PROMEDIO_RAW"], inplace=True)

    # Normalizar IES (anonimizar si tiene nombres reales)
    raw["IES ANONIMIZADA"] = normalize_eis(raw["IES ANONIMIZADA"])

    # Limpiar texto de sub-dimensión, variable e indicador
    for col in ("SUBDIMENSIÓN", "VARIABLE", "INDICADOR"):
        raw[col] = (
            raw[col].astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

    # Agregar al nivel INDICADOR (promedio de todas las preguntas del indicador)
    agg = (
        raw.groupby(
            ["IES ANONIMIZADA", "SUBDIMENSIÓN", "VARIABLE", "INDICADOR"],
            as_index=False,
        )["PROMEDIO_RAW"]
        .mean()
    )

    # Escala 0–1 → 0–100 y redondear
    agg["RESULTADO"] = (agg["PROMEDIO_RAW"] * 100).round(2)
    agg.drop(columns=["PROMEDIO_RAW"], inplace=True)

    # Agregar columna de dimensión macro al inicio
    agg.insert(0, "DIMENSION_MACRO", config["dimension"])

    return agg.reset_index(drop=True)


def main():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), EXCEL_FILE)

    if not os.path.exists(file_path):
        print(f"[ERROR] No se encontró: {file_path}")
        return

    frames = []
    for cfg in SHEETS_CONFIG:
        if not cfg.get("active", False):
            print(f"Hoja '{cfg['name']}' desactivada (pendiente datos de Ing. Bernarda)")
            continue

        print(f"Procesando: {cfg['name']} ({cfg['dimension']}) ...")
        try:
            df = load_sheet_raw(file_path, cfg)
            frames.append(df)
            print(f"  → {len(df)} registros | {df['IES ANONIMIZADA'].nunique()} universidades")
        except Exception as exc:
            print(f"  [ERROR] {cfg['name']}: {exc}")

    if not frames:
        print("[ERROR] No se procesó ninguna hoja activa.")
        return

    result = pd.concat(frames, ignore_index=True)

    # ── Reporte de verificación ──────────────────────────────────────────────
    print("\n══ Resumen del CSV generado ══")
    print(f"Total registros      : {len(result)}")
    print(f"Dimensiones activas  : {result['DIMENSION_MACRO'].unique().tolist()}")
    print(f"Universidades        : {sorted(result['IES ANONIMIZADA'].unique().tolist())}")
    print(f"Sub-dimensiones      : {result['SUBDIMENSIÓN'].unique().tolist()}")
    print(f"RESULTADO rango      : {result['RESULTADO'].min():.1f}% – {result['RESULTADO'].max():.1f}%")

    print("\nPromedio por universidad (↓):")
    ranking = (
        result.groupby("IES ANONIMIZADA")["RESULTADO"]
        .mean()
        .sort_values(ascending=False)
    )
    for uni, val in ranking.items():
        print(f"  {uni:<22} {val:.1f}%")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_ettalent_clean.csv")
    result.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nCSV exportado → {out_path}")
    print(f"Columnas: {result.columns.tolist()}")


if __name__ == "__main__":
    main()
