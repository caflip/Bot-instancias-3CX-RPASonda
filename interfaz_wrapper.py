from Scripts.downloader import download_report
from Scripts.unificador import unificar_reportes
from Scripts.mailer import enviar_correo
from Scripts.utils import definirRuta, crear_directorio_si_no_existe, crearArchivoAuditoria
from dotenv import load_dotenv
from pathlib import Path
import os
import sys

# Preparar rutas
if getattr(sys, 'frozen', False):
    base_path = Path(sys.executable).parent
else:
    base_path = Path(__file__).parent

load_dotenv(base_path / '.env')

ruta_reportes = definirRuta(base_path, 'Reportes')
rutaAuditoria = definirRuta(base_path, 'Auditoria')
ruta_salida = definirRuta(base_path, 'Reportes/Reporte_Unificado')

crear_directorio_si_no_existe(ruta_reportes)
crear_directorio_si_no_existe(rutaAuditoria)
crear_directorio_si_no_existe(ruta_salida)

auditoria = crearArchivoAuditoria(rutaAuditoria)
fila_auditoria = 2

_3CX_USERNAME = os.getenv("3CX_USERNAME")
_3CX_PASSWORD = os.getenv("3CX_PASSWORD")

correo_saliente = os.getenv("MAIL_USERNAME")
contrasena_correo = os.getenv("MAIL_PASSWORD")
correo_destinatario = os.getenv("MAIL_TO")

def ejecutar(instancias, fecha_inicio, fecha_fin):

    global fila_auditoria

    estado_download, nombre_reportes, fila_auditoria = download_report(instancias, _3CX_USERNAME, _3CX_PASSWORD, fecha_inicio, fecha_fin,auditoria, ruta_reportes, fila_auditoria)

    if not estado_download or not nombre_reportes:
        raise Exception("Error al descargar los reportes")

    estado_unificacion, ruta_unificado, fila_auditoria = unificar_reportes(ruta_reportes, nombre_reportes, ruta_salida, auditoria, fila_auditoria)

    if not estado_unificacion:
        raise Exception("Error al unificar reportes")

    # estado_envio, fila_auditoria = enviar_correo(instancias, correo_saliente, contrasena_correo,correo_destinatario, ruta_unificado, auditoria, fila_auditoria)

    # if not estado_envio:
    #     raise Exception("Error al enviar el correo")

    return True
