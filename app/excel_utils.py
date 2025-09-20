import pandas as pd

def read_excel(path="data/empresas.xlsx"):
    df = pd.read_excel(path)
    if "razon_social" not in df.columns:
        raise ValueError("El Excel debe tener una columna llamada 'razon_social'")
    return df["razon_social"].dropna().tolist()
