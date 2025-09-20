# 🏢 API SUNAT Scraper

Una API REST desarrollada con FastAPI para consultar información de empresas en el portal de SUNAT (Servicio de Administración Tributaria del Perú) mediante múltiples métodos de búsqueda.

## 📋 Características

- **Múltiples tipos de búsqueda**:
  - 🏷️ Por nombre o razón social
  - 🔢 Por RUC (Registro Único de Contribuyentes) - **Optimizado para resultados directos**
  - 📄 Por documento del representante (DNI, Carnet, Pasaporte, Cédula Diplomática)
- **Consulta individual**: Busca información de una empresa específica
- **Consulta masiva**: Procesa múltiples registros desde un archivo Excel
- **Múltiples formatos de salida**: JSON, Excel, CSV y reportes de texto
- **Manejo robusto de errores**: Reintentos automáticos y manejo de fallos de conexión
- **Modo debug**: Navegador visible para depuración
- **Anti-detección**: Configuraciones realistas del navegador para evitar bloqueos
- **Validaciones automáticas**: Verificación de formato de RUC, DNI y otros documentos
- **Datos formateados**: Campos en snake_case con limpieza automática de texto
- **Búsqueda optimizada por RUC**: Acceso directo sin navegación adicional

## 🚀 Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd api-sunat
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   # o
   venv\\Scripts\\activate  # En Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Instalar navegadores de Playwright**
   ```bash
   playwright install chromium
   ```

5. **Preparar archivo de datos** (opcional)
   - Coloca tu archivo Excel con los datos a consultar en `data/empresas.xlsx`
   - El archivo puede contener nombres de empresas, RUCs o números de documento
   - Se usará la primera columna por defecto, o puedes especificar la columna

## 🔧 Uso

### Iniciar el servidor

```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar servidor
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://127.0.0.1:8000`

### Endpoints disponibles

#### 1. Consulta por nombre/razón social
```
GET /consulta/{nombre_empresa}
```

**Ejemplo:**
```bash
curl "http://127.0.0.1:8000/consulta/EMPRESA%20EJEMPLO%20S.A.C."
```

#### 2. Consulta por RUC (Optimizada)
```
GET /consulta-ruc/{ruc}
```

**Ejemplo:**
```bash
curl "http://127.0.0.1:8000/consulta-ruc/20123456789"
```

**Características especiales:**
- ✅ **Acceso directo**: Sin navegación intermedia
- ⚡ **Más rápida**: Resultado inmediato de SUNAT
- 🎯 **Datos completos**: Información completa en una sola consulta
- 🔍 **Sin búsqueda de enlaces**: Procesa directamente la vista de resultado

**Validaciones:**
- El RUC debe tener exactamente 11 dígitos
- Solo se aceptan números

#### 3. Consulta por documento del representante
```
GET /consulta-documento/{numero_documento}
```

**Ejemplo:**
```bash
# Consulta por DNI (por defecto)
curl "http://127.0.0.1:8000/consulta-documento/12345678"

# Consulta por Carnet de Extranjería
curl "http://127.0.0.1:8000/consulta-documento/123456789?tipo_documento=4"

# Consulta por Pasaporte
curl "http://127.0.0.1:8000/consulta-documento/AB123456?tipo_documento=7"
```

**Tipos de documento disponibles:**
- `1` = DNI (Documento Nacional de Identidad) - *Por defecto*
- `4` = Carnet de Extranjería
- `7` = Pasaporte
- `A` = Cédula Diplomática de Identidad

**Validaciones:**
- DNI: debe tener exactamente 8 dígitos

#### 4. Consulta masiva desde Excel
```
GET /consulta-excel
```

**Ejemplos:**
```bash
# Consulta masiva por nombres (por defecto)
curl "http://127.0.0.1:8000/consulta-excel"

# Consulta masiva por RUCs
curl "http://127.0.0.1:8000/consulta-excel?tipo_busqueda=ruc"

# Consulta masiva por DNIs
curl "http://127.0.0.1:8000/consulta-excel?tipo_busqueda=documento&tipo_documento=1"

# Consulta masiva por Carnets de Extranjería
curl "http://127.0.0.1:8000/consulta-excel?tipo_busqueda=documento&tipo_documento=4"
```

**Parámetros:**
- `tipo_busqueda`: `nombre` (por defecto), `ruc` o `documento`
- `tipo_documento`: Para búsqueda por documento (`1`, `4`, `7`, `A`)
- `debug`: `true` para modo debug

**Características:**
- Lee datos desde `data/empresas.xlsx`
- Guarda resultados automáticamente en `data/resultados/`
- Genera múltiples formatos (JSON, Excel, CSV, reporte)
- Validaciones automáticas según el tipo de búsqueda

#### 5. Documentación interactiva
```
http://127.0.0.1:8000/docs
```

