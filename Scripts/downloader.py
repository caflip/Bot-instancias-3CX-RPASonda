from Scripts.login import login_3cx
from playwright.sync_api import sync_playwright
import Scripts.utils as RPA
from pathlib import Path
import pandas as pd
from datetime import datetime

URLS = {
    "VIP": "https://movigoo02.telco.convergia.io/#/office/reports/call-reports",
    "Instancia 1": "https://movigoo03.telco.convergia.io/#/office/reports/call-reports",
    "Instancia 2": "https://movigoo04.telco.convergia.io/#/office/reports/call-reports",
    "Instancia 3": "https://movigoo-sonda-olimpica.telco.convergia.io/#/office/reports/call-reports",
}

def parse_fecha_generica(fecha_str):
    if not fecha_str:
        return None

    formatos = ["%m/%d/%Y"]
    for fmt in formatos:
        try:
            return datetime.strptime(fecha_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Formato de fecha no soportado: {fecha_str}")

def analizar_csv_paginacion(ruta_csv, fecha_inicio_str, limite_registros=20000):
    df = pd.read_csv(ruta_csv)

    # Quitar filas "Totals"
    mask_totals = df.apply(
        lambda row: row.astype(str).str.contains("Totals", case=False, na=False).any(),
        axis=1
    )
    df = df[~mask_totals]

    num_registros = len(df)

    if num_registros == 0:
        return 0, None, parse_fecha_generica(fecha_inicio_str)

    # Último registro real = fecha más antigua de ese CSV
    oldest_call_str = str(df["Call Time"].iloc[-1]).strip()

    oldest_date = None
    try:
        # Usualmente viene como 2025-11-20T23:48:43
        oldest_date = datetime.fromisoformat(oldest_call_str).date()
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                oldest_date = datetime.strptime(oldest_call_str, fmt).date()
                break
            except ValueError:
                continue

    if oldest_date is None:
        raise ValueError(f"No se pudo interpretar la fecha de Call Time: {oldest_call_str}")

    fecha_inicio_date = parse_fecha_generica(fecha_inicio_str)

    return num_registros, oldest_date, fecha_inicio_date



def download_report(instancias, _3CX_USERNAME, _3CX_PASSWORD,
                    fecha_inicio, fecha_fin, auditoria, ruta_reportes, fila_auditoria):
    nombres_reportes = []
    try:
        with sync_playwright() as p:
            chromium_path = Path.home() / "AppData/Local/ms-playwright/chromium-1181/chrome-win/chrome.exe"
            browser = p.chromium.launch(
                executable_path=str(chromium_path),
                headless=True,
                args=["--start-maximized"]
            )

            # recorrer las instancias
            for instancia in instancias:
                page = browser.new_page(no_viewport=True)
                login = login_3cx(page, URLS[instancia], _3CX_USERNAME, _3CX_PASSWORD)

                # Validar login
                if login[0] is False:
                    fila_auditoria = RPA.diligenciarAuditoria(
                        auditoria,
                        [instancia, login[1]],
                        fila_auditoria
                    )
                    page.close()
                    continue

                # Si NO hay filtro de fechas → una sola descarga como antes
                if not (fecha_inicio and fecha_fin):
                    with page.expect_download(timeout=30000) as download_info:
                        page.locator('[data-qa="export-report"]').click()
                    download = download_info.value

                    nombre_archivo = f"reporte_{instancia.replace(' ', '_').lower()}.csv"
                    ruta_destino = Path(ruta_reportes) / nombre_archivo
                    download.save_as(str(ruta_destino))
                    nombres_reportes.append(nombre_archivo)

                    page.close()
                    continue

                # --- Hay filtro de fechas: paginación por límite de 20k ---
                fecha_inicio_original = fecha_inicio   # la del usuario
                fecha_fin_original = fecha_fin
                fecha_fin_actual = fecha_fin_original  # esta es la que vamos moviendo hacia atrás

                parte = 1
                hay_mas_datos = True

                while hay_mas_datos:
                    # Abrir panel de filtro
                    page.locator('[data-qa="toggle-filter"]').click()
                    page.wait_for_timeout(500)

                    seleccion_lista = RPA.seleccionar_personalizado(page)

                    if not seleccion_lista:
                        print("No se pudo aplicar el filtro de fechas")
                        fila_auditoria = RPA.diligenciarAuditoria(
                            auditoria,
                            [instancia, "No se pudo seleccionar el filtro 'Personalizado/Custom'"],
                            fila_auditoria
                        )
                        break

                    # Adaptar formato de fecha según instancia
                    # IMPORTANTE: fecha_inicio se mantiene, movemos solo fecha_fin_actual
                    fecha_inicio_fmt, fecha_fin_fmt = RPA.adaptar_formato_fecha(
                        instancia,
                        fecha_inicio_original,
                        fecha_fin_actual
                    )

                    # limpiar el campo de fechas
                    campo_fechas = page.locator(
                        '//*[@id="app-container"]/app-office-layout/app-layout-type3/div[2]/div/ng-component/app-page/app-complex-filter/app-odata-search/div/div[2]/div/div/div[1]/app-date-range-filter/div/div/field-wrapper/div[1]/div/input'
                    )
                    campo_fechas.fill('')
                    page.wait_for_timeout(500)

                    # ingresar nuevo rango
                    campo_fechas.fill(f"{fecha_inicio_fmt} - {fecha_fin_fmt}")

                    # click buscar
                    page.locator(
                        '//*[@id="app-container"]/app-office-layout/app-layout-type3/div[2]/div/ng-component/app-page/app-complex-filter/app-odata-search/div/div[2]/div/div/div[2]/button[1]'
                    ).click()
                    page.wait_for_timeout(10000)  # esperar a que se aplique el filtro

                    # descargar
                    with page.expect_download(timeout=30000) as download_info:
                        page.locator('[data-qa="export-report"]').click()
                    download = download_info.value

                    # nombre de archivo con parte
                    nombre_archivo = f"reporte_{instancia.replace(' ', '_').lower()}_part{parte}.csv"
                    ruta_destino = Path(ruta_reportes) / nombre_archivo
                    download.save_as(str(ruta_destino))
                    nombres_reportes.append(nombre_archivo)

                    # Analizar CSV para saber si necesitamos otro bloque
                    try:
                        num_registros, oldest_date, fecha_inicio_date = analizar_csv_paginacion(
                            str(ruta_destino),
                            fecha_inicio_original,
                            limite_registros=20000
                        )
                    except Exception as e_csv:
                        print(f"Error analizando CSV para paginación: {e_csv}")
                        # Por seguridad, salir del bucle de esta instancia
                        break

                    # === LÓGICA DE PARADA / CONTINUIDAD ===
                    # 1) Si trae menos de 20k registros → no hay truncamiento
                    # 2) Si la fecha más antigua ya es <= fecha_inicio del filtro → ya cubrimos todo el rango
                    if num_registros < 20000 or (oldest_date is not None and oldest_date <= fecha_inicio_date):
                        hay_mas_datos = False
                    else:
                        # Caso crítico: seguimos truncados dentro del rango del filtro
                        # ⇒ mover fecha_fin_actual hacia atrás hasta oldest_date
                        fecha_fin_actual = oldest_date.strftime("%m/%d/%Y")
                        parte += 1

                page.close()

            browser.close()

        # Auditoría
        if nombres_reportes:
            fila_auditoria = RPA.diligenciarAuditoria(
                auditoria,
                ["Descarga de reportes", "Reportes descargados: " + ", ".join(nombres_reportes)],
                fila_auditoria
            )
        else:
            fila_auditoria = RPA.diligenciarAuditoria(
                auditoria,
                ["Descarga de reportes", "No se descargaron reportes"],
                fila_auditoria
            )

        return True, nombres_reportes, fila_auditoria

    except Exception as e:
        print(f"Error al descargar reportes: {e}")
        fila_auditoria = RPA.diligenciarAuditoria(
            auditoria,
            ["Descarga de reportes", str(e)],
            fila_auditoria
        )
        return False, [], fila_auditoria
