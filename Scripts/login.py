# Función para autenticar en la instancia de 3CX
import re
from playwright.sync_api import Page

def login_3cx(page: Page, url_instancia: str, username: str, password: str):
    """Inicia sesión en la instancia de 3CX
    Args:
        page (Page): La página Playwright que se utiliza para interactuar con la instancia de 3CX.
        url_instancia (str): URL de la instancia de 3CX.
        username (str): Nombre de usuario para iniciar sesión.
        password (str): Contraseña para iniciar sesión.
    """
    try:
        # navegar a la URL de la instancia
        page.goto(url_instancia)
        # ingresar usuario
        page.locator('id=loginInput').fill(username)
        # ingresar contraseña
        page.locator('id=passwordInput').fill(password)
        # click iniciar sesión
        page.locator('id=submitBtn').click()
        #cerrar modal solo si aparce
        try:
            page.locator('[data-qa="modal-ok"]').click(timeout=5000)
        except Exception as e:
            print("No se encontró el modal")
        return [True,'']
    except Exception as e:
        print(f"Error al iniciar sesión en la instancia {url_instancia}: {e}")
        return [False, f"Error al iniciar sesión en la instancia {url_instancia}: {e}"]



