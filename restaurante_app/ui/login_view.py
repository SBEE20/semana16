import tkinter as tk
from tkinter import ttk
from pathlib import Path


class LoginView:
    """
    Vista de acceso al sistema del restaurante (Semana 16).
    Incorpora recursos visuales de la carpeta assets/ (logotipo) y formulario
    de validación de credenciales con control de eventos de teclado (<Return>).
    """

    def __init__(self, root: tk.Tk, restaurante_servicio, cambiar_vista_callback, ruta_assets: Path = None):
        """
        Inicializa la vista de login.

        Args:
            root: Ventana principal de Tkinter
            restaurante_servicio: Instancia de RestauranteServicio para autenticación
            cambiar_vista_callback: Función de retorno para cambiar de vista
            ruta_assets: Ruta a la carpeta de recursos visuales
        """
        self.root = root
        self.restaurante_servicio = restaurante_servicio
        self.cambiar_vista_callback = cambiar_vista_callback
        self.ruta_assets = ruta_assets or (Path(__file__).resolve().parent.parent / "assets")

        self.frame = None
        self.entry_usuario = None
        self.entry_password = None
        self.label_error = None
        self.img_logo = None

    def mostrar(self) -> None:
        """Despliega la interfaz de inicio de sesión en la ventana principal."""
        # Limpiar la ventana
        for widget in self.root.winfo_children():
            widget.destroy()

        # Contenedor principal de la vista
        self.frame = tk.Frame(self.root, bg="#eceff1")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Contenedor central (tarjeta de acceso)
        card_frame = tk.Frame(self.frame, bg="#ffffff", bd=2, relief=tk.GROOVE)
        card_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=470, height=540)

        # Encabezado del login
        header_frame = tk.Frame(card_frame, bg="#0f172a", height=115)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Cargar logotipo desde assets/
        ruta_logo = self.ruta_assets / "logo.png"
        if ruta_logo.exists():
            try:
                self.img_logo = tk.PhotoImage(file=str(ruta_logo))
                lbl_logo = tk.Label(header_frame, image=self.img_logo, bg="#0f172a")
                lbl_logo.pack(side=tk.LEFT, padx=(20, 10), pady=15)
            except Exception as e:
                print(f"Nota: No se pudo cargar imagen de logo: {e}")
                self.img_logo = None

        header_text_frame = tk.Frame(header_frame, bg="#0f172a")
        header_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=18)

        tk.Label(
            header_text_frame,
            text="RESTAURANTE APP",
            font=("Segoe UI", 15, "bold"),
            bg="#0f172a",
            fg="#f8fafc",
            anchor=tk.W
        ).pack(fill=tk.X)

        tk.Label(
            header_text_frame,
            text="Semana 16 • Manejo de Eventos en Tkinter",
            font=("Segoe UI", 9),
            bg="#0f172a",
            fg="#38bdf8",
            anchor=tk.W
        ).pack(fill=tk.X)

        tk.Label(
            header_text_frame,
            text="Gestión de Usuarios con Eventos y Roles",
            font=("Segoe UI", 8),
            bg="#0f172a",
            fg="#94a3b8",
            anchor=tk.W
        ).pack(fill=tk.X)

        # Contenedor del formulario
        form_frame = tk.Frame(card_frame, bg="#ffffff")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=35, pady=18)

        # Campo: Usuario
        tk.Label(
            form_frame,
            text="Nombre de Usuario:",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#334155"
        ).pack(anchor=tk.W, pady=(5, 3))

        self.entry_usuario = ttk.Entry(form_frame, font=("Segoe UI", 11))
        self.entry_usuario.pack(fill=tk.X, pady=(0, 12), ipady=3)
        self.entry_usuario.bind("<Return>", lambda e: self.intentar_acceso())

        # Campo: Contraseña
        tk.Label(
            form_frame,
            text="Contraseña:",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#334155"
        ).pack(anchor=tk.W, pady=(0, 3))

        self.entry_password = ttk.Entry(form_frame, font=("Segoe UI", 11), show="•")
        self.entry_password.pack(fill=tk.X, pady=(0, 8), ipady=3)
        self.entry_password.bind("<Return>", lambda e: self.intentar_acceso())

        # Etiqueta de mensajes de error o advertencia
        self.label_error = tk.Label(
            form_frame,
            text="",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#dc2626",
            wraplength=370,
            justify=tk.CENTER
        )
        self.label_error.pack(pady=4)

        # Botón de ingreso con command=
        btn_ingresar = tk.Button(
            form_frame,
            text="Iniciar Sesión",
            font=("Segoe UI", 11, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.intentar_acceso
        )
        btn_ingresar.pack(fill=tk.X, pady=(8, 12), ipady=6)

        # Contenedor de credenciales de prueba con roles
        info_frame = tk.Frame(card_frame, bg="#f8fafc", bd=1, relief=tk.SOLID)
        info_frame.pack(fill=tk.X, padx=25, pady=(0, 18))

        tk.Label(
            info_frame,
            text="Credenciales de acceso con diferentes roles:\n"
                 "👑 admin / admin123 (Administrador)\n"
                 "👔 gerente / gerente123 (Empleado)  |  mesero / mesero123 (Empleado)\n"
                 "👤 cliente1 / cliente123 (Cliente)",
            font=("Segoe UI", 8),
            bg="#f8fafc",
            fg="#475569",
            justify=tk.CENTER
        ).pack(pady=6)

        # Foco inicial
        self.entry_usuario.focus()

    def intentar_acceso(self) -> None:
        """Valida las credenciales ingresadas mediante el servicio."""
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()

        if not usuario or not password:
            self.mostrar_error("Por favor, ingrese el usuario y la contraseña.")
            return

        if self.restaurante_servicio.validar_acceso(usuario, password):
            self.limpiar_campos()
            self.cambiar_vista_callback("main", usuario)
        else:
            self.mostrar_error("Credenciales incorrectas. Verifique e intente nuevamente.")
            self.entry_password.delete(0, tk.END)
            self.entry_password.focus()

    def mostrar_error(self, mensaje: str) -> None:
        """Muestra un mensaje de advertencia o error en la interfaz."""
        if self.label_error:
            self.label_error.config(text=f"⚠️ {mensaje}")

    def limpiar_campos(self) -> None:
        """Limpia los campos y estados del formulario de login."""
        if self.entry_usuario:
            self.entry_usuario.delete(0, tk.END)
        if self.entry_password:
            self.entry_password.delete(0, tk.END)
        if self.label_error:
            self.label_error.config(text="")