**Parámetros opcionales (todos los endpoints):**
- `debug=true`: Ejecuta en modo debug (navegador visible)

## 📊 Formatos de salida

### Consultas individuales
Devuelve JSON con la información de la empresa:

```json
## 📄 Ejemplos de respuesta

### Formato de datos actualizado

Todos los endpoints ahora devuelven datos **formateados y limpios**:

- 🔤 **Campos en snake_case**: `numero_ruc`, `razon_social`, `estado_contribuyente`, etc.
- 🧹 **Texto limpio**: Espacios extra, saltos de línea y caracteres especiales removidos
- 📋 **Campos estandarizados**: Mapeo consistente de nombres de campos
- ✨ **Valores normalizados**: Estados como "ACTIVO/INACTIVO", "HABIDO/NO HABIDO"

### Consulta por nombre
```json
{
  "nombre": "EMPRESA EJEMPLO",
  "tipo_busqueda": "nombre",
  "resultados": [
    {
      "numero_ruc": "20123456789 - EMPRESA EJEMPLO SOCIEDAD ANONIMA CERRADA",
      "tipo_contribuyente": "SOCIEDAD ANONIMA CERRADA",
      "nombre_comercial": "-",
      "fecha_inscripcion": "01/03/2005",
      "fecha_inicio_actividades": "01/03/2005",
      "estado_contribuyente": "ACTIVO",
      "condicion_contribuyente": "HABIDO",
      "domicilio_fiscal": "AV. EJEMPLO NRO. 123 LIMA - LIMA - SAN ISIDRO",
      "sistema_emision_comprobante": "MANUAL",
      "actividad_comercio_exterior": "SIN ACTIVIDAD",
      "sistema_contabilidad": "MANUAL/COMPUTARIZADO",
      "actividades_economicas": "Principal - 7110 - ACTIVIDADES DE ARQUITECTURA E INGENIERÍA...",
      "comprobantes_pago_autorizados": "FACTURA | BOLETA DE VENTA | NOTA DE CREDITO...",
      "sistema_emision_electronica": "FACTURA PORTAL DESDE 22/04/2020 | BOLETA PORTAL...",
      "emisor_electronico_desde": "22/04/2020",
      "comprobantes_electronicos": "FACTURA (desde 22/04/2020),BOLETA (desde 21/05/2020)...",
      "afiliado_ple_desde": "-",
      "padrones": "NINGUNO"
    }
  ]
}
```

### Consulta por RUC (Optimizada)
```json
{
  "ruc": "20123456789",
  "tipo_busqueda": "ruc",
  "resultados": [
    {
      "numero_ruc": "20123456789 - EMPRESA EJEMPLO SOCIEDAD ANONIMA CERRADA",
      "tipo_contribuyente": "SOCIEDAD ANONIMA CERRADA",
      "estado_contribuyente": "ACTIVO",
      "condicion_contribuyente": "HABIDO",
      "domicilio_fiscal": "AV. EJEMPLO NRO. 123 LIMA - LIMA - SAN ISIDRO",
      "actividades_economicas": "Principal - 7110 - ACTIVIDADES DE ARQUITECTURA..."
    }
  ]
}
```
```

### Consulta por RUC
```json
{
  "ruc": "20123456789",
  "tipo_busqueda": "ruc",
  "resultados": [...]
}
```

### Consulta por documento
```json
{
  "numero_documento": "12345678",
  "tipo_documento": "DNI",
  "tipo_busqueda": "documento",
  "resultados": [...]
}
```

### Consulta masiva
Genera archivos en `data/resultados/`:

- **`consulta_sunat_[tipo]_YYYYMMDD_HHMMSS.json`**: Datos completos en JSON
- **`consulta_sunat_[tipo]_YYYYMMDD_HHMMSS.xlsx`**: Hoja de cálculo con resultados
- **`consulta_sunat_[tipo]_YYYYMMDD_HHMMSS.csv`**: Archivo CSV para análisis
- **`reporte_YYYYMMDD_HHMMSS.txt`**: Resumen ejecutivo

Donde `[tipo]` puede ser: `nombre`, `ruc`, `documento_dni`, `documento_carnet`, etc.

## ⚙️ Configuración

### Variables de entorno

Crea un archivo `.env` para personalizar el comportamiento:

```env
# Modo debug global (navegador visible)
SUNAT_DEBUG=false

# Puerto del servidor
PORT=8000
```

### Configuración del Excel

El archivo `data/empresas.xlsx` debe contener los datos a consultar en la primera columna:

#### Para búsqueda por nombres:
```
| Empresa                    |
|----------------------------|
| EMPRESA UNO S.A.C.        |
| COMPAÑÍA DOS S.R.L.       |
| NEGOCIO TRES E.I.R.L.     |
```

#### Para búsqueda por RUC:
```
| RUC         |
|-------------|
| 20123456789 |
| 20987654321 |
| 10123456789 |
```

