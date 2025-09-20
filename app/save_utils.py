import json
import pandas as pd
from datetime import datetime
import os

def save_results_to_files(results_data: dict, base_filename: str = None) -> dict:
    """
    Guarda los resultados en múltiples formatos (JSON, Excel, CSV)
    
    Args:
        results_data: Diccionario con los resultados {empresa: [datos]}
        base_filename: Nombre base para los archivos (opcional)
    
    Returns:
        Diccionario con las rutas de los archivos guardados
    """
    if base_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"consulta_sunat_{timestamp}"
    
    # Crear directorio de salida si no existe
    output_dir = "data/resultados"
    os.makedirs(output_dir, exist_ok=True)
    
    # Rutas de archivos
    json_file = os.path.join(output_dir, f"{base_filename}.json")
    excel_file = os.path.join(output_dir, f"{base_filename}.xlsx")
    csv_file = os.path.join(output_dir, f"{base_filename}.csv")
    
    saved_files = {}
    
    try:
        # Guardar como JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        saved_files['json'] = json_file
        print(f"✓ Datos guardados en JSON: {json_file}")
        
        # Preparar datos para DataFrame
        flat_data = []
        for empresa, resultados in results_data['resultados'].items():
            if resultados:
                for i, resultado in enumerate(resultados):
                    if isinstance(resultado, dict) and 'error' not in resultado:
                        # Añadir información de la empresa y número de resultado
                        resultado_flat = {
                            'empresa_buscada': empresa,
                            'numero_resultado': i + 1,
                            **resultado
                        }
                        flat_data.append(resultado_flat)
                    elif isinstance(resultado, dict) and 'error' in resultado:
                        # Guardar errores también
                        flat_data.append({
                            'empresa_buscada': empresa,
                            'numero_resultado': i + 1,
                            'error': resultado['error']
                        })
        
        if flat_data:
            df = pd.DataFrame(flat_data)
            
            # Guardar como Excel
            try:
                with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Resultados SUNAT', index=False)
                    
                    # Si hay errores, crear una hoja separada
                    errors = results_data.get('errores', [])
                    if errors:
                        error_df = pd.DataFrame([{'error': error} for error in errors])
                        error_df.to_excel(writer, sheet_name='Errores', index=False)
                
                saved_files['excel'] = excel_file
                print(f"✓ Datos guardados en Excel: {excel_file}")
            except Exception as e:
                print(f"✗ Error guardando Excel: {str(e)}")
            
            # Guardar como CSV
            try:
                df.to_csv(csv_file, index=False, encoding='utf-8')
                saved_files['csv'] = csv_file
                print(f"✓ Datos guardados en CSV: {csv_file}")
            except Exception as e:
                print(f"✗ Error guardando CSV: {str(e)}")
        
        else:
            print("⚠️ No se encontraron datos válidos para guardar en Excel/CSV")
    
    except Exception as e:
        print(f"✗ Error general guardando archivos: {str(e)}")
    
    return saved_files

def save_summary_report(results_data: dict, saved_files: dict) -> str:
    """
    Genera un reporte resumen en texto plano
    """
    output_dir = "data/resultados"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f"reporte_{timestamp}.txt")
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("REPORTE DE CONSULTA SUNAT\n")
            f.write("="*60 + "\n")
            f.write(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Resumen de empresas procesadas
            total_empresas = len(results_data['resultados'])
            empresas_con_datos = 0
            empresas_con_errores = 0
            total_resultados = 0
            
            for empresa, resultados in results_data['resultados'].items():
                if resultados:
                    tiene_datos = False
                    for resultado in resultados:
                        if isinstance(resultado, dict):
                            if 'error' in resultado:
                                empresas_con_errores += 1
                            else:
                                tiene_datos = True
                                total_resultados += 1
                    if tiene_datos:
                        empresas_con_datos += 1
            
            f.write(f"Total de empresas consultadas: {total_empresas}\n")
            f.write(f"Empresas con datos encontrados: {empresas_con_datos}\n")
            f.write(f"Empresas con errores: {empresas_con_errores}\n")
            f.write(f"Total de resultados obtenidos: {total_resultados}\n\n")
            
            # Archivos generados
            f.write("ARCHIVOS GENERADOS:\n")
            f.write("-" * 20 + "\n")
            for formato, archivo in saved_files.items():
                f.write(f"- {formato.upper()}: {archivo}\n")
            
            # Errores encontrados
            if 'errores' in results_data and results_data['errores']:
                f.write(f"\nERRORES ENCONTRADOS ({len(results_data['errores'])}):\n")
                f.write("-" * 30 + "\n")
                for error in results_data['errores']:
                    f.write(f"- {error}\n")
        
        print(f"✓ Reporte generado: {report_file}")
        return report_file
        
    except Exception as e:
        print(f"✗ Error generando reporte: {str(e)}")
        return None