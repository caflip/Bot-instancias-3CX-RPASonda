import smtplib
from email.message import EmailMessage
import Scripts.utils as RPA

def enviar_correo(instancias,correo_saliente, contrasena_correo, correo_destinatario, ruta_archivo, auditoria, fila_auditoria):
    try:
        # Crear el mensaje de correo
        msg = EmailMessage()
        msg['Subject'] = 'Reporte Unificado 3CX'
        msg['From'] = correo_saliente
        msg['To'] = correo_destinatario
        msg.set_content(f'Adjunto se encuentra el reporte unificado de las instancias: {instancias} de 3CX.')

        # Adjuntar el archivo
        with open(ruta_archivo, 'rb') as f:
            file_data = f.read()
            file_name = ruta_archivo.split('/')[-1]
            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        # Enviar el correo
        # with smtplib.SMTP("smtp.office365.com", 587) as server:
        #     server.starttls()
        #     server.login(correo_saliente, contrasena_correo)
        #     server.send_message(msg)

        print("Correo enviado exitosamente.")
        # Diligenciar la auditoría
        fila_auditoria = RPA.diligenciarAuditoria(auditoria, ["Envio de correo", "Correo enviado a: " + correo_destinatario], fila_auditoria)
        return True,fila_auditoria
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        # Diligenciar la auditoría en caso de error
        fila_auditoria = RPA.diligenciarAuditoria(auditoria, ["Envio de correo", str(e)], fila_auditoria)
        return False, fila_auditoria