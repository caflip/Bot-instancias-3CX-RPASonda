from Scripts.login import login_3cx
from Scripts.downloader import download_report
from Scripts.unificador import unificar_reportes
from Scripts.mailer import enviar_correo
from playwright.sync_api import sync_playwright
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import Scripts.utils as RPA

# Detectar ruta base (tanto para .py como para .exe)
if getattr(sys, 'frozen', False):
    base_path = Path(sys.executable).parent
else:
    base_path = Path(__file__).parent

dotenv_path = base_path / '.env'
# Cargar las variables de entorno desde el archivo .env
load_dotenv(dotenv_path)

# Definir rutas basadas en base_path
ruta_reportes = RPA.definirRuta(base_path, 'Reportes')
rutaAuditoria = RPA.definirRuta(base_path, 'Auditoria')
ruta_salida = RPA.definirRuta(base_path, 'Reportes/Reporte_Unificado')

# Validar que existan las rutas necesarias
RPA.crear_directorio_si_no_existe(ruta_reportes)
RPA.crear_directorio_si_no_existe(rutaAuditoria)
RPA.crear_directorio_si_no_existe(ruta_salida)

#crear archivo de auditoria
auditoria = RPA.crearArchivoAuditoria(rutaAuditoria)
# definir fila inicial para la auditoría
fila_auditoria = 2

# Obtener las credenciales de 3CX desde las variables de entorno
_3CX_USERNAME = os.getenv("3CX_USERNAME")
_3CX_PASSWORD = os.getenv("3CX_PASSWORD")

# obtener informacion del envio de correo
correo_saliente = os.getenv("MAIL_USERNAME")
contrasena_correo = os.getenv("MAIL_PASSWORD")
correo_destinatario = os.getenv("MAIL_TO")

def test_download_report(_3CX_USERNAME,_3CX_PASSWORD, auditoria, ruta_reportes, fila_auditoria):
    instancias = ["VIP", "Instancia 1", "Instancia 2", "Instancia 3"]
    fecha_inicio = "08/01/2025"
    fecha_fin = "08/06/2025"
    estado_download, nombre_reportes, fila_auditoria = download_report(instancias,_3CX_USERNAME,_3CX_PASSWORD, fecha_inicio, fecha_fin, auditoria, ruta_reportes, fila_auditoria)
    print("Reportes descargados:", nombre_reportes)

def test_unificar_reportes(ruta_reportes, ruta_salida, auditoria, fila_auditoria):
    nombre_reportes = ['reporte_vip.csv', 'reporte_instancia_1.csv', 'reporte_instancia_2.csv', 'reporte_instancia_3.csv'] 
    estado_unificacion, ruta_unificado, fila_auditoria = unificar_reportes(ruta_reportes, nombre_reportes, ruta_salida, auditoria, fila_auditoria)
    print("Ruta del reporte unificado:", ruta_unificado)

def test_enviar_correo(ruta_salida, auditoria, fila_auditoria):
    instancias = ["VIP", "Instancia 1", "Instancia 2", "Instancia 3"]
    fila_auditoria = enviar_correo(instancias,correo_saliente, contrasena_correo, correo_destinatario, ruta_salida, auditoria, fila_auditoria)
    print("Correo enviado a:", correo_destinatario)


if __name__ == "__main__":
    # test_login_3cx()
    # test_download_report(_3CX_USERNAME,_3CX_PASSWORD, auditoria, ruta_reportes, fila_auditoria)
    test_unificar_reportes(ruta_reportes, ruta_salida, auditoria, fila_auditoria)
    # test_enviar_correo(ruta_salida, auditoria, fila_auditoria)
