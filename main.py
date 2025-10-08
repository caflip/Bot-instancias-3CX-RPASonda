from Scripts.downloader import download_report
from Scripts.unificador import unificar_reportes
from Scripts.mailer import enviar_correo
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import Scripts.utils as RPA
from rich.prompt import Prompt
from rich.console import Console

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

console = Console() # crear una instancia de la clase Console

def main(ruta_reportes, ruta_salida, auditoria, fila_auditoria, _3CX_USERNAME, _3CX_PASSWORD, correo_saliente, contrasena_correo, correo_destinatario):
    console.print("[bold cyan]Bienvenido a la herramienta de descarga de reportes instancias 3CX[/bold cyan]")

    instancias = {
        "1": "VIP",
        "2": "Instancia 1",
        "3": "Instancia 2",
        "4": "Instancia 3"
    }

    seleccion = Prompt.ask("Seleccione instancias separadas por coma (1-4)", default="1")
    seleccion_ids = seleccion.split(",") # dividir la cadena en una lista de IDs
    instancias_seleccionadas = []

    for id in seleccion_ids:
        id_ = id.strip() # Eliminar espacios en blanco
        if id_ in instancias:
            instancias_seleccionadas.append(instancias[id_])

    usar_fechas = Prompt.ask("¿Desea usar fechas de inicio y fin? (s/n)", default="n").lower() == "s"
    if usar_fechas:
        fecha_inicio = Prompt.ask("Ingrese la fecha de inicio (formato: MM/DD/YYYY)")
        fecha_fin = Prompt.ask("Ingrese la fecha de fin (formato: MM/DD/YYYY)")
    else:
        fecha_inicio = None
        fecha_fin = None
    
    #descargar reportes
    estado_download, nombre_reportes, fila_auditoria = download_report(instancias_seleccionadas,_3CX_USERNAME,_3CX_PASSWORD, fecha_inicio, fecha_fin, auditoria, ruta_reportes, fila_auditoria)
    if estado_download and len(nombre_reportes) > 0:
        console.print(f"[bold green]Reportes descargados exitosamente: {nombre_reportes}[/bold green]")
        #unificar reportes
        estado_unificacion, ruta_unificado, fila_auditoria = unificar_reportes(ruta_reportes, nombre_reportes, ruta_salida, auditoria, fila_auditoria)
        if estado_unificacion and ruta_unificado != None:
            console.print(f"[bold green]Reporte unificado creado en: {ruta_unificado}[/bold green]")
            # #enviar correo
            # estado_envio, fila_auditoria = enviar_correo(instancias_seleccionadas,correo_saliente, contrasena_correo, correo_destinatario, ruta_unificado, auditoria, fila_auditoria)
            # if estado_envio:
            #     console.print(f"[bold green]Correo enviado exitosamente a: {correo_destinatario}[/bold green]")
            # else:
            #     console.print("[bold red]Error al enviar el correo.[/bold red]")
        else:
            console.print("[bold red]Error al unificar los reportes.[/bold red]")
    else:
        console.print("[bold red]Error al descargar los reportes.[/bold red]")

if __name__ == "__main__":
    main(ruta_reportes, ruta_salida, auditoria, fila_auditoria, _3CX_USERNAME, _3CX_PASSWORD, correo_saliente, contrasena_correo, correo_destinatario)
    console.print("[bold cyan]Proceso finalizado.[/bold cyan]")



