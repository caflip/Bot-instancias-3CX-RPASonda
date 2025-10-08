from Scripts.login import login_3cx
from playwright.sync_api import sync_playwright
import Scripts.utils as RPA
from pathlib import Path



URLS = {
    "VIP": "https://movigoo02.telco.convergia.io/#/office/reports/call-reports",
    "Instancia 1": "https://movigoo03.telco.convergia.io/#/office/reports/call-reports",
    "Instancia 2": "https://movigoo04.telco.convergia.io/#/office/reports/call-reports",
    "Instancia 3": "https://movigoo-sonda-olimpica.telco.convergia.io/#/office/reports/call-reports",
}


def download_report(instancias,_3CX_USERNAME,_3CX_PASSWORD, fecha_inicio, fecha_fin, auditoria, ruta_reportes, fila_auditoria):
    nombres_reportes = []
    try:
        with sync_playwright() as p:

            chromium_path = Path.home() / "AppData/Local/ms-playwright/chromium-1181/chrome-win/chrome.exe"
            browser = p.chromium.launch(executable_path=str(chromium_path), headless=False, args=["--start-maximized"])

            #recorrer las intancias
            for instancia in instancias:

                # Crear una nueva página en el navegador
                page = browser.new_page(no_viewport=True)
                login = login_3cx(page, URLS[instancia], _3CX_USERNAME, _3CX_PASSWORD)

                # Validar si el login fue exitoso
                if login[0] is False:
                    fila_auditoria =RPA.diligenciarAuditoria(auditoria, [instancia, login[1]],fila_auditoria)
                    continue

                # validar si se desea con filtros
                if fecha_inicio and fecha_fin:

                    # aplicar filtro
                    page.locator('[data-qa="toggle-filter"]').click()
                    page.wait_for_timeout(500)
                    seleccion_lista = RPA.seleccionar_personalizado(page)
                    
                    # ingresar fechas (mmm/dd/yyyy - mmm/dd/yyyy)
                    if seleccion_lista:
                        # Convertir fecha según instancia
                        fecha_inicio_fmt, fecha_fin_fmt = RPA.adaptar_formato_fecha(instancia, fecha_inicio, fecha_fin)

                        #limpiar el campo de fechas
                        page.locator('//*[@id="app-container"]/app-office-layout/app-layout-type3/div[2]/div/ng-component/app-page/app-complex-filter/app-odata-search/div/div[2]/div/div/div[1]/app-date-range-filter/div/div/field-wrapper/div[1]/div/input').fill('')
                        page.wait_for_timeout(500)
                        #Ingresar nuevo valor 
                        page.locator('//*[@id="app-container"]/app-office-layout/app-layout-type3/div[2]/div/ng-component/app-page/app-complex-filter/app-odata-search/div/div[2]/div/div/div[1]/app-date-range-filter/div/div/field-wrapper/div[1]/div/input').fill(f"{fecha_inicio_fmt} - {fecha_fin_fmt}")
                        #click buscarg
                        page.locator('//*[@id="app-container"]/app-office-layout/app-layout-type3/div[2]/div/ng-component/app-page/app-complex-filter/app-odata-search/div/div[2]/div/div/div[2]/button[1]').click()
                        page.wait_for_timeout(10000)  # Esperar a que se aplique el filtro
                    else:
                        print("No se pudo aplicar el filtro de fechas")
                        fila_auditoria = RPA.diligenciarAuditoria(auditoria,[instancia, "No se pudo seleccionar el filtro 'Personalizado/Custom'"],fila_auditoria)
                        continue
                

                # Iniciar escucha antes del clic
                with page.expect_download(timeout=30000) as download_info:
                    page.locator('[data-qa="export-report"]').click()
                download = download_info.value


                # Definir nombre y ruta personalizada
                nombre_archivo = f"reporte_{instancia.replace(' ', '_').lower()}.csv"
                ruta_destino = Path(ruta_reportes) / nombre_archivo

                # Guardar el archivo
                download.save_as(str(ruta_destino))
                nombres_reportes.append(nombre_archivo) 
                
                page.close()
            browser.close()

        # Auditoria
        if nombres_reportes:
            # Diligenciar la auditoría
            fila_auditoria = RPA.diligenciarAuditoria(auditoria, ["Descarga de reportes", "Reportes descargados: " + ", ".join(nombres_reportes)], fila_auditoria)
        else:
            fila_auditoria = RPA.diligenciarAuditoria(auditoria, ["Descarga de reportes", "No se descargaron reportes"], fila_auditoria)
    
        return True, nombres_reportes, fila_auditoria
    except Exception as e:
        print(f"Error al descargar reportes: {e}")
        fila_auditoria = RPA.diligenciarAuditoria(auditoria, ["Descarga de reportes", str(e)], fila_auditoria)
        return False, [], fila_auditoria
    