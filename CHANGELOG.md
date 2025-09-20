# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-09-19

### Agregado
- 🔢 **Búsqueda por RUC**: Nuevo endpoint `/consulta-ruc/{ruc}` para buscar directamente por RUC
- 📄 **Búsqueda por documento**: Nuevo endpoint `/consulta-documento/{numero}` con soporte para:
  - DNI (Documento Nacional de Identidad)
  - Carnet de Extranjería
  - Pasaporte
  - Cédula Diplomática de Identidad
- 🔧 **Consulta masiva multimodal**: El endpoint `/consulta-excel` ahora soporta múltiples tipos de búsqueda
- ✅ **Validaciones automáticas**: Verificación de formato para RUC (11 dígitos) y DNI (8 dígitos)
- 📊 **Archivos con identificación**: Los archivos de salida incluyen el tipo de búsqueda en el nombre

### Cambiado
- 🔄 **Función scraper mejorada**: Soporte para múltiples tipos de búsqueda con selección automática de campos
- 📈 **Respuestas enriquecidas**: Todas las respuestas incluyen el tipo de búsqueda utilizada
- 📁 **Excel utils más flexible**: Lectura automática de la primera columna independientemente del nombre
- 🎯 **Manejo de errores específico**: Códigos HTTP apropiados según el tipo de error

### Endpoints nuevos
- `GET /consulta-ruc/{ruc}` - Consulta por RUC
- `GET /consulta-documento/{numero_documento}` - Consulta por documento del representante

### Parámetros nuevos
- `tipo_busqueda` en `/consulta-excel` (nombre, ruc, documento)
- `tipo_documento` para especificar tipo de documento (1, 4, 7, A)
- Validación automática de parámetros según el tipo de búsqueda

## [1.0.0] - 2025-09-19

### Agregado
- ✨ API REST completa con FastAPI
- 🔍 Consulta individual de empresas por nombre/razón social
- 📊 Consulta masiva desde archivo Excel
- 💾 Guardado automático en múltiples formatos (JSON, Excel, CSV)
- 🐛 Modo debug con navegador visible
- 🔄 Sistema de reintentos con backoff exponencial
- 🛡️ Manejo robusto de errores y timeouts
- 📋 Generación de reportes resumidos
- 🤖 Configuraciones anti-detección para el navegador
- ⚡ Delays optimizados entre velocidad y realismo

### Características técnicas
- Scraping con Playwright para mayor confiabilidad
- Múltiples estrategias de interacción con elementos (fill, click+type, JavaScript)
- Parsing inteligente de resultados HTML con BeautifulSoup
- Manejo de overlays y elementos dinámicos
- Scrolling automático para elementos fuera de vista
- Headers HTTP realistas y user-agent auténtico

### Endpoints disponibles
- `GET /consulta/{nombre}` - Consulta individual por nombre
- `GET /consulta-excel` - Consulta masiva desde Excel
- `GET /docs` - Documentación interactiva (Swagger UI)

### Formatos de salida
- JSON para integración con otras aplicaciones
- Excel con hojas separadas para datos y errores
- CSV para análisis de datos
- Reportes de texto plano con resúmenes ejecutivos

### Configuración
- Variables de entorno para personalización
- Modo debug configurable globalmente
- Timeouts y delays ajustables
- Directorio de salida personalizable

---

## Tipos de cambios
- **Agregado** para nuevas características
- **Cambiado** para cambios en funcionalidad existente
- **Obsoleto** para características que pronto serán removidas
- **Removido** para características removidas
- **Corregido** para corrección de bugs
- **Seguridad** para vulnerabilidades