#### Para búsqueda por documento:
```
| Documento |
|-----------|
| 12345678  |
| 87654321  |
| 11223344  |
```

**Nota**: El sistema usa automáticamente la primera columna del Excel, independientemente de su nombre.

## 🔍 Modo Debug

Para ver el navegador en funcionamiento:

```bash
# Consulta individual con debug
curl "http://127.0.0.1:8000/consulta/EMPRESA?debug=true"
curl "http://127.0.0.1:8000/consulta-ruc/20123456789?debug=true"
curl "http://127.0.0.1:8000/consulta-documento/12345678?debug=true"

# Consulta masiva con debug
curl "http://127.0.0.1:8000/consulta-excel?debug=true"
curl "http://127.0.0.1:8000/consulta-excel?tipo_busqueda=ruc&debug=true"

# O configurar globalmente
export SUNAT_DEBUG=true
uvicorn app.main:app --reload
```

## 🛠️ Manejo de errores

El sistema incluye manejo robusto de errores:

- **Reintentos automáticos**: 3 intentos con backoff exponencial
- **Múltiples estrategias**: Fill directo, click+type, inyección JavaScript
- **Timeouts configurables**: Esperas inteligentes para elementos
- **Recuperación de sesión**: Continúa con otros registros si uno falla
- **Validaciones automáticas**: 
  - RUC: exactamente 11 dígitos
  - DNI: exactamente 8 dígitos
  - Tipos de documento válidos

### Códigos de error HTTP

- **400 Bad Request**: Datos de entrada inválidos (RUC/DNI mal formateado, tipo de búsqueda inválido)
- **503 Service Unavailable**: Problemas de conexión con SUNAT
- **500 Internal Server Error**: Errores inesperados del servidor

## 📁 Estructura del proyecto

```
api-sunat/
├── app/
│   ├── __init__.py
│   ├── main.py           # Aplicación FastAPI principal
│   ├── scraper.py        # Lógica de web scraping
│   ├── parser.py         # Procesamiento de HTML
│   ├── excel_utils.py    # Utilidades para Excel
│   └── save_utils.py     # Guardado de resultados
├── data/
│   ├── empresas.xlsx     # Archivo de entrada
│   └── resultados/       # Archivos de salida
├── requirements.txt      # Dependencias
├── .gitignore           # Archivos ignorados
└── README.md            # Este archivo
```

## 🚨 Consideraciones importantes

### Términos de uso
- Este proyecto es para fines educativos y de automatización legítima
- Respeta los términos de servicio del sitio web de SUNAT
- Usa delays apropiados para no sobrecargar el servidor

### Limitaciones
- Dependiente de la estructura HTML del sitio de SUNAT
- Puede requerir actualizaciones si SUNAT cambia su interfaz
- El rendimiento depende de la velocidad de conexión a internet

### Rendimiento
- **Consulta individual**: ~10-15 segundos por registro
- **Consulta masiva**: Proceso automático con progreso visible
- **Optimizaciones**: Delays balanceados entre velocidad y detección
- **Diferentes tipos de búsqueda**:
  - Por RUC: Más rápido (campo directo)
  - Por nombre: Requiere click adicional
  - Por documento: Requiere selección de tipo

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu característica (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Solución de problemas

### Error de conexión
```
Error de conexión: No se pudo conectar al sitio web de SUNAT
```
**Solución**: Verificar conexión a internet y reintentar. El sitio de SUNAT puede estar temporalmente no disponible.

### Elemento no visible
```
Timeout 30000ms exceeded
```
**Solución**: Ejecutar en modo debug (`debug=true`) para ver qué está pasando en el navegador.

### RUC inválido
```
El RUC debe tener 11 dígitos
```
**Solución**: Verificar que el RUC tenga exactamente 11 dígitos numéricos.

### DNI inválido
```
El DNI debe tener 8 dígitos
```
**Solución**: Verificar que el DNI tenga exactamente 8 dígitos numéricos.

### Tipo de documento inválido
```
Tipo de documento no válido. Use: 1, 4, 7, A
```
**Solución**: Usar uno de los tipos válidos (1=DNI, 4=Carnet, 7=Pasaporte, A=Cédula Diplomática).

### Playwright no instalado
```
playwright executable doesn't exist
```
**Solución**: Ejecutar `playwright install chromium`

### Archivo Excel no encontrado
```
No such file or directory: 'data/empresas.xlsx'
```
**Solución**: Crear el archivo Excel en la ruta correcta con los datos a consultar.

## 📞 Soporte

Si encuentras problemas o tienes preguntas:

1. Revisa la sección de solución de problemas
2. Verifica que tienes la última versión
3. Ejecuta en modo debug para diagnosticar
4. Abre un issue en el repositorio con detalles del error

---

**Desarrollado con ❤️ para automatizar consultas SUNAT de manera eficiente y responsable.**