import pandas as pd

def read_excel(path="data/empresas.xlsx", column_name=None):
    """
    Lee datos desde un archivo Excel.
    
    Args:
        path: Ruta al archivo Excel
        column_name: Nombre específico de la columna a leer. Si es None, usa la primera columna.
    
    Returns:
        Lista de valores de la columna especificada
    """
    df = pd.read_excel(path)
    
    if column_name:
        if column_name not in df.columns:
            raise ValueError(f"El Excel debe tener una columna llamada '{column_name}'. Columnas disponibles: {list(df.columns)}")
        return df[column_name].dropna().astype(str).tolist()
    else:
        # Si no se especifica columna, usar la primera
        if df.empty:
            raise ValueError("El archivo Excel está vacío")
        
        first_column = df.columns[0]
        return df[first_column].dropna().astype(str).tolist()

def read_excel_multiple_columns(path="data/empresas.xlsx"):
    """
    Lee todas las columnas de un archivo Excel para análisis de estructura.
    
    Returns:
        DataFrame completo y lista de nombres de columnas
    """
    df = pd.read_excel(path)
    return df, list(df.columns)
