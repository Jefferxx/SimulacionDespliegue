import pandas as pd
import numpy as np
import os

def clean_column_name(col):
    col = str(col).strip().upper()
    # Mapeo de nombres para estandarizar
    mapping = {
        'EIS': 'EIS',
        'DIMENSIÓN': 'DIMENSION',
        'DIMENSION': 'DIMENSION',
        'VARIABLE': 'VARIABLE',
        'INDICADOR': 'INDICADOR',
        'PREGUNTA': 'PREGUNTA',
        'PUNTAJE': 'PUNTAJE_1',
        'PUNTAJE 1': 'PUNTAJE_1',
        'PUNTAJE_1': 'PUNTAJE_1',
        'PUNTAJE 2': 'PUNTAJE_2',
        'PUNTAJE_2': 'PUNTAJE_2',
        'PROMEDIO': 'PROMEDIO'
    }
    return mapping.get(col, col)

def process_sheet(file_path, sheet_name, skiprows):
    print(f"Procesando hoja: {sheet_name}...")
    
    # Cargar la hoja
    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skiprows)
    
    # Limpiar nombres de columnas y manejar duplicados
    new_columns = []
    seen = set()
    for col in df.columns:
        clean_col = clean_column_name(col)
        # Si ya hemos visto este nombre de columna (limpio), le añadimos un sufijo
        if clean_col in seen:
            new_columns.append(f"{clean_col}_DUP")
        else:
            new_columns.append(clean_col)
            seen.add(clean_col)
    
    df.columns = new_columns
    
    # Seleccionar solo las columnas necesarias (incluyendo PREGUNTA para granularidad profunda)
    cols_to_keep = ['EIS', 'DIMENSION', 'VARIABLE', 'INDICADOR', 'PREGUNTA', 'PUNTAJE_1', 'PUNTAJE_2']
    
    existing_cols = [c for c in cols_to_keep if c in df.columns]
    df = df[existing_cols].copy()
    
    # Eliminar filas donde EIS sea nulo
    df = df.dropna(subset=['EIS'])
    
    # Limpiar EIS (Strip + Uppercase)
    df['EIS'] = df['EIS'].astype(str).str.strip().str.upper()
    
    # Filtrar ruidos comunes
    df = df[df['EIS'] != 'EIS']
    
    # Limpiar DIMENSION y VARIABLE (Strip + Title case)
    if 'DIMENSION' in df.columns:
        df['DIMENSION'] = df['DIMENSION'].astype(str).str.strip().str.title()
    if 'VARIABLE' in df.columns:
        df['VARIABLE'] = df['VARIABLE'].astype(str).str.strip().str.title()
        
    # Convertir puntajes a numérico
    for col in ['PUNTAJE_1', 'PUNTAJE_2']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = 0 # Asegurar que existe la columna
            
    # Calcular PROMEDIO igual que la fórmula del Excel
    df['PUNTAJE_2'] = df['PUNTAJE_2'].fillna(0)
    df['PUNTAJE_1'] = df['PUNTAJE_1'].fillna(0)
    df['PROMEDIO'] = (df['PUNTAJE_1'] + df['PUNTAJE_2']) / 2
    
    # Agregar columna HOJA
    sheet_clean_name = sheet_name.replace('d_', '').replace('_', ' ').title()
    df['HOJA'] = sheet_clean_name

    # --- NUEVO: Agregación de Datos (Resolviendo granularidad de PREGUNTA) ---
    # Agrupamos por los niveles jerárquicos y calculamos el promedio
    group_cols = ['EIS', 'HOJA', 'DIMENSION', 'VARIABLE', 'INDICADOR']
    df = df.groupby(group_cols).mean(numeric_only=True).reset_index()
    
    # Reordenar columnas para consistencia
    final_cols = ['EIS', 'HOJA', 'DIMENSION', 'VARIABLE', 'INDICADOR', 'PUNTAJE_1', 'PUNTAJE_2', 'PROMEDIO']
    df = df.reindex(columns=final_cols)
    
    # Eliminar filas donde PROMEDIO sea NaN
    df = df.dropna(subset=['PROMEDIO'])
    
    return df

def main():
    file_path = 'datset actual.xlsx'
    if not os.path.exists(file_path):
        print(f"Error: No se encuentra el archivo {file_path}")
        return

    sheets_config = [
        {'name': 'd_transparencia', 'skip': 0},
        {'name': 'd_participacion', 'skip': 0},
        {'name': 'd_informacion_academica', 'skip': 2},
        {'name': 'd_comunicación', 'skip': 1},
        {'name': 'd_transformacion digital', 'skip': 1},
        {'name': 'd_investigacion', 'skip': 0}
    ]
    
    all_data = []
    
    for config in sheets_config:
        try:
            df_sheet = process_sheet(file_path, config['name'], config['skip'])
            all_data.append(df_sheet)
        except Exception as e:
            print(f"Error procesando {config['name']}: {e}")
            
    if not all_data:
        print("No se pudo procesar ninguna hoja.")
        return
        
    # Concatenar todo
    final_df = pd.concat(all_data, ignore_index=True)

    # --- CORRECCIÓN: Filtrado Estricto de EIS Válidas ---
    # Algunas hojas traen "UNIVERSIDAD 1, 2, ..." como ruido o placeholders.
    # Solo procesaremos las 7 oficiales.
    EIS_OFICIALES = ["ESPOL", "UNL", "EPN", "UTEQ", "ESPOCH", "UNEMI", "ESPE"]
    
    # Asegurar limpieza de nombres antes de filtrar
    final_df['EIS'] = final_df['EIS'].astype(str).str.strip().str.upper()
    final_df = final_df[final_df['EIS'].isin(EIS_OFICIALES)].copy()

    # --- NUEVO: Anonimización Dinámica ---
    # Ordenamos para asegurar que Universidad 1 sea siempre la misma
    real_eis = sorted(final_df['EIS'].unique())
    anonymization_map = {name: f"Universidad {i+1}" for i, name in enumerate(real_eis)}
    
    print("\n--- MAPA DE ANONIMIZACIÓN (PURGADO) ---")
    for real, anon in anonymization_map.items():
        print(f"{real} -> {anon}")
    print("-----------------------------\n")
    
    final_df['EIS'] = final_df['EIS'].map(anonymization_map)
    
    # Exportar a CSV
    output_file = 'dataset_ettalent_clean.csv'
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nArchivo guardado exitosamente: {output_file}")
    print(f"Total de registros limpios: {len(final_df)}")

if __name__ == "__main__":
    main()
