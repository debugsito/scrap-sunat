import re
from typing import Dict, Any

def clean_and_format_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Limpia y formatea los datos extraídos de SUNAT.
    Convierte las claves a snake_case y limpia los valores.
    """
    if not isinstance(data, dict):
        return data
    
    cleaned_data = {}
    
    for key, value in data.items():
        # Convertir clave a snake_case
        clean_key = convert_to_snake_case(key)
        
        # Limpiar valor
        clean_value = clean_value_text(value) if isinstance(value, str) else value
        
        cleaned_data[clean_key] = clean_value
    
    return cleaned_data

def convert_to_snake_case(text: str) -> str:
    """
    Convierte texto a snake_case.
    """
    # Reemplazar caracteres especiales y espacios
    text = re.sub(r'[^\w\s]', '', text)
    
    # Reemplazar espacios múltiples con uno solo
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Convertir a snake_case
    text = text.lower().replace(' ', '_')
    
    # Limpiar underscores múltiples
    text = re.sub(r'_+', '_', text)
    
    # Remover underscores al inicio y final
    text = text.strip('_')
    
    return text

def clean_value_text(text: str) -> str:
    """
    Limpia el texto de valores, removiendo espacios extra, tabs, etc.
    """
    if not text or text == '-' or text == 'NINGUNO':
        return None
    
    # Remover tabs, saltos de línea y espacios extra
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Casos especiales según el contenido
    if 'RUC' in text and '-' in text:
        # Limpiar formato de RUC
        return format_ruc_field(text)
    
    if 'DNI' in text and '-' in text:
        # Limpiar formato de DNI
        return format_dni_field(text)
    
    if text.startswith('Principal') and '-' in text:
        # Limpiar actividades económicas
        return format_economic_activity(text)
    
    if 'AFILIADO DESDE' in text.upper() or 'desde' in text.lower():
        # Limpiar fechas con "desde"
        return format_date_field(text)
    
    # Convertir fechas simples
    if re.match(r'^\d{2}/\d{2}/\d{4}$', text):
        return text
    
    return text

def format_ruc_field(text: str) -> str:
    """
    Formatea campo de RUC: '10750690713 - RAMOS FLORES CARLOS SEBASTIAN'
    """
    parts = text.split(' - ', 1)
    if len(parts) == 2:
        ruc = parts[0].strip()
        name = parts[1].strip()
        return f"{ruc} - {name}"
    return text

def format_dni_field(text: str) -> str:
    """
    Formatea campo de DNI limpiando tabs y espacios extra
    """
    # Buscar patrón DNI número - NOMBRE
    pattern = r'DNI\s+(\d+)\s*-\s*(.+)'
    match = re.search(pattern, text)
    
    if match:
        dni = match.group(1)
        name = re.sub(r'\s+', ' ', match.group(2).strip())
        return f"DNI {dni} - {name}"
    
    return re.sub(r'\s+', ' ', text.strip())

def format_economic_activity(text: str) -> str:
    """
    Formatea actividades económicas: 'Principal - 6202 - DESCRIPCIÓN'
    """
    # Buscar patrón Principal - código - descripción
    pattern = r'Principal\s*-\s*(\d+)\s*-\s*(.+)'
    match = re.search(pattern, text)
    
    if match:
        code = match.group(1)
        description = match.group(2).strip()
        return f"{code} - {description}"
    
    return text

def format_date_field(text: str) -> str:
    """
    Formatea campos con fechas que contienen 'desde' o información adicional
    """
    # Caso: "RECIBOS POR HONORARIOS AFILIADO DESDE 03/01/2017"
    if 'AFILIADO DESDE' in text.upper():
        pattern = r'(.+?)\s+AFILIADO\s+DESDE\s+(\d{2}/\d{2}/\d{4})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            description = match.group(1).strip()
            date = match.group(2)
            return f"{description} (afiliado desde {date})"
    
    # Caso: "RECIBO POR HONORARIO (desde 03/01/2017)"
    elif 'desde' in text.lower():
        pattern = r'(.+?)\s*\(desde\s+(\d{2}/\d{2}/\d{4})\)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return text  # Ya está bien formateado
        
        # Otro formato de desde
        pattern = r'(.+?)\s+desde\s+(\d{2}/\d{2}/\d{4})'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            description = match.group(1).strip()
            date = match.group(2)
            return f"{description} (desde {date})"
    
    return text

def extract_date_from_text(text: str) -> str:
    """
    Extrae solo la fecha de un texto si existe
    """
    pattern = r'(\d{2}/\d{2}/\d{4})'
    match = re.search(pattern, text)
    return match.group(1) if match else text

# Mapeo de campos comunes para estandarizar nombres
FIELD_MAPPING = {
    'numero_de_ruc': 'ruc',
    'tipo_contribuyente': 'tipo_contribuyente',
    'tipo_de_documento': 'documento_identidad',
    'nombre_comercial': 'nombre_comercial',
    'fecha_de_inscripcion': 'fecha_inscripcion',
    'estado_del_contribuyente': 'estado',
    'condicion_del_contribuyente': 'condicion',
    'domicilio_fiscal': 'domicilio_fiscal',
    'sistema_emision_de_comprobante': 'sistema_emision_comprobante',
    'sistema_contabilidad': 'sistema_contabilidad',
    'actividades_economicas': 'actividad_economica',
    'actividad_es_economica_s': 'actividad_economica',  # Variante del campo
    'comprobantes_de_pago_c_aut_de_impresion_f_806_u_816': 'comprobantes_autorizados',
    'sistema_de_emision_electronica': 'emision_electronica',
    'emisor_electronico_desde': 'emisor_electronico_desde',
    'comprobantes_electronicos': 'comprobantes_electronicos',
    'afiliado_al_ple_desde': 'afiliado_ple_desde',
    'padrones': 'padrones'
}

def apply_field_mapping(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aplica mapeo de campos para estandarizar nombres
    """
    mapped_data = {}
    
    for key, value in data.items():
        # Usar mapeo si existe, sino mantener la clave original
        mapped_key = FIELD_MAPPING.get(key, key)
        mapped_data[mapped_key] = value
    
    return mapped_data