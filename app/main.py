from fastapi import FastAPI, HTTPException, Query
from .scraper import scrape_sunat
from .excel_utils import read_excel
from .save_utils import save_results_to_files, save_summary_report

app = FastAPI(title="SUNAT Scraper API")

@app.get("/consulta/{nombre}")
def consulta(nombre: str, debug: bool = Query(False, description="Ejecutar en modo debug (navegador visible)")):
    """
    Consulta información de una empresa por nombre en SUNAT
    """
    try:
        resultados = scrape_sunat(nombre, debug_mode=debug)
        
        # Check if we got error results
        if resultados and isinstance(resultados[0], dict) and "error" in resultados[0]:
            error_msg = resultados[0]["error"]
            if "conexión" in error_msg.lower() or "connection" in error_msg.lower():
                raise HTTPException(status_code=503, detail=error_msg)
            else:
                raise HTTPException(status_code=400, detail=error_msg)
        
        return {"nombre": nombre, "resultados": resultados}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/consulta-excel")
def consulta_excel(debug: bool = Query(False, description="Ejecutar en modo debug (navegador visible)")):
    """
    Consulta información de todas las empresas listadas en el archivo Excel
    y guarda los resultados en archivos (JSON, Excel, CSV)
    """
    try:
        print("🚀 Iniciando consulta masiva de empresas desde Excel...")
        nombres = read_excel()
        print(f"📋 Se encontraron {len(nombres)} empresas para consultar")
        
        all_results = {}
        errors = []
        processed = 0
        
        for i, nombre in enumerate(nombres, 1):
            try:
                print(f"📊 Procesando empresa {i}/{len(nombres)}: {nombre}")
                resultados = scrape_sunat(nombre, debug_mode=debug)
                
                if resultados and isinstance(resultados[0], dict) and "error" in resultados[0]:
                    error_msg = f"{nombre}: {resultados[0]['error']}"
                    errors.append(error_msg)
                    print(f"❌ Error en {nombre}: {resultados[0]['error']}")
                else:
                    print(f"✅ Datos obtenidos para {nombre}: {len(resultados)} resultado(s)")
                
                all_results[nombre] = resultados
                processed += 1
                
                # Mostrar progreso cada 5 empresas
                if processed % 5 == 0:
                    print(f"📈 Progreso: {processed}/{len(nombres)} empresas procesadas")
                    
            except Exception as e:
                error_msg = f"Error procesando {nombre}: {str(e)}"
                errors.append(error_msg)
                all_results[nombre] = [{"error": error_msg}]
                print(f"💥 Error inesperado en {nombre}: {str(e)}")
        
        # Preparar datos para guardado
        response_data = {"resultados": all_results}
        if errors:
            response_data["errores"] = errors
        
        print(f"\n📁 Guardando resultados en archivos...")
        
        # Guardar en archivos
        saved_files = save_results_to_files(response_data)
        
        # Generar reporte resumen
        report_file = save_summary_report(response_data, saved_files)
        if report_file:
            saved_files['reporte'] = report_file
        
        # Preparar respuesta resumida
        summary = {
            "mensaje": "✅ Consulta completada exitosamente",
            "total_empresas": len(nombres),
            "empresas_procesadas": processed,
            "total_errores": len(errors),
            "archivos_generados": saved_files,
            "resumen": {
                "empresas_con_datos": len([k for k, v in all_results.items() 
                                         if v and not (isinstance(v[0], dict) and 'error' in v[0])]),
                "total_resultados": sum(len(v) for v in all_results.values() 
                                      if v and not (isinstance(v[0], dict) and 'error' in v[0]))
            }
        }
        
        if errors:
            summary["errores_muestra"] = errors[:5]  # Solo mostrar los primeros 5 errores
            if len(errors) > 5:
                summary["errores_muestra"].append(f"... y {len(errors) - 5} errores más (ver archivo de reporte)")
        
        print(f"\n🎉 ¡Proceso completado!")
        print(f"📊 Empresas procesadas: {processed}")
        print(f"📁 Archivos guardados en: data/resultados/")
        
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
