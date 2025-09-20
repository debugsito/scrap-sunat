# 🏢 API SUNAT Scraper

Una API REST desarrollada con FastAPI para consultar información de empresas en el portal de SUNAT (Servicio de Administración Tributaria del Perú).

## 📋 Características

- **Consulta individual**: Busca información de una empresa específica por nombre o razón social
- **Consulta masiva**: Procesa múltiples empresas desde un archivo Excel
- **Múltiples formatos de salida**: JSON, Excel, CSV y reportes de texto
- **Manejo robusto de errores**: Reintentos automáticos y manejo de fallos de conexión
- **Modo debug**: Navegador visible para depuración
- **Anti-detección**: Configuraciones realistas del navegador para evitar bloqueos

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
   - Coloca tu archivo Excel con las empresas a consultar en `data/empresas.xlsx`
   - El archivo debe tener una columna con los nombres de las empresas

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

#### 1. Consulta individual
```
GET /consulta/{nombre_empresa}
```

**Ejemplo:**
```bash
curl "http://127.0.0.1:8000/consulta/EMPRESA%20EJEMPLO%20S.A.C."
```

**Parámetros opcionales:**
- `debug=true`: Ejecuta en modo debug (navegador visible)

#### 2. Consulta masiva desde Excel
```
GET /consulta-excel
```

**Ejemplo:**
```bash
curl "http://127.0.0.1:8000/consulta-excel"
```

**Características:**
- Lee empresas desde `data/empresas.xlsx`
- Guarda resultados automáticamente en `data/resultados/`
- Genera múltiples formatos (JSON, Excel, CSV, reporte)

#### 3. Documentación interactiva
```
http://127.0.0.1:8000/docs
```

## 📊 Formatos de salida

### Consulta individual
Devuelve JSON con la información de la empresa:

```json
{
  "nombre": "EMPRESA EJEMPLO S.A.C.",
  "resultados": [
    {
      "RUC": "20123456789",
      "Razón Social": "EMPRESA EJEMPLO SOCIEDAD ANONIMA CERRADA",
      "Estado del Contribuyente": "ACTIVO",
      "Condición del Domicilio": "HABIDO",
      "Dirección": "CAL. EJEMPLO NRO. 123 LIMA - LIMA - SAN ISIDRO"
    }
  ]
}
```

### Consulta masiva
Genera archivos en `data/resultados/`:

- **`consulta_sunat_YYYYMMDD_HHMMSS.json`**: Datos completos en JSON
- **`consulta_sunat_YYYYMMDD_HHMMSS.xlsx`**: Hoja de cálculo con resultados
- **`consulta_sunat_YYYYMMDD_HHMMSS.csv`**: Archivo CSV para análisis
- **`reporte_YYYYMMDD_HHMMSS.txt`**: Resumen ejecutivo

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

El archivo `data/empresas.xlsx` debe tener:
- **Hoja**: "Empresas" (por defecto)
- **Columna**: Nombres de empresas (primera columna)

Ejemplo:
```
| Empresa                    |
|----------------------------|
| EMPRESA UNO S.A.C.        |
| COMPAÑÍA DOS S.R.L.       |
| NEGOCIO TRES E.I.R.L.     |
```

## 🔍 Modo Debug

Para ver el navegador en funcionamiento:

```bash
# Consulta individual con debug
curl "http://127.0.0.1:8000/consulta/EMPRESA?debug=true"

# Consulta masiva con debug
curl "http://127.0.0.1:8000/consulta-excel?debug=true"

# O configurar globalmente
export SUNAT_DEBUG=true
uvicorn app.main:app --reload
```

## 🛠️ Manejo de errores

El sistema incluye manejo robusto de errores:

- **Reintentos automáticos**: 3 intentos con backoff exponencial
- **Múltiples estrategias**: Fill directo, click+type, inyección JavaScript
- **Timeouts configurables**: Esperas inteligentes para elementos
- **Recuperación de sesión**: Continúa con otras empresas si una falla

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
- **Consulta individual**: ~10-15 segundos por empresa
- **Consulta masiva**: Proceso automático con progreso visible
- **Optimizaciones**: Delays balanceados entre velocidad y detección

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

### Playwright no instalado
```
playwright executable doesn't exist
```
**Solución**: Ejecutar `playwright install chromium`

## 📞 Soporte

Si encuentras problemas o tienes preguntas:

1. Revisa la sección de solución de problemas
2. Verifica que tienes la última versión
3. Ejecuta en modo debug para diagnosticar
4. Abre un issue en el repositorio con detalles del error

---

**Desarrollado con ❤️ para automatizar consultas SUNAT de manera eficiente y responsable.**