from bs4 import BeautifulSoup
from .data_formatter import clean_and_format_data, apply_field_mapping

def parse_resultado(html: str) -> dict:
    """
    Parsea el HTML de resultado de SUNAT y devuelve datos limpios y formateados.
    Maneja tanto la vista de lista de resultados como la vista directa de RUC.
    """
    soup = BeautifulSoup(html, "lxml")
    
    # Verificar si es la vista directa de resultado (búsqueda por RUC)
    panel = soup.select_one(".panel.panel-primary")
    if panel and "Resultado de la Búsqueda" in panel.get_text():
        return parse_direct_result(panel)
    
    # Si no es vista directa, usar el parser original
    panel = soup.select_one(".panel.panel-primary")
    if not panel:
        return {"error": "No se encontró información"}

    data = {}
    for item in panel.select(".list-group-item"):
        label = item.select_one(".col-sm-5, .col-sm-3")
        value = item.select_one(".col-sm-7, .col-sm-3:nth-of-type(2)")
        if label and value:
            key = label.get_text(strip=True).replace(":", "")
            val = value.get_text(" ", strip=True)
            data[key] = val

    # Limpiar y formatear los datos
    cleaned_data = clean_and_format_data(data)
    
    # Aplicar mapeo de campos estandarizados
    formatted_data = apply_field_mapping(cleaned_data)
    
    return formatted_data

def parse_direct_result(panel) -> dict:
    """
    Parsea la vista directa de resultados (búsqueda por RUC)
    """
    data = {}
    
    for item in panel.select(".list-group-item"):
        # Buscar el label (título del campo)
        label_elem = item.select_one(".col-sm-5 .list-group-item-heading, .col-sm-3 .list-group-item-heading")
        if not label_elem:
            continue
            
        label = label_elem.get_text(strip=True).replace(":", "")
        
        # Buscar el valor correspondiente
        value_elem = None
        
        # Primero intentar encontrar texto directo
        value_elem = (item.select_one(".col-sm-7 .list-group-item-text") or 
                     item.select_one(".col-sm-7 .list-group-item-heading") or
                     item.select_one(".col-sm-3:last-child .list-group-item-text"))
        
        if value_elem:
            value = value_elem.get_text(" ", strip=True)
        else:
            # Si no hay texto directo, buscar tablas
            table = item.select_one(".col-sm-7 table, .col-sm-3:last-child table")
            if table:
                rows = table.select("tr")
                if len(rows) == 1:
                    # Una sola fila, tomar su contenido
                    value = rows[0].get_text(" ", strip=True)
                else:
                    # Múltiples filas, concatenar
                    value = " | ".join([row.get_text(" ", strip=True) for row in rows if row.get_text(strip=True)])
            else:
                # Último recurso: tomar todo el texto del contenedor de valor
                value_container = item.select_one(".col-sm-7, .col-sm-3:last-child")
                if value_container:
                    value = value_container.get_text(" ", strip=True)
                else:
                    value = ""
        
        if label and value:
            data[label] = value
    
    # Limpiar y formatear los datos
    cleaned_data = clean_and_format_data(data)
    
    # Aplicar mapeo de campos estandarizados
    formatted_data = apply_field_mapping(cleaned_data)
    
    return formatted_data
