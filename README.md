# Bot Automatización de Reportes 3CX RPASonda

## 1. Descripción general

Este proyecto es una herramienta de automatización para descargar, unificar y enviar por correo reportes de llamadas de la plataforma 3CX.
Permite trabajar en modo consola y modo interfaz gráfica, e incluye lógica para seleccionar rangos de fechas personalizados y combinar varios reportes en uno solo.

El objetivo principal es ahorrar tiempo y eliminar procesos manuales repetitivos.

## 2. Funcionalidades Principales
- **Login automático**: Iniciar sesión automáticamente en cada instancia de 3CX.
- **Seleccion automatica de fechas**: Seleccionar fechas de inicio y fin de reporte.
- **Seleccion de reportes**: Seleccionar los reportes a descargar.
- **Descarga de múltiples reportes en diferentes URLs.**
- **Unificar reportes**: Unir varios reportes en uno solo (si aplica).
- **Enviar por correo**: Enviar el reporte unificado por correo electrónico.
- **Guardar reportes**: Guardar los reportes en un directorio específico.
- **Interfaz gráfica**: Interfaz gráfica para seleccionar fechas y reportes.

## 3. Estructura del proyecto
```
    📂 proyecto/
    │── 📄 main.py
    │── 📄 interfaz.py
    │── 📄 interfaz_wrapper.py
    │── 📄 test.py
    │── 📄 .env
    │── 📄 requirements.txt
    │── 📄 README.md
    📂 reportes/
        │── 📂 Reporte Unificado/
    📂 Auditoria/
    📂 scripts/
        │── 📄 downloader.py
        │── 📄 login.py
        │── 📄 mailer.py
        │── 📄 unificador.py
        │── 📄 utils.py
```

## 4. Descripción de Archivos

**main.py**
- **Rol**: Punto de entrada en modo consola.
- **Funci+on**: Coordina la ejecución de los módulos (login.py, downloader, unificador, mailer).

**downloader.py**
- **Rol**: Encargado de **navegar** por las URLs, aplicar filtros y descargar los reportes.
- **Tecnología**: Playwright.
- **Características especiales**:
    - Selección robusta del filtro **"Personalizado"** en ng-select con IDs dinámicos.
    - Manejo de múltiples URLs con la misma lógica.
    - Guarda archivos en la carpeta /reportes.

**login.py**
- **Rol**: Realiza el inicio de sesión en 3CX.
- **Función**: Abre la sesión y devuelve una instancia del navegador lista para descargar.

**mailer.py**
- **Rol**: Envía por correo los reportes generados.
- **Tecnología**: SMTP (configurado desde .env).
**Parámetros**: destinatarios, asunto, cuerpo y archivos adjuntos.

**unificador.py**
- **Rol**: Une varios reportes en un solo archivo Excel.
- **Tecnología**: Pandas.
- **Funcionalidad extra**: Elimina duplicados.

**utils.py**
- **Rol**: Contiene funciones de apoyo para formatear fechas, manejar rutas, logs, y selección dinámica en Angular ng-select.

**interfaz.py**
- **Rol**: Proporciona una interfaz gráfica local.
- **Características**:
    - Selección de instancias con checkboxes.
    - Selección de fechas en calendario.
    - Botón de ejecución que lanza el flujo completo.

**interfaz_wrapper.py**
- **Rol*: Adaptador para empaquetar la interfaz con PyInstaller y garantizar que recursos como iconos y plantillas se incluyan.

**test.py**
- **Rol**: Pruebas rápidas para verificar funcionamiento de módulos.
- **Ejemplo de prueba**:
    - Login correcto.
    - Descarga de un reporte.
    - Unificación de dos reportes.
    - Envío de correo de prueba.

**.env**
- **Rol**: Contiene credenciales y configuración sensible.
- **Variables típicas**: 
    ```
    3CX_USERNAME=example@example.com
    3CX_PASSWORD=example
    MAIL_USERNAME=example@example.com
    MAIL_PASSWORD=example
    MAIL_TO=example@example.com
    ```

## 5. Intalación

#### Requisitos previos
- Python 3.13.4
- Navegador Chromium (Instalado automatizamnete por Playwright)
- Whindows 10/11 

#### Pasos
```
# 1. Descomprimir .zip en directorio raiz del proyecto

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar credenciales
.env modificar valores

# 5. Instalar navegadores de Playwright
playwright install

```

## 6. Uso

#### Modo consola
```
python main.py
```

### Modo interfaz gráfica
```
python interfaz.py
```

## 7. Compilación a .exe
### Crear el .spec personalizado
Ejecutar una solo una vez para generar el .spec
```
pyinstaller interfaz.py --noconfirm --onefile --windowed
```
Esto genera un archivo .spec que se puede modificar para ajustar la configuración.
Incluir directorios adicionales (Scripts, .env, etc.)
```
# En interfaz.spec
a = Analysis(
    ['interfaz.py'],
    ...
    datas=[
        ('Scripts/*.py', 'Scripts'),  # incluye Scripts
        ('.env', '.'),                # incluye archivo de entorno
    ],
    ...
)
```
### Recomendaciones de opciones para el .exe
| Opción       | Descripción                                                                |
| ------------ | -------------------------------------------------------------------------- |
| `--onefile`  | Empaqueta todo en un único `.exe`                                          |
| `--windowed` | Evita que se abra la consola al iniciar (ideal para GUI con Tkinter)       |
| `--add-data` | Para incluir archivos adicionales: `.env`, íconos, carpetas como `Scripts` |

### Recompilar
```
pyinstaller interfaz.spec --noconfirm --clean
```

Esto genera un archivo `.exe` que puede ejecutar en cualquier máquina con Python instalado.

Se encuentra en la carpeta:
```
proyecto/dist/
```