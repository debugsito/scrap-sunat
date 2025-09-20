from playwright.sync_api import sync_playwright
from playwright._impl._errors import Error as PlaywrightError
import time
import random
import os
from .parser import parse_resultado

def scrape_sunat(nombre: str, debug_mode: bool = False) -> list:
    """
    Scrapes SUNAT website for company information.
    Returns a list of results or error information.
    """
    results = []
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            with sync_playwright() as p:
                # Configure browser with more realistic settings
                # Check if we should run in debug mode (visible browser)
                debug_mode = debug_mode or os.getenv('SUNAT_DEBUG', 'false').lower() == 'true'
                
                browser = p.chromium.launch(
                    headless=not debug_mode,  # headless=False solo en debug mode
                    slow_mo=500 if debug_mode else 0,    # Slow motion solo en debug
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                # Create page with realistic user agent and viewport
                page = browser.new_page()
                page.set_viewport_size({"width": 1366, "height": 768})
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                })
                
                # Set reasonable timeout
                page.set_default_timeout(60000)  # Aumentado a 60 segundos
                
                print(f"Navegando a SUNAT para buscar: {nombre}")
                
                # Navigate to the page with wait until load
                page.goto(
                    "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp",
                    wait_until="networkidle"
                )
                
                # Wait for page to fully load
                print("Esperando que la página cargue completamente...")
                time.sleep(1.5)  # Reducido de 3 a 1.5 segundos
                
                # First, click on "Por Nomb./Raz.Soc." button to enable the search field
                print("Haciendo clic en 'Por Nomb./Raz.Soc.' para activar búsqueda por razón social...")
                page.wait_for_selector("#btnPorRazonSocial", state="visible", timeout=30000)
                page.click("#btnPorRazonSocial")
                time.sleep(0.5)  # Reducido de 1 a 0.5 segundos
                
                # Wait for the search input to be visible and interactable
                print("Esperando que el campo de búsqueda esté disponible...")
                
                # First wait for the element to exist
                page.wait_for_selector("#txtNombreRazonSocial", timeout=30000)
                
                # Then wait for it to be visible and enabled
                search_input = page.locator("#txtNombreRazonSocial")
                search_input.wait_for(state="visible", timeout=30000)
                
                # Check if there are any overlays or modals that might be blocking the element
                try:
                    # Look for common modal/overlay patterns that might block interaction
                    overlays = page.query_selector_all("[class*='modal'], [class*='overlay'], [class*='loading'], [class*='popup']")
                    if overlays:
                        print("Detectadas posibles ventanas modales, esperando que se cierren...")
                        time.sleep(1.5)  # Reducido de 3 a 1.5 segundos
                except:
                    pass
                
                # Scroll to the element to make sure it's in view
                search_input.scroll_into_view_if_needed()
                time.sleep(0.5)  # Reducido de 1 a 0.5 segundos
                
                # Try multiple approaches to interact with the element
                input_filled = False
                
                # Approach 1: Direct fill
                try:
                    print("Intentando llenar el campo directamente...")
                    search_input.fill(nombre, timeout=10000)
                    input_filled = True
                    print("✓ Campo llenado exitosamente")
                except Exception as e:
                    print(f"✗ Fallo el llenado directo: {str(e)}")
                
                # Approach 2: Click then type
                if not input_filled:
                    try:
                        print("Intentando click + type...")
                        search_input.click(timeout=10000)
                        time.sleep(0.3)  # Reducido de 0.5 a 0.3 segundos
                        search_input.clear()
                        search_input.type(nombre, delay=50)  # Reducido de 100 a 50ms
                        input_filled = True
                        print("✓ Campo llenado con click + type")
                    except Exception as e:
                        print(f"✗ Fallo click + type: {str(e)}")
                
                # Approach 3: JavaScript injection as last resort
                if not input_filled:
                    try:
                        print("Intentando inyección JavaScript...")
                        page.evaluate(f"""
                            const input = document.querySelector('#txtNombreRazonSocial');
                            if (input) {{
                                input.value = '{nombre}';
                                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }}
                        """)
                        input_filled = True
                        print("✓ Campo llenado con JavaScript")
                    except Exception as e:
                        print(f"✗ Fallo JavaScript: {str(e)}")
                        raise Exception(f"No se pudo llenar el campo de búsqueda después de múltiples intentos: {str(e)}")
                
                time.sleep(1)
                
                # Wait for search button to be visible and click it
                print("Haciendo click en buscar...")
                page.wait_for_selector("#btnAceptar", state="visible")
                page.click("#btnAceptar")
                
                # Wait for results with longer timeout
                print("Esperando resultados...")
                try:
                    page.wait_for_selector(".aRucs", timeout=20000)
                except:
                    # Try to check if there's a "no results" message
                    no_results = page.query_selector_all("text=No se encontraron")
                    if no_results:
                        browser.close()
                        return [{"error": "No se encontraron resultados para la búsqueda"}]
                    raise

                links = page.query_selector_all("a.aRucs")
                print(f"Encontrados {len(links)} resultados")
                
                if not links:
                    browser.close()
                    return [{"error": "No se encontraron resultados para la búsqueda"}]
                
                for i in range(len(links)):
                    try:
                        print(f"Procesando resultado {i+1} de {len(links)}")
                        # Add delay between requests - optimizado pero realista
                        time.sleep(random.uniform(1, 2.5))  # Reducido de (2, 4) a (1, 2.5)
                        
                        # Vuelve a buscar cada vez (porque DOM cambia tras regresar)
                        current_links = page.query_selector_all("a.aRucs")
                        if i < len(current_links):
                            # Scroll to the link to make sure it's visible
                            current_links[i].scroll_into_view_if_needed()
                            time.sleep(0.3)  # Reducido de 0.5 a 0.3 segundos
                            
                            print(f"Haciendo click en resultado {i+1}")
                            current_links[i].click()
                            
                            # Wait for detail page to load
                            print("Esperando que cargue la página de detalles...")
                            page.wait_for_selector(".panel.panel-primary", timeout=15000)
                            time.sleep(1)  # Reducido de 2 a 1 segundo

                            html = page.content()
                            result = parse_resultado(html)
                            results.append(result)
                            print(f"Datos extraídos para resultado {i+1}")

                            # Regresar al listado
                            print("Regresando al listado...")
                            page.go_back()
                            page.wait_for_selector(".aRucs", timeout=15000)
                            time.sleep(0.5)  # Reducido de 1 a 0.5 segundos
                        
                    except Exception as e:
                        print(f"Error procesando resultado {i+1}: {str(e)}")
                        results.append({"error": f"Error al procesar resultado {i+1}: {str(e)}"})
                        try:
                            page.go_back()
                            page.wait_for_selector(".aRucs", timeout=5000)
                            time.sleep(0.5)  # Reducido de 1 a 0.5 segundos
                        except:
                            print("No se pudo regresar al listado, terminando...")
                            break

                print(f"Scraping completado. Total de resultados: {len(results)}")
                browser.close()
                return results
                
        except PlaywrightError as e:
            error_msg = str(e)
            if "ERR_CONNECTION_RESET" in error_msg or "net::" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 1.5 + random.uniform(0.5, 2)  # Reducido los tiempos
                    print(f"Connection error, retrying in {wait_time:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    return [{"error": "Error de conexión: No se pudo conectar al sitio web de SUNAT. El servicio puede estar temporalmente no disponible."}]
            else:
                return [{"error": f"Error del navegador: {error_msg}"}]
                
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 1.5 + random.uniform(0.5, 2)  # Reducido los tiempos
                print(f"Unexpected error, retrying in {wait_time:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                return [{"error": f"Error inesperado: {str(e)}"}]
    
    return [{"error": "Se agotaron todos los intentos de conexión"}]
