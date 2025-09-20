from fastapi import FastAPI, HTTPException, Query
from .scraper import scrape_sunat
from .excel_utils import read_excel
from .save_utils import save_results_to_files, save_summary_report
from .data_formatter import clean_and_format_data, apply_field_mapping

app = FastAPI(title="SUNAT Scraper API")

@app.get("/")
def root():
    """
    Información básica de la API
    """
    return {
        "mensaje": "API SUNAT Scraper",
        "version": "1.1.0",
        "descripcion": "API para consultar información de empresas en SUNAT",
        "tipos_busqueda": ["nombre", "ruc", "documento"],
        "documentacion": "/docs",
        "ejemplo_datos_formateados": "/ejemplo-formato"
    }

@app.get("/debug-ruc/{ruc}")
def debug_ruc(ruc: str):
    """
    Endpoint especial para debuggear problemas con búsqueda por RUC
    Siempre ejecuta en modo debug visible
    """
    try:
        # Validar formato básico de RUC
        if not ruc.isdigit() or len(ruc) != 11:
            raise HTTPException(status_code=400, detail="El RUC debe tener 11 dígitos")
        
        print(f"🔍 DEBUGGING RUC: {ruc}")
        resultados = scrape_sunat(ruc, search_type="ruc", debug_mode=True)  # Forzar debug
        
        return {
            "ruc": ruc,
            "tipo_busqueda": "ruc",
            "modo": "debug",
            "resultados": resultados,
            "nota": "Este endpoint siempre ejecuta en modo debug para identificar problemas"
        }
    
    except Exception as e:
        return {
            "error": f"Error en debug RUC: {str(e)}",
            "ruc": ruc,
            "sugerencia": "Revisa los logs del servidor para más detalles"
        }
def ejemplo_formato():
    """
    Muestra un ejemplo de cómo se formatean los datos de salida
    """
    ejemplo_original = {
        "Número de RUC": "10750690713 - RAMOS FLORES CARLOS SEBASTIAN",
        "Tipo Contribuyente": "PERSONA NATURAL SIN NEGOCIO",
        "Tipo de Documento": "DNI  75069071 - RAMOS FLORES, CARLOS SEBASTIAN",
        "Nombre Comercial": "-",
        "Fecha de Inscripción": "02/01/2017",
        "Estado del Contribuyente": "ACTIVO",
        "Condición del Contribuyente": "HABIDO",
        "Actividad(es) Económica(s)": "Principal - 6202 - CONSULTORÍA DE INFORMÁTICA",
        "Sistema de Emisión Electrónica": "RECIBOS POR HONORARIOS AFILIADO DESDE 03/01/2017"
    }
    
    ejemplo_formateado = apply_field_mapping(clean_and_format_data(ejemplo_original))
    
    return {
        "datos_originales": ejemplo_original,
        "datos_formateados": ejemplo_formateado,
        "mejoras": [
            "Claves convertidas a snake_case",
            "Valores '-' y 'NINGUNO' convertidos a null",
            "Espacios y tabs extra removidos",
            "Campos de fecha formateados consistentemente",
            "Nombres de campos estandarizados"
        ]
    }

@app.get("/consulta/{nombre}")
def consulta(nombre: str, debug: bool = Query(False, description="Ejecutar en modo debug (navegador visible)")):
    """
    Consulta información de una empresa por nombre o razón social en SUNAT
    """
    try:
        resultados = scrape_sunat(nombre, search_type="nombre", debug_mode=debug)
        
        # Check if we got error results
        if resultados and isinstance(resultados[0], dict) and "error" in resultados[0]:
            error_msg = resultados[0]["error"]
            if "conexión" in error_msg.lower() or "connection" in error_msg.lower():
                raise HTTPException(status_code=503, detail=error_msg)
            else:
                raise HTTPException(status_code=400, detail=error_msg)
        
        return {"nombre": nombre, "tipo_busqueda": "nombre", "resultados": resultados}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/consulta-ruc/{ruc}")
def consulta_ruc(ruc: str, debug: bool = Query(False, description="Ejecutar en modo debug (navegador visible)")):
    """
    Consulta información de una empresa por RUC en SUNAT
    """
    try:
        # Validar formato básico de RUC (11 dígitos)
        if not ruc.isdigit() or len(ruc) != 11:
            raise HTTPException(status_code=400, detail="El RUC debe tener 11 dígitos")
        
        resultados = scrape_sunat(ruc, search_type="ruc", debug_mode=debug)
        
        # Check if we got error results
        if resultados and isinstance(resultados[0], dict) and "error" in resultados[0]:
            error_msg = resultados[0]["error"]
            if "conexión" in error_msg.lower() or "connection" in error_msg.lower():
                raise HTTPException(status_code=503, detail=error_msg)
            else:
                raise HTTPException(status_code=400, detail=error_msg)
        
        return {"ruc": ruc, "tipo_busqueda": "ruc", "resultados": resultados}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/consulta-documento/{numero_documento}")
def consulta_documento(
    numero_documento: str, 
    tipo_documento: str = Query("1", description="Tipo de documento (1=DNI, 4=Carnet Extranjería, 7=Pasaporte, A=Cédula Diplomática)"),
    debug: bool = Query(False, description="Ejecutar en modo debug (navegador visible)")
):
    """
    Consulta información de una empresa por número de documento del representante en SUNAT
    """
    try:
        # Validar tipo de documento
        tipos_validos = ["1", "4", "7", "A"]
        if tipo_documento not in tipos_validos:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de documento no válido. Use: {', '.join(tipos_validos)}"
            )
        
        # Validaciones básicas según tipo de documento
        if tipo_documento == "1":  # DNI
            if not numero_documento.isdigit() or len(numero_documento) != 8:
                raise HTTPException(status_code=400, detail="El DNI debe tener 8 dígitos")
        
        resultados = scrape_sunat(numero_documento, search_type="documento", document_type=tipo_documento, debug_mode=debug)
        
        # Check if we got error results
        if resultados and isinstance(resultados[0], dict) and "error" in resultados[0]:
            error_msg = resultados[0]["error"]
            if "conexión" in error_msg.lower() or "connection" in error_msg.lower():
                raise HTTPException(status_code=503, detail=error_msg)
            else:
                raise HTTPException(status_code=400, detail=error_msg)
        
        tipos_doc = {"1": "DNI", "4": "Carnet de Extranjería", "7": "Pasaporte", "A": "Cédula Diplomática"}
        return {
            "numero_documento": numero_documento, 
            "tipo_documento": tipos_doc.get(tipo_documento, tipo_documento),
            "tipo_busqueda": "documento", 
            "resultados": resultados
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/consulta-excel")
def consulta_excel(
    tipo_busqueda: str = Query("nombre", description="Tipo de búsqueda (nombre, ruc, documento)"),
    tipo_documento: str = Query("1", description="Para búsqueda por documento: tipo (1=DNI, 4=Carnet Extranjería, 7=Pasaporte, A=Cédula Diplomática)"),
    debug: bool = Query(False, description="Ejecutar en modo debug (navegador visible)")
):
    """
    Consulta información de todas las empresas listadas en el archivo Excel
    y guarda los resultados en archivos (JSON, Excel, CSV)
    """
    try:
        # Validar tipo de búsqueda
        tipos_validos = ["nombre", "ruc", "documento"]
        if tipo_busqueda not in tipos_validos:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de búsqueda no válido. Use: {', '.join(tipos_validos)}"
            )
        
        if tipo_busqueda == "documento":
            tipos_doc_validos = ["1", "4", "7", "A"]
            if tipo_documento not in tipos_doc_validos:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Tipo de documento no válido. Use: {', '.join(tipos_doc_validos)}"
                )
        
        print(f"🚀 Iniciando consulta masiva por {tipo_busqueda} desde Excel...")
        datos_excel = read_excel()
        print(f"📋 Se encontraron {len(datos_excel)} registros para consultar")
        
        all_results = {}
        errors = []
        processed = 0
        
        for i, valor in enumerate(datos_excel, 1):
            try:
                print(f"📊 Procesando registro {i}/{len(datos_excel)}: {valor}")
                
                # Validaciones básicas según tipo de búsqueda
                if tipo_busqueda == "ruc" and (not valor.isdigit() or len(valor) != 11):
                    error_msg = f"RUC inválido: {valor} (debe tener 11 dígitos)"
                    errors.append(error_msg)
                    all_results[valor] = [{"error": error_msg}]
                    continue
                
                if tipo_busqueda == "documento" and tipo_documento == "1" and (not valor.isdigit() or len(valor) != 8):
                    error_msg = f"DNI inválido: {valor} (debe tener 8 dígitos)"
                    errors.append(error_msg)
                    all_results[valor] = [{"error": error_msg}]
                    continue
                
                # Realizar scraping
                resultados = scrape_sunat(valor, search_type=tipo_busqueda, document_type=tipo_documento, debug_mode=debug)
                
                if resultados and isinstance(resultados[0], dict) and "error" in resultados[0]:
                    error_msg = f"{valor}: {resultados[0]['error']}"
                    errors.append(error_msg)
                    print(f"❌ Error en {valor}: {resultados[0]['error']}")
                else:
                    print(f"✅ Datos obtenidos para {valor}: {len(resultados)} resultado(s)")
                
                all_results[valor] = resultados
                processed += 1
                
                # Mostrar progreso cada 5 registros
                if processed % 5 == 0:
                    print(f"📈 Progreso: {processed}/{len(datos_excel)} registros procesados")
                    
            except Exception as e:
                error_msg = f"Error procesando {valor}: {str(e)}"
                errors.append(error_msg)
                all_results[valor] = [{"error": error_msg}]
                print(f"💥 Error inesperado en {valor}: {str(e)}")
        
        # Preparar datos para guardado
        response_data = {
            "resultados": all_results,
            "tipo_busqueda": tipo_busqueda,
            "tipo_documento": tipo_documento if tipo_busqueda == "documento" else None
        }
        if errors:
            response_data["errores"] = errors
        
        print(f"\n📁 Guardando resultados en archivos...")
        
        # Guardar en archivos
        filename_base = f"consulta_sunat_{tipo_busqueda}"
        if tipo_busqueda == "documento":
            tipos_doc = {"1": "dni", "4": "carnet", "7": "pasaporte", "A": "cedula"}
            filename_base += f"_{tipos_doc.get(tipo_documento, tipo_documento)}"
        
        saved_files = save_results_to_files(response_data, filename_base)
        
        # Generar reporte resumen
        report_file = save_summary_report(response_data, saved_files)
        if report_file:
            saved_files['reporte'] = report_file
        
        # Preparar respuesta resumida
        summary = {
            "mensaje": "✅ Consulta completada exitosamente",
            "tipo_busqueda": tipo_busqueda,
            "total_registros": len(datos_excel),
            "registros_procesados": processed,
            "total_errores": len(errors),
            "archivos_generados": saved_files,
            "resumen": {
                "registros_con_datos": len([k for k, v in all_results.items() 
                                         if v and not (isinstance(v[0], dict) and 'error' in v[0])]),
                "total_resultados": sum(len(v) for v in all_results.values() 
                                      if v and not (isinstance(v[0], dict) and 'error' in v[0]))
            }
        }
        
        if tipo_busqueda == "documento":
            tipos_doc = {"1": "DNI", "4": "Carnet de Extranjería", "7": "Pasaporte", "A": "Cédula Diplomática"}
            summary["tipo_documento"] = tipos_doc.get(tipo_documento, tipo_documento)
        
        if errors:
            summary["errores_muestra"] = errors[:5]  # Solo mostrar los primeros 5 errores
            if len(errors) > 5:
                summary["errores_muestra"].append(f"... y {len(errors) - 5} errores más (ver archivo de reporte)")
        
        print(f"\n🎉 ¡Proceso completado!")
        print(f"📊 Registros procesados: {processed}")
        print(f"📁 Archivos guardados en: data/resultados/")
        
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
