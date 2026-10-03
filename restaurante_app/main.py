import tkinter as tk
from pathlib import Path
import sys

# Asegurar que el directorio del proyecto esté en sys.path
DIRECTORIO_RAIZ = Path(__file__).resolve().parent
if str(DIRECTORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRECTORIO_RAIZ))

from servicios.archivo_servicio import ArchivoServicio
from servicios.restaurante_servicio import RestauranteServicio
from ui.login_view import LoginView
from ui.main_view import MainView


class AplicacionRestaurante:
    """
    Coordinador principal del ciclo de vida de la aplicación (Semana 16).
    Instancia una única ventana Tkinter, inicializa las capas de servicios,
    recursos visuales de assets/ y coordina el cambio entre las vistas (LoginView y MainView).
    """

    def __init__(self, root: tk.Tk):
        """
        Inicializa la aplicación y sus dependencias.

        Args:
            root: Ventana principal de Tkinter
        """
        self.root = root
        self.root.title("Sistema de Gestión de Restaurante - Semana 16 (Manejo de Eventos y Gestión de Usuarios)")
        self.root.geometry("1100x720")
        self.root.minsize(980, 640)

        # Rutas absolutas a datos y recursos visuales
        ruta_datos = DIRECTORIO_RAIZ / "datos"
        ruta_assets = DIRECTORIO_RAIZ / "assets"

        # Configurar icono de ventana si existe en assets
        ruta_logo = ruta_assets / "logo.png"
        if ruta_logo.exists():
            try:
                self.icono_app = tk.PhotoImage(file=str(ruta_logo))
                self.root.iconphoto(False, self.icono_app)
            except Exception as e:
                print(f"Nota: No se pudo configurar el icono de la ventana: {e}")

        # Inicialización de la capa de servicios
        self.archivo_servicio = ArchivoServicio(str(ruta_datos))
        self.restaurante_servicio = RestauranteServicio(self.archivo_servicio)

        # Inicialización de las vistas de la capa de interfaz
        self.login_view = LoginView(
            self.root,
            self.restaurante_servicio,
            self.cambiar_vista,
            ruta_assets=ruta_assets
        )
        self.main_view = MainView(
            self.root,
            self.restaurante_servicio,
            self.cambiar_vista,
            ruta_assets=ruta_assets
        )

        # Iniciar mostrando la vista de autenticación
        self.login_view.mostrar()

    def cambiar_vista(self, nombre_vista: str, usuario: str = None) -> None:
        """
        Gestiona la transición fluida entre vistas sin abrir ventanas adicionales.

        Args:
            nombre_vista: 'login' o 'main'
            usuario: Nombre del usuario autenticado (requerido para 'main')
        """
        if nombre_vista == "login":
            self.login_view.mostrar()
        elif nombre_vista == "main" and usuario:
            self.main_view.mostrar(usuario)


def main():
    """Punto de entrada oficial de la aplicación."""
    root = tk.Tk()
    app = AplicacionRestaurante(root)
    root.mainloop()


if __name__ == "__main__":
    main()
