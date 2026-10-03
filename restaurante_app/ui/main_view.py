import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Optional


class MainView:
    """
    Vista principal del sistema de restaurante (Semana 16).
    Evolución integral con manejo de eventos en Tkinter aplicado a la gestión
    de usuarios con roles (Administrador, Empleado, Cliente), incorporando:
    - Evento virtual <<TreeviewSelect>> para carga interactiva de usuarios.
    - Evento virtual <<ComboboxSelected>> para respuesta al cambio de rol.
    - Eventos de teclado <Return> (Enter) para confirmación de registro.
    - Evento de teclado <Escape> (Esc) para cancelar selección y limpiar formulario.
    - Botones con command= para Registrar, Actualizar, Eliminar y Limpiar.
    - Control de acceso administrativo según el rol del usuario autenticado.
    - Mantenimiento completo de las secciones de Ventas y Productos.
    """

    def __init__(self, root: tk.Tk, restaurante_servicio, cambiar_vista_callback, ruta_assets: Path = None):
        """
        Inicializa la vista principal.

        Args:
            root: Ventana principal de Tkinter
            restaurante_servicio: Instancia de RestauranteServicio
            cambiar_vista_callback: Función de retorno para cambio de vistas
            ruta_assets: Ruta a la carpeta de recursos visuales
        """
        self.root = root
        self.restaurante_servicio = restaurante_servicio
        self.cambiar_vista_callback = cambiar_vista_callback
        self.ruta_assets = ruta_assets or (Path(__file__).resolve().parent.parent / "assets")

        self.frame = None
        self.frame_contenido = None
        self.usuario_actual = None
        self.objeto_usuario_actual = None

        # Almacenamiento de referencias a imágenes de assets para evitar recolección de basura
        self.imagenes = {}

        # -------------------------------------------------------------
        # VARIABLES Y WIDGETS DE GESTIÓN DE PRODUCTOS
        # -------------------------------------------------------------
        self.var_codigo = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_categoria = tk.StringVar()
        self.var_precio = tk.StringVar()
        self.var_stock = tk.StringVar(value="0")

        self.entry_codigo = None
        self.entry_nombre = None
        self.combo_categoria = None
        self.entry_precio = None
        self.spin_stock = None
        self.tree_productos = None
        self.label_estado_productos = None

        # -------------------------------------------------------------
        # VARIABLES Y WIDGETS DE GESTIÓN DE VENTAS
        # -------------------------------------------------------------
        self.var_venta_usuario = tk.StringVar()
        self.var_venta_producto = tk.StringVar()
        self.var_venta_cantidad = tk.StringVar(value="1")

        self.combo_venta_usuario = None
        self.combo_venta_producto = None
        self.spin_venta_cantidad = None
        self.tree_ventas = None
        self.label_estado_ventas = None
        self.lbl_info_precio = None
        self.lbl_info_stock = None
        self.lbl_info_total = None
        self.lbl_resumen_ventas = None

        # -------------------------------------------------------------
        # VARIABLES Y WIDGETS DE GESTIÓN DE USUARIOS (SEMANA 16)
        # -------------------------------------------------------------
        self.var_usr_id = tk.StringVar()
        self.var_usr_nombre = tk.StringVar()
        self.var_usr_username = tk.StringVar()
        self.var_usr_password = tk.StringVar()
        self.var_usr_rol = tk.StringVar(value="Empleado")
        self.var_usr_busqueda = tk.StringVar()
        self.var_mostrar_pass = tk.BooleanVar(value=False)
        self.modo_edicion_usuario = False

        self.entry_usr_id = None
        self.entry_usr_nombre = None
        self.entry_usr_username = None
        self.entry_usr_password = None
        self.combo_usr_rol = None
        self.tree_usuarios = None
        self.label_estado_usuarios = None
        self.lbl_tarjeta_rol = None
        self.lbl_tarjeta_desc = None
        self.lbl_resumen_usuarios = None
        self.btn_usr_registrar = None
        self.btn_usr_actualizar = None
        self.btn_usr_eliminar = None
        self.btn_usr_limpiar = None

        # Cargar recursos de assets
        self._cargar_assets()

    def _cargar_assets(self) -> None:
        """Carga de manera segura los íconos y el logo desde la carpeta assets/."""
        archivos = {
            "logo": "logo.png",
            "productos": "icon_productos.png",
            "ventas": "icon_ventas.png",
            "usuarios": "icon_usuarios.png",
            "logout": "icon_logout.png"
        }
        for clave, nombre_archivo in archivos.items():
            ruta = self.ruta_assets / nombre_archivo
            if ruta.exists():
                try:
                    self.imagenes[clave] = tk.PhotoImage(file=str(ruta))
                except Exception as e:
                    print(f"Nota: No se pudo cargar {nombre_archivo}: {e}")
                    self.imagenes[clave] = None
            else:
                self.imagenes[clave] = None

    def mostrar(self, usuario: str) -> None:
        """
        Despliega la interfaz principal y su estructura de contenedores.

        Args:
            usuario: Nombre de usuario autenticado
        """
        self.usuario_actual = usuario
        self.objeto_usuario_actual = self.restaurante_servicio.obtener_usuario_por_username(usuario)

        # Limpiar la ventana
        for widget in self.root.winfo_children():
            widget.destroy()

        # Contenedor raíz de la vista
        self.frame = tk.Frame(self.root, bg="#f1f5f9")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # 1. Contenedor Superior (Encabezado con logotipo de assets/ y rol de usuario)
        self._construir_encabezado()

        # 2. Contenedor de Navegación (con botones e íconos)
        self._construir_barra_navegacion()

        # 3. Contenedor de Área de Trabajo Dinámica
        self.frame_contenido = tk.Frame(self.frame, bg="#f1f5f9")
        self.frame_contenido.pack(fill=tk.BOTH, expand=True, padx=16, pady=(8, 12))

        # Cargar por defecto la sección correspondiente:
        # Si es Administrador, abrir directamente la sección estrella de la Semana 16: Usuarios
        # Si es Empleado o Cliente, abrir Ventas
        if self.es_admin_actual():
            self.mostrar_seccion_usuarios()
        else:
            self.mostrar_seccion_ventas()

    def es_admin_actual(self) -> bool:
        """Determina si la cuenta en sesión activa tiene rol de Administrador."""
        if self.objeto_usuario_actual:
            return self.objeto_usuario_actual.es_administrador()
        return self.restaurante_servicio.es_usuario_admin(self.usuario_actual)

    def _construir_encabezado(self) -> None:
        """Construye el contenedor superior con información institucional, logo, sesión y rol."""
        header_frame = tk.Frame(self.frame, bg="#0f172a", height=76)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Contenedor izquierdo: Logo + Título
        info_izq = tk.Frame(header_frame, bg="#0f172a")
        info_izq.pack(side=tk.LEFT, padx=16, pady=8)

        img_logo = self.imagenes.get("logo")
        if img_logo:
            lbl_logo = tk.Label(info_izq, image=img_logo, bg="#0f172a")
            lbl_logo.pack(side=tk.LEFT, padx=(0, 12))

        titulos_frame = tk.Frame(info_izq, bg="#0f172a")
        titulos_frame.pack(side=tk.LEFT)

        lbl_titulo = tk.Label(
            titulos_frame,
            text="🍽️ SISTEMA DE GESTIÓN DE RESTAURANTE",
            font=("Segoe UI", 14, "bold"),
            bg="#0f172a",
            fg="#f8fafc"
        )
        lbl_titulo.pack(anchor=tk.W)

        lbl_subtitulo = tk.Label(
            titulos_frame,
            text="Semana 16 • Manejo de Eventos en Tkinter (Gestión de Usuarios con Roles)",
            font=("Segoe UI", 9),
            bg="#0f172a",
            fg="#38bdf8"
        )
        lbl_subtitulo.pack(anchor=tk.W)

        # Contenedor derecho: Información de usuario en sesión y Badge de Rol
        sub_info = tk.Frame(header_frame, bg="#0f172a")
        sub_info.pack(side=tk.RIGHT, padx=20, pady=10)

        # Fila superior de usuario con rol
        fila_user = tk.Frame(sub_info, bg="#0f172a")
        fila_user.pack(anchor=tk.E)

        tk.Label(
            fila_user,
            text=f"Sesión activa: {self.usuario_actual}",
            font=("Segoe UI", 10, "bold"),
            bg="#0f172a",
            fg="#f8fafc"
        ).pack(side=tk.LEFT, padx=(0, 8))

        rol_nombre = self.objeto_usuario_actual.rol if self.objeto_usuario_actual else "Empleado"
        color_badge = "#10b981" if rol_nombre == "Administrador" else ("#0284c7" if rol_nombre == "Empleado" else "#0d9488")
        icono_badge = "👑" if rol_nombre == "Administrador" else ("👔" if rol_nombre == "Empleado" else "👤")

        lbl_badge_rol = tk.Label(
            fila_user,
            text=f" {icono_badge} {rol_nombre.upper()} ",
            font=("Segoe UI", 8, "bold"),
            bg=color_badge,
            fg="#ffffff",
            bd=0,
            padx=4,
            pady=1
        )
        lbl_badge_rol.pack(side=tk.LEFT)

        tk.Label(
            sub_info,
            text="Restaurante Gourmet • Panel Operativo y Administrativo",
            font=("Segoe UI", 8),
            bg="#0f172a",
            fg="#94a3b8"
        ).pack(anchor=tk.E, pady=(2, 0))

    def _construir_barra_navegacion(self) -> None:
        """Construye la barra de navegación con botones para alternar entre vistas."""
        nav_frame = tk.Frame(self.frame, bg="#ffffff", height=52, bd=1, relief=tk.SOLID)
        nav_frame.pack(fill=tk.X)
        nav_frame.pack_propagate(False)

        # Botón Gestión de Usuarios (Semana 16)
        img_usr = self.imagenes.get("usuarios")
        btn_usuarios = tk.Button(
            nav_frame,
            text=" 👥 Gestión de Usuarios",
            image=img_usr,
            compound=tk.LEFT if img_usr else tk.NONE,
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed" if self.es_admin_actual() else "#64748b",
            fg="#ffffff",
            activebackground="#6d28d9" if self.es_admin_actual() else "#475569",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.mostrar_seccion_usuarios
        )
        btn_usuarios.pack(side=tk.LEFT, padx=(16, 8), pady=7)

        # Botón Registro de Ventas
        img_ventas = self.imagenes.get("ventas")
        btn_ventas = tk.Button(
            nav_frame,
            text=" 🛒 Registro de Ventas",
            image=img_ventas,
            compound=tk.LEFT if img_ventas else tk.NONE,
            font=("Segoe UI", 10, "bold"),
            bg="#16a34a",
            fg="#ffffff",
            activebackground="#15803d",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.mostrar_seccion_ventas
        )
        btn_ventas.pack(side=tk.LEFT, padx=8, pady=7)

        # Botón Gestión de Productos
        img_prod = self.imagenes.get("productos")
        btn_productos = tk.Button(
            nav_frame,
            text=" 📦 Gestión de Productos",
            image=img_prod,
            compound=tk.LEFT if img_prod else tk.NONE,
            font=("Segoe UI", 10, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.mostrar_seccion_productos
        )
        btn_productos.pack(side=tk.LEFT, padx=8, pady=7)

        # Botón Cerrar Sesión
        img_logout = self.imagenes.get("logout")
        btn_cerrar = tk.Button(
            nav_frame,
            text=" 🚪 Cerrar Sesión",
            image=img_logout,
            compound=tk.LEFT if img_logout else tk.NONE,
            font=("Segoe UI", 9, "bold"),
            bg="#ef4444",
            fg="#ffffff",
            activebackground="#dc2626",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.cerrar_sesion
        )
        btn_cerrar.pack(side=tk.RIGHT, padx=16, pady=7)

    # =============================================================
    # SECCIÓN: GESTIÓN DE USUARIOS (SEMANA 16 - MANEJO DE EVENTOS)
    # Treeview, <<TreeviewSelect>>, <Return>, <Escape>, <<ComboboxSelected>>
    # =============================================================

    def mostrar_seccion_usuarios(self) -> None:
        """
        Construye la sección de Gestión de Usuarios.
        Aplica control de acceso por roles:
        - Si el usuario autenticado es Administrador: Acceso completo al CRUD y eventos.
        - Si el usuario es Empleado o Cliente: Vista de acceso restringido informativa.
        """
        self._limpiar_contenido()

        # Control de Acceso por Rol (Requisito fundamental de Semana 16)
        if not self.es_admin_actual():
            self._construir_vista_acceso_restringido_usuarios()
            return

        panel_horizontal = tk.Frame(self.frame_contenido, bg="#f1f5f9")
        panel_horizontal.pack(fill=tk.BOTH, expand=True)

        # ---------------------------------------------------------
        # COLUMNA IZQUIERDA: FORMULARIO DE USUARIO Y BOTONES (command=)
        # ---------------------------------------------------------
        col_izquierda = tk.Frame(panel_horizontal, bg="#f1f5f9", width=420)
        col_izquierda.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        col_izquierda.pack_propagate(False)

        # Formulario
        lf_formulario = ttk.LabelFrame(col_izquierda, text=" Formulario de Gestión de Usuarios ")
        lf_formulario.pack(fill=tk.X, pady=(0, 6), ipady=4)
        lf_formulario.columnconfigure(1, weight=1)

        # 1. Identificador de Usuario (ID)
        ttk.Label(lf_formulario, text="ID Usuario:", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5
        )
        self.entry_usr_id = ttk.Entry(
            lf_formulario,
            textvariable=self.var_usr_id,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.entry_usr_id.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)

        # 2. Nombre Completo
        ttk.Label(lf_formulario, text="Nombre Completo:", font=("Segoe UI", 9, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5
        )
        self.entry_usr_nombre = ttk.Entry(
            lf_formulario,
            textvariable=self.var_usr_nombre,
            font=("Segoe UI", 9)
        )
        self.entry_usr_nombre.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)

        # 3. Nombre de Usuario (Username)
        ttk.Label(lf_formulario, text="Usuario (login):", font=("Segoe UI", 9, "bold")).grid(
            row=2, column=0, sticky=tk.W, padx=10, pady=5
        )
        self.entry_usr_username = ttk.Entry(
            lf_formulario,
            textvariable=self.var_usr_username,
            font=("Segoe UI", 9)
        )
        self.entry_usr_username.grid(row=2, column=1, sticky=tk.EW, padx=10, pady=5)

        # 4. Contraseña
        ttk.Label(lf_formulario, text="Contraseña:", font=("Segoe UI", 9, "bold")).grid(
            row=3, column=0, sticky=tk.W, padx=10, pady=5
        )

        frame_pass = tk.Frame(lf_formulario, bg="#f1f5f9")
        frame_pass.grid(row=3, column=1, sticky=tk.EW, padx=10, pady=5)

        self.entry_usr_password = ttk.Entry(
            frame_pass,
            textvariable=self.var_usr_password,
            show="•",
            font=("Segoe UI", 9)
        )
        self.entry_usr_password.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_ver_pass = tk.Checkbutton(
            frame_pass,
            text="👁️",
            variable=self.var_mostrar_pass,
            command=self._toggle_ver_password,
            bg="#f1f5f9",
            activebackground="#f1f5f9",
            bd=0,
            cursor="hand2"
        )
        btn_ver_pass.pack(side=tk.RIGHT, padx=(4, 0))

        # 5. Rol de Usuario (Combobox con <<ComboboxSelected>>)
        ttk.Label(lf_formulario, text="Rol del Usuario:", font=("Segoe UI", 9, "bold")).grid(
            row=4, column=0, sticky=tk.W, padx=10, pady=5
        )
        roles = ["Administrador", "Empleado", "Cliente"]
        self.combo_usr_rol = ttk.Combobox(
            lf_formulario,
            textvariable=self.var_usr_rol,
            values=roles,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.combo_usr_rol.grid(row=4, column=1, sticky=tk.EW, padx=10, pady=5)
        self.combo_usr_rol.current(1)  # Empleado por defecto

        # VINCULACIÓN DE EVENTO VIRTUAL COMBOBOX: <<ComboboxSelected>>
        self.combo_usr_rol.bind("<<ComboboxSelected>>", self._on_combobox_rol_seleccionado)

        # Tarjeta reactiva de información del rol (actualizada por <<ComboboxSelected>>)
        frame_info_rol = tk.Frame(lf_formulario, bg="#ffffff", bd=1, relief=tk.SOLID)
        frame_info_rol.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=(6, 8))

        f_tit_rol = tk.Frame(frame_info_rol, bg="#ffffff")
        f_tit_rol.pack(fill=tk.X, padx=8, pady=(5, 2))

        tk.Label(f_tit_rol, text="Nivel de Privilegios:", font=("Segoe UI", 8, "bold"), bg="#ffffff", fg="#64748b").pack(side=tk.LEFT)
        self.lbl_tarjeta_rol = tk.Label(
            f_tit_rol,
            text="👔 Empleado",
            font=("Segoe UI", 8, "bold"),
            bg="#e0f2fe",
            fg="#0284c7",
            padx=6,
            pady=1
        )
        self.lbl_tarjeta_rol.pack(side=tk.RIGHT)

        self.lbl_tarjeta_desc = tk.Label(
            frame_info_rol,
            text="Operación del restaurante, registro de ventas y consulta de existencias.",
            font=("Segoe UI", 8),
            bg="#ffffff",
            fg="#475569",
            wraplength=370,
            justify=tk.LEFT
        )
        self.lbl_tarjeta_desc.pack(fill=tk.X, padx=8, pady=(2, 6))

        # ---------------------------------------------------------
        # VINCULACIÓN DE EVENTOS DE TECLADO: <Return> y <Escape>
        # Reutilizan métodos sin duplicar lógica de negocio
        # ---------------------------------------------------------
        widgets_formulario = [
            self.entry_usr_nombre,
            self.entry_usr_username,
            self.entry_usr_password,
            self.combo_usr_rol
        ]
        for w in widgets_formulario:
            w.bind("<Return>", self._on_enter_teclado)
            w.bind("<Escape>", self._on_escape_teclado)

        # ---------------------------------------------------------
        # BOTONES DE ACCIONES ASOCIADOS CON command=
        # ---------------------------------------------------------
        lf_acciones = ttk.LabelFrame(col_izquierda, text=" Acciones del Formulario ")
        lf_acciones.pack(fill=tk.X, pady=4, ipady=3)

        fila_btns_1 = tk.Frame(lf_acciones, bg="#f1f5f9")
        fila_btns_1.pack(fill=tk.X, padx=8, pady=3)

        self.btn_usr_registrar = tk.Button(
            fila_btns_1,
            text="➕ Registrar [Enter]",
            font=("Segoe UI", 9, "bold"),
            bg="#16a34a",
            fg="#ffffff",
            activebackground="#15803d",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._accion_registrar_usuario
        )
        self.btn_usr_registrar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4), ipady=4)

        self.btn_usr_actualizar = tk.Button(
            fila_btns_1,
            text="✏️ Actualizar",
            font=("Segoe UI", 9, "bold"),
            bg="#d97706",
            fg="#ffffff",
            activebackground="#b45309",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED,
            command=self._accion_actualizar_usuario
        )
        self.btn_usr_actualizar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0), ipady=4)

        fila_btns_2 = tk.Frame(lf_acciones, bg="#f1f5f9")
        fila_btns_2.pack(fill=tk.X, padx=8, pady=3)

        self.btn_usr_eliminar = tk.Button(
            fila_btns_2,
            text="🗑️ Eliminar Usuario",
            font=("Segoe UI", 9, "bold"),
            bg="#dc2626",
            fg="#ffffff",
            activebackground="#b91c1c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED,
            command=self._accion_eliminar_usuario
        )
        self.btn_usr_eliminar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4), ipady=3)

        self.btn_usr_limpiar = tk.Button(
            fila_btns_2,
            text="🧹 Limpiar [Esc]",
            font=("Segoe UI", 9),
            bg="#64748b",
            fg="#ffffff",
            activebackground="#475569",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._limpiar_formulario_usuario
        )
        self.btn_usr_limpiar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0), ipady=3)

        # ---------------------------------------------------------
        # PANEL EDUCATIVO DE EVENTOS Y ATAJOS IMPLEMENTADOS
        # ---------------------------------------------------------
        lf_atajos = ttk.LabelFrame(col_izquierda, text=" Eventos y Atajos Activos ")
        lf_atajos.pack(fill=tk.X, pady=4, ipady=3)

        frame_info_eventos = tk.Frame(lf_atajos, bg="#f8fafc", bd=1, relief=tk.SOLID)
        frame_info_eventos.pack(fill=tk.X, padx=8, pady=4)

        items_eventos = [
            ("<<TreeviewSelect>>", "Clic en la tabla carga datos al formulario"),
            ("<Return> (Enter)", "Confirma el registro del usuario"),
            ("<Escape> (Esc)", "Limpia el formulario y deselecciona"),
            ("<<ComboboxSelected>>", "Actualiza dinámicamente la tarjeta de rol"),
            ("command=", "Asociado a botones Registrar, Actualizar, Eliminar, Limpiar")
        ]

        for ev_nombre, ev_desc in items_eventos:
            f_item = tk.Frame(frame_info_eventos, bg="#f8fafc")
            f_item.pack(fill=tk.X, padx=6, pady=1)
            tk.Label(
                f_item,
                text=ev_nombre,
                font=("Consolas", 8, "bold"),
                bg="#f8fafc",
                fg="#7c3aed" if "<<" in ev_nombre else ("#0284c7" if "<" in ev_nombre else "#16a34a")
            ).pack(side=tk.LEFT)
            tk.Label(
                f_item,
                text=f": {ev_desc}",
                font=("Segoe UI", 8),
                bg="#f8fafc",
                fg="#475569"
            ).pack(side=tk.LEFT)

        # Barra de estado y retroalimentación cromática
        frame_estado = tk.Frame(col_izquierda, bg="#ffffff", bd=1, relief=tk.SOLID)
        frame_estado.pack(fill=tk.X, pady=(6, 0))

        self.label_estado_usuarios = tk.Label(
            frame_estado,
            text="Listo para registrar usuarios o seleccionar una fila del directorio.",
            font=("Segoe UI", 8),
            bg="#ffffff",
            fg="#475569",
            wraplength=380,
            justify=tk.LEFT
        )
        self.label_estado_usuarios.pack(fill=tk.X, padx=8, pady=6)

        # ---------------------------------------------------------
        # COLUMNA DERECHA: TABLA TREEVIEW DE USUARIOS Y EVENTO <<TreeviewSelect>>
        # ---------------------------------------------------------
        col_derecha = tk.Frame(panel_horizontal, bg="#f1f5f9")
        col_derecha.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        lf_tabla_usuarios = ttk.LabelFrame(col_derecha, text=" Directorio de Usuarios Registrados ")
        lf_tabla_usuarios.pack(fill=tk.BOTH, expand=True)

        # Barra de búsqueda en tiempo real
        f_busqueda = tk.Frame(lf_tabla_usuarios, bg="#f1f5f9")
        f_busqueda.pack(fill=tk.X, padx=10, pady=(6, 4))

        tk.Label(f_busqueda, text="🔍 Filtrar usuarios:", font=("Segoe UI", 9, "bold"), bg="#f1f5f9", fg="#334155").pack(side=tk.LEFT, padx=(0, 6))

        entry_busqueda = ttk.Entry(f_busqueda, textvariable=self.var_usr_busqueda, font=("Segoe UI", 9))
        entry_busqueda.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        entry_busqueda.bind("<KeyRelease>", lambda e: self._actualizar_tabla_usuarios())

        btn_limpiar_busq = tk.Button(
            f_busqueda,
            text="Borrar filtro",
            font=("Segoe UI", 8),
            bg="#e2e8f0",
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: [self.var_usr_busqueda.set(""), self._actualizar_tabla_usuarios()]
        )
        btn_limpiar_busq.pack(side=tk.RIGHT)

        # Contenedor para Treeview y Scrollbar
        frame_tree_u = tk.Frame(lf_tabla_usuarios, bg="#ffffff")
        frame_tree_u.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        # NOTA DE SEGURIDAD (Requisito docente):
        # Columnas visibles: ID, Nombre, Usuario y Rol.
        # NUNCA se expone la contraseña en la tabla.
        columnas = ("id_usuario", "nombre", "username", "rol")
        self.tree_usuarios = ttk.Treeview(
            frame_tree_u,
            columns=columnas,
            show="headings",
            selectmode="browse"
        )

        self.tree_usuarios.heading("id_usuario", text="Identificador (ID)")
        self.tree_usuarios.heading("nombre", text="Nombre Completo")
        self.tree_usuarios.heading("username", text="Usuario (Username)")
        self.tree_usuarios.heading("rol", text="Rol del Sistema")

        self.tree_usuarios.column("id_usuario", width=120, anchor=tk.CENTER)
        self.tree_usuarios.column("nombre", width=240, anchor=tk.W)
        self.tree_usuarios.column("username", width=160, anchor=tk.CENTER)
        self.tree_usuarios.column("rol", width=140, anchor=tk.CENTER)

        scroll_tree_u = ttk.Scrollbar(frame_tree_u, orient=tk.VERTICAL, command=self.tree_usuarios.yview)
        self.tree_usuarios.configure(yscrollcommand=scroll_tree_u.set)

        self.tree_usuarios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_tree_u.pack(side=tk.RIGHT, fill=tk.Y)

        # VINCULACIÓN DEL EVENTO VIRTUAL <<TreeviewSelect>>
        self.tree_usuarios.bind("<<TreeviewSelect>>", self._on_treeview_usuario_seleccionado)
        self.tree_usuarios.bind("<Escape>", self._on_escape_teclado)

        # Panel inferior de resumen por roles
        frame_resumen = tk.Frame(lf_tabla_usuarios, bg="#f8fafc", bd=1, relief=tk.GROOVE)
        frame_resumen.pack(fill=tk.X, padx=10, pady=(4, 8))

        self.lbl_resumen_usuarios = tk.Label(
            frame_resumen,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg="#f8fafc",
            fg="#1e293b"
        )
        self.lbl_resumen_usuarios.pack(side=tk.LEFT, padx=12, pady=6)

        # Cargar datos iniciales
        self._actualizar_tabla_usuarios()
        self._on_combobox_rol_seleccionado()
        self._preparar_nuevo_id()

    def _construir_vista_acceso_restringido_usuarios(self) -> None:
        """Despliega una pantalla informativa de acceso denegado para roles no administrativos."""
        card_restringido = tk.Frame(self.frame_contenido, bg="#ffffff", bd=2, relief=tk.GROOVE)
        card_restringido.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=540, height=360)

        # Encabezado de advertencia
        header_warn = tk.Frame(card_restringido, bg="#dc2626", height=70)
        header_warn.pack(fill=tk.X)
        header_warn.pack_propagate(False)

        tk.Label(
            header_warn,
            text="🔒 ACCESO RESTRINGIDO",
            font=("Segoe UI", 14, "bold"),
            bg="#dc2626",
            fg="#ffffff"
        ).pack(pady=(12, 2))

        tk.Label(
            header_warn,
            text="Control de Privilegios de Seguridad • Semana 16",
            font=("Segoe UI", 9),
            bg="#dc2626",
            fg="#fecaca"
        ).pack()

        # Cuerpo del mensaje
        cuerpo = tk.Frame(card_restringido, bg="#ffffff")
        cuerpo.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)

        rol_nombre = self.objeto_usuario_actual.rol if self.objeto_usuario_actual else "Empleado"

        tk.Label(
            cuerpo,
            text=f"El usuario '{self.usuario_actual}' tiene asignado el rol de '{rol_nombre}'.",
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg="#1e293b"
        ).pack(pady=(0, 10))

        tk.Label(
            cuerpo,
            text="La gestión administrativa de usuarios (registro, actualización y eliminación)\n"
                 "está reservada de manera exclusiva para usuarios con rol de Administrador.\n\n"
                 "Si requiere gestionar usuarios, por favor cierre sesión e ingrese con una\n"
                 "cuenta con privilegios administrativos (ej. admin / admin123).",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#475569",
            justify=tk.CENTER
        ).pack(pady=5)

        btn_ir_ventas = tk.Button(
            cuerpo,
            text="🛒 Ir al Registro de Ventas",
            font=("Segoe UI", 10, "bold"),
            bg="#16a34a",
            fg="#ffffff",
            activebackground="#15803d",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.mostrar_seccion_ventas
        )
        btn_ir_ventas.pack(pady=(15, 0), ipady=5, ipadx=10)

    # -------------------------------------------------------------
    # EVENTOS Y CALLBACKS DE GESTIÓN DE USUARIOS
    # -------------------------------------------------------------

    def _on_treeview_usuario_seleccionado(self, event=None) -> None:
        """
        Callback asociado al evento virtual <<TreeviewSelect>> mediante bind().
        Flujo de interacción:
        1. Captura la fila seleccionada por el usuario en el Treeview.
        2. Extrae el identificador del registro (id_usuario).
        3. Consulta el objeto completo en RestauranteServicio (sin exponer contraseña en tabla).
        4. Carga de forma reactiva los atributos en los campos del formulario.
        5. Actualiza la tarjeta del rol y habilita los botones Actualizar y Eliminar.
        """
        if not self.tree_usuarios:
            return

        seleccion = self.tree_usuarios.selection()
        if not seleccion:
            return

        valores = self.tree_usuarios.item(seleccion[0], "values")
        if not valores:
            return

        id_usuario = valores[0]

        # Consultar mediante el servicio usando el identificador
        usuario = self.restaurante_servicio.consultar_usuario(id_usuario)
        if not usuario:
            self._mostrar_estado_usuario(f"⚠️ No se pudo localizar el usuario '{id_usuario}'.", tipo="error")
            return

        # Cargar datos en el formulario
        self.var_usr_id.set(usuario.id_usuario)
        self.var_usr_nombre.set(usuario.nombre)
        self.var_usr_username.set(usuario.username)
        self.var_usr_rol.set(usuario.rol)
        # Dejar campo de contraseña en blanco para proteger credenciales existentes
        self.var_usr_password.set("")

        # En modo edición, protegemos el username para conservar el identificador único
        if self.entry_usr_username:
            self.entry_usr_username.config(state="disabled")

        self.modo_edicion_usuario = True

        # Actualizar tarjeta de rol correspondiente
        self._on_combobox_rol_seleccionado()

        # Ajustar estados de botones
        if self.btn_usr_actualizar:
            self.btn_usr_actualizar.config(state=tk.NORMAL)
        if self.btn_usr_eliminar:
            self.btn_usr_eliminar.config(state=tk.NORMAL)
        if self.btn_usr_registrar:
            self.btn_usr_registrar.config(text="➕ Registrar Nuevo")

        # Foco al nombre para facilitar la edición
        if self.entry_usr_nombre:
            self.entry_usr_nombre.focus()

        self._mostrar_estado_usuario(
            f"✅ <<TreeviewSelect>>: Datos de '{usuario.nombre}' (@{usuario.username}) cargados en el formulario. "
            f"(Deje la contraseña vacía si no desea modificarla).",
            tipo="exito"
        )

    def _on_combobox_rol_seleccionado(self, event=None) -> None:
        """
        Callback asociado al evento virtual <<ComboboxSelected>> del combobox de rol.
        Actualiza dinámicamente la tarjeta visual de privilegios y descripción del rol.
        """
        rol = self.var_usr_rol.get().strip()

        detalles_roles = {
            "Administrador": {
                "badge": "👑 Administrador",
                "bg_badge": "#f3e8ff",
                "fg_badge": "#7c3aed",
                "desc": "Acceso total al sistema: gestión de usuarios, productos, ventas y configuración."
            },
            "Empleado": {
                "badge": "👔 Empleado",
                "bg_badge": "#e0f2fe",
                "fg_badge": "#0284c7",
                "desc": "Acceso operativo: registro de ventas, consulta de catálogo y control de existencias."
            },
            "Cliente": {
                "badge": "👤 Cliente",
                "bg_badge": "#ccfbf1",
                "fg_badge": "#0d9488",
                "desc": "Acceso básico: consulta de catálogo de platos, bebidas y consulta de pedidos."
            }
        }

        info = detalles_roles.get(rol, detalles_roles["Empleado"])

        if self.lbl_tarjeta_rol:
            self.lbl_tarjeta_rol.config(
                text=info["badge"],
                bg=info["bg_badge"],
                fg=info["fg_badge"]
            )
        if self.lbl_tarjeta_desc:
            self.lbl_tarjeta_desc.config(text=info["desc"])

    def _on_enter_teclado(self, event=None) -> None:
        """
        Callback asociado al evento de teclado <Return> (Enter) en los campos del formulario.
        Reutiliza los métodos existentes (_accion_registrar_usuario o _accion_actualizar_usuario)
        evitando duplicar lógica de negocio.
        """
        if self.modo_edicion_usuario:
            self._accion_actualizar_usuario()
        else:
            self._accion_registrar_usuario()

    def _on_escape_teclado(self, event=None) -> None:
        """
        Callback asociado al evento de teclado <Escape> (Esc).
        Limpia el formulario, cancela la selección actual del Treeview y restaura la vista.
        """
        if self.tree_usuarios:
            self.tree_usuarios.selection_remove(self.tree_usuarios.selection())
        self._limpiar_formulario_usuario(mensaje="Operación cancelada y formulario restablecido mediante tecla <Escape>.")

    def _toggle_ver_password(self) -> None:
        """Alterna entre mostrar u ocultar la contraseña en el campo de texto."""
        if not self.entry_usr_password:
            return
        if self.var_mostrar_pass.get():
            self.entry_usr_password.config(show="")
        else:
            self.entry_usr_password.config(show="•")

    def _preparar_nuevo_id(self) -> None:
        """Calcula y proyecta el siguiente identificador disponible para nuevo usuario."""
        siguiente_id = self.restaurante_servicio._generar_siguiente_id_usuario()
        self.var_usr_id.set(f"[{siguiente_id}] (Auto)")

    def _actualizar_tabla_usuarios(self) -> None:
        """Consulta los usuarios en el servicio y refresca la tabla Treeview aplicando filtros."""
        if not self.tree_usuarios:
            return

        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)

        filtro = self.var_usr_busqueda.get().strip().lower()
        usuarios = self.restaurante_servicio.obtener_usuarios()

        conteo_admin = 0
        conteo_empleado = 0
        conteo_cliente = 0

        for u in usuarios:
            if u.es_administrador():
                conteo_admin += 1
            elif u.es_empleado():
                conteo_empleado += 1
            elif u.es_cliente():
                conteo_cliente += 1

            # Filtrar si corresponde
            if filtro:
                coincide = (
                    filtro in u.id_usuario.lower()
                    or filtro in u.nombre.lower()
                    or filtro in u.username.lower()
                    or filtro in u.rol.lower()
                )
                if not coincide:
                    continue

            # Inserción segura: ID, Nombre, Username, Rol (sin contraseña)
            self.tree_usuarios.insert(
                "",
                tk.END,
                values=(
                    u.id_usuario,
                    u.nombre,
                    u.username,
                    u.rol
                )
            )

        if self.lbl_resumen_usuarios:
            self.lbl_resumen_usuarios.config(
                text=f"📊 Total Usuarios: {len(usuarios)}  |  "
                     f"👑 Admins: {conteo_admin}  |  "
                     f"👔 Empleados: {conteo_empleado}  |  "
                     f"👤 Clientes: {conteo_cliente}"
            )

    # -------------------------------------------------------------
    # MÉTODOS DE OPERACIONES CRUD DE USUARIOS (ASOCIADOS A command=)
    # -------------------------------------------------------------

    def _accion_registrar_usuario(self) -> None:
        """
        Registra un nuevo usuario delegando la validación y persistencia a RestauranteServicio.
        Invocado por el botón 'Registrar Usuario' (command=) y por el atajo <Return>.
        """
        nombre = self.var_usr_nombre.get().strip()
        username = self.var_usr_username.get().strip()
        password = self.var_usr_password.get()
        rol = self.var_usr_rol.get().strip()

        # Validación visual básica previa
        if not nombre or not username or not password:
            self._mostrar_estado_usuario("⚠️ Debe completar todos los campos del usuario.", tipo="advertencia")
            messagebox.showwarning("Campos Requeridos", "Por favor complete nombre, nombre de usuario y contraseña.")
            if not nombre and self.entry_usr_nombre:
                self.entry_usr_nombre.focus()
            elif not username and self.entry_usr_username:
                self.entry_usr_username.focus()
            elif not password and self.entry_usr_password:
                self.entry_usr_password.focus()
            return

        # Delegación completa a la capa de servicio
        exito, mensaje, nuevo_usuario = self.restaurante_servicio.registrar_usuario(
            username=username,
            password=password,
            nombre=nombre,
            rol=rol
        )

        if exito and nuevo_usuario:
            self._mostrar_estado_usuario(f"✅ {mensaje}", tipo="exito")
            self._actualizar_tabla_usuarios()
            self._limpiar_formulario_usuario(conservar_estado=True)
            messagebox.showinfo("Usuario Registrado", mensaje)
        else:
            self._mostrar_estado_usuario(f"❌ {mensaje}", tipo="error")
            messagebox.showwarning("Atención al Registrar", mensaje)

    def _accion_actualizar_usuario(self) -> None:
        """
        Actualiza los datos del usuario seleccionado delegando a RestauranteServicio.
        Invocado por el botón 'Actualizar' (command=).
        """
        id_usuario = self.var_usr_id.get().strip().replace("[", "").replace("]", "").replace("(Auto)", "").strip()
        nombre = self.var_usr_nombre.get().strip()
        rol = self.var_usr_rol.get().strip()
        password = self.var_usr_password.get().strip()  # Si está vacía, no se altera

        if not id_usuario or not self.modo_edicion_usuario:
            self._mostrar_estado_usuario("⚠️ Debe seleccionar un usuario de la tabla para actualizar.", tipo="advertencia")
            messagebox.showinfo("Seleccione Usuario", "Haga clic en una fila del directorio para cargar sus datos.")
            return

        if not nombre:
            self._mostrar_estado_usuario("⚠️ El nombre del usuario no puede quedar vacío.", tipo="advertencia")
            messagebox.showwarning("Campo Requerido", "El nombre completo es obligatorio.")
            return

        # Delegación al servicio
        exito, mensaje = self.restaurante_servicio.actualizar_usuario(
            id_usuario=id_usuario,
            nombre=nombre,
            rol=rol,
            password=password if password else None
        )

        if exito:
            self._mostrar_estado_usuario(f"✅ {mensaje}", tipo="exito")
            self._actualizar_tabla_usuarios()
            self._limpiar_formulario_usuario(conservar_estado=True)
            messagebox.showinfo("Actualización Exitosa", mensaje)
        else:
            self._mostrar_estado_usuario(f"❌ {mensaje}", tipo="error")
            messagebox.showwarning("No se pudo actualizar", mensaje)

    def _accion_eliminar_usuario(self) -> None:
        """
        Elimina el usuario seleccionado aplicando confirmación y reglas de seguridad.
        Invocado por el botón 'Eliminar' (command=).
        """
        id_usuario = self.var_usr_id.get().strip().replace("[", "").replace("]", "").replace("(Auto)", "").strip()
        if not id_usuario or not self.modo_edicion_usuario:
            self._mostrar_estado_usuario("⚠️ Seleccione el usuario que desea eliminar.", tipo="advertencia")
            messagebox.showinfo("Seleccione Usuario", "Seleccione un usuario de la tabla para proceder.")
            return

        usuario = self.restaurante_servicio.consultar_usuario(id_usuario)
        if not usuario:
            self._mostrar_estado_usuario(f"❌ El usuario con ID '{id_usuario}' no existe.", tipo="error")
            return

        # Regla de seguridad visual inmediata: No eliminar cuenta activa
        if usuario.username.lower() == str(self.usuario_actual).lower():
            self._mostrar_estado_usuario("❌ Bloqueado: No puede eliminar su propia cuenta administrativa en sesión activa.", tipo="error")
            messagebox.showerror(
                "Operación Denegada",
                f"No puede eliminar al usuario '{usuario.username}' porque es la cuenta con la que ha iniciado sesión actualmente."
            )
            return

        # Confirmación requerida
        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar al usuario '{usuario.nombre}' (@{usuario.username})?\n"
            f"ID: {usuario.id_usuario} | Rol: {usuario.rol}\n\n"
            f"Esta acción eliminará el registro de usuarios.json de forma definitiva."
        )

        if confirmar:
            exito, mensaje = self.restaurante_servicio.eliminar_usuario(
                id_usuario=id_usuario,
                username_en_sesion=self.usuario_actual
            )

            if exito:
                self._mostrar_estado_usuario(f"✅ {mensaje}", tipo="exito")
                self._actualizar_tabla_usuarios()
                self._limpiar_formulario_usuario(conservar_estado=True)
                messagebox.showinfo("Usuario Eliminado", mensaje)
            else:
                self._mostrar_estado_usuario(f"❌ {mensaje}", tipo="error")
                messagebox.showerror("Error al Eliminar", mensaje)

    def _limpiar_formulario_usuario(self, conservar_estado: bool = False, mensaje: str = None) -> None:
        """Restaura los campos del formulario de usuario y devuelve la interfaz a su estado inicial."""
        self._preparar_nuevo_id()
        self.var_usr_nombre.set("")
        self.var_usr_username.set("")
        self.var_usr_password.set("")
        self.var_mostrar_pass.set(False)
        self.var_usr_rol.set("Empleado")

        if self.entry_usr_username:
            self.entry_usr_username.config(state="normal")
        if self.entry_usr_password:
            self.entry_usr_password.config(show="•")

        self.modo_edicion_usuario = False

        # Deshabilitar botones de edición
        if self.btn_usr_actualizar:
            self.btn_usr_actualizar.config(state=tk.DISABLED)
        if self.btn_usr_eliminar:
            self.btn_usr_eliminar.config(state=tk.DISABLED)
        if self.btn_usr_registrar:
            self.btn_usr_registrar.config(text="➕ Registrar [Enter]")

        # Actualizar tarjeta de rol
        self._on_combobox_rol_seleccionado()

        if self.tree_usuarios:
            self.tree_usuarios.selection_remove(self.tree_usuarios.selection())

        if not conservar_estado:
            texto = mensaje or "Formulario restablecido a modo nuevo registro."
            self._mostrar_estado_usuario(texto, tipo="info")

        if self.entry_usr_nombre:
            self.entry_usr_nombre.focus()

    def _mostrar_estado_usuario(self, mensaje: str, tipo: str = "info") -> None:
        """Actualiza la barra de estado de usuarios con colores dinámicos."""
        colores = {
            "exito": "#16a34a",
            "error": "#dc2626",
            "advertencia": "#d97706",
            "info": "#475569"
        }
        if self.label_estado_usuarios:
            color = colores.get(tipo, "#475569")
            self.label_estado_usuarios.config(text=mensaje, fg=color)

    # =============================================================
    # SECCIÓN: REGISTRO DE VENTAS (CONSERVADA DE SEMANA 15)
    # =============================================================

    def mostrar_seccion_ventas(self) -> None:
        """Construye la sección de Registro de Ventas."""
        self._limpiar_contenido()

        panel_horizontal = tk.Frame(self.frame_contenido, bg="#f1f5f9")
        panel_horizontal.pack(fill=tk.BOTH, expand=True)

        # Columna Izquierda: Formulario de Registro de Venta
        col_izquierda = tk.Frame(panel_horizontal, bg="#f1f5f9", width=410)
        col_izquierda.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        col_izquierda.pack_propagate(False)

        lf_venta = ttk.LabelFrame(col_izquierda, text=" Formulario de Operación de Venta ")
        lf_venta.pack(fill=tk.X, pady=(0, 8), ipady=6)
        lf_venta.columnconfigure(1, weight=1)

        # Campo: Selección de Usuario
        ttk.Label(lf_venta, text="Usuario:", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=8
        )

        usuarios = self.restaurante_servicio.obtener_usuarios()
        valores_usuarios = [f"{u.username} - {u.nombre} ({u.rol})" for u in usuarios]

        self.combo_venta_usuario = ttk.Combobox(
            lf_venta,
            textvariable=self.var_venta_usuario,
            values=valores_usuarios,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.combo_venta_usuario.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=8)

        # Seleccionar por defecto el usuario actual en sesión si coincide
        for idx, u in enumerate(usuarios):
            if u.username.lower() == (self.usuario_actual or "").lower():
                self.combo_venta_usuario.current(idx)
                break
        else:
            if valores_usuarios:
                self.combo_venta_usuario.current(0)

        # Campo: Selección de Producto
        ttk.Label(lf_venta, text="Producto:", font=("Segoe UI", 9, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=8
        )

        self.combo_venta_producto = ttk.Combobox(
            lf_venta,
            textvariable=self.var_venta_producto,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.combo_venta_producto.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=8)
        self._refrescar_combo_productos_venta()

        # Campo: Cantidad a vender
        ttk.Label(lf_venta, text="Cantidad:", font=("Segoe UI", 9, "bold")).grid(
            row=2, column=0, sticky=tk.W, padx=10, pady=8
        )

        self.spin_venta_cantidad = ttk.Spinbox(
            lf_venta,
            from_=1,
            to=999,
            textvariable=self.var_venta_cantidad,
            font=("Segoe UI", 9),
            command=self._actualizar_calculo_total
        )
        self.spin_venta_cantidad.grid(row=2, column=1, sticky=tk.EW, padx=10, pady=8)
        self.spin_venta_cantidad.bind("<KeyRelease>", lambda e: self._actualizar_calculo_total())

        self.combo_venta_producto.bind("<<ComboboxSelected>>", lambda e: self._actualizar_calculo_total())

        # Contenedor con resumen informativo del producto
        frame_detalles = tk.Frame(lf_venta, bg="#f8fafc", bd=1, relief=tk.SOLID)
        frame_detalles.grid(row=3, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=(6, 12))

        f_fila1 = tk.Frame(frame_detalles, bg="#f8fafc")
        f_fila1.pack(fill=tk.X, padx=8, pady=(6, 2))
        tk.Label(f_fila1, text="Precio Unitario:", font=("Segoe UI", 9), bg="#f8fafc", fg="#475569").pack(side=tk.LEFT)
        self.lbl_info_precio = tk.Label(f_fila1, text="$0.00", font=("Segoe UI", 9, "bold"), bg="#f8fafc", fg="#0f172a")
        self.lbl_info_precio.pack(side=tk.RIGHT)

        f_fila2 = tk.Frame(frame_detalles, bg="#f8fafc")
        f_fila2.pack(fill=tk.X, padx=8, pady=2)
        tk.Label(f_fila2, text="Stock Disponible:", font=("Segoe UI", 9), bg="#f8fafc", fg="#475569").pack(side=tk.LEFT)
        self.lbl_info_stock = tk.Label(f_fila2, text="0 unidades", font=("Segoe UI", 9, "bold"), bg="#f8fafc", fg="#0284c7")
        self.lbl_info_stock.pack(side=tk.RIGHT)

        f_fila3 = tk.Frame(frame_detalles, bg="#f8fafc")
        f_fila3.pack(fill=tk.X, padx=8, pady=(2, 6))
        tk.Label(f_fila3, text="Total Estimado:", font=("Segoe UI", 10, "bold"), bg="#f8fafc", fg="#1e293b").pack(side=tk.LEFT)
        self.lbl_info_total = tk.Label(f_fila3, text="$0.00", font=("Segoe UI", 11, "bold"), bg="#f8fafc", fg="#16a34a")
        self.lbl_info_total.pack(side=tk.RIGHT)

        # Botones de Acción de Ventas
        lf_acciones_venta = ttk.LabelFrame(col_izquierda, text=" Acciones del Evento ")
        lf_acciones_venta.pack(fill=tk.X, pady=4, ipady=4)

        btn_registrar_venta = tk.Button(
            lf_acciones_venta,
            text="💳 Registrar Venta",
            font=("Segoe UI", 10, "bold"),
            bg="#16a34a",
            fg="#ffffff",
            activebackground="#15803d",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._callback_registrar_venta
        )
        btn_registrar_venta.pack(fill=tk.X, padx=10, pady=(6, 4), ipady=5)

        btn_limpiar_venta = tk.Button(
            lf_acciones_venta,
            text="🧹 Restablecer Selección",
            font=("Segoe UI", 9),
            bg="#64748b",
            fg="#ffffff",
            activebackground="#475569",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._limpiar_formulario_venta
        )
        btn_limpiar_venta.pack(fill=tk.X, padx=10, pady=4, ipady=3)

        # Estado de Ventas
        frame_estado = tk.Frame(col_izquierda, bg="#ffffff", bd=1, relief=tk.SOLID)
        frame_estado.pack(fill=tk.X, pady=(6, 0))

        self.label_estado_ventas = tk.Label(
            frame_estado,
            text="Seleccione un usuario, producto y cantidad para registrar la venta.",
            font=("Segoe UI", 8),
            bg="#ffffff",
            fg="#475569",
            wraplength=380,
            justify=tk.LEFT
        )
        self.label_estado_ventas.pack(fill=tk.X, padx=8, pady=6)

        # Columna Derecha: Tabla Treeview de Ventas
        col_derecha = tk.Frame(panel_horizontal, bg="#f1f5f9")
        col_derecha.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        lf_tabla_ventas = ttk.LabelFrame(col_derecha, text=" Historial de Ventas Registradas ")
        lf_tabla_ventas.pack(fill=tk.BOTH, expand=True)

        frame_tree_v = tk.Frame(lf_tabla_ventas, bg="#ffffff")
        frame_tree_v.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))

        columnas = ("id_venta", "fecha_hora", "usuario", "codigo", "producto", "cantidad", "precio_unit", "total")
        self.tree_ventas = ttk.Treeview(
            frame_tree_v,
            columns=columnas,
            show="headings",
            selectmode="browse"
        )

        self.tree_ventas.heading("id_venta", text="ID Venta")
        self.tree_ventas.heading("fecha_hora", text="Fecha y Hora")
        self.tree_ventas.heading("usuario", text="Usuario")
        self.tree_ventas.heading("codigo", text="Cód.")
        self.tree_ventas.heading("producto", text="Producto")
        self.tree_ventas.heading("cantidad", text="Cant.")
        self.tree_ventas.heading("precio_unit", text="P. Unit.")
        self.tree_ventas.heading("total", text="Total")

        self.tree_ventas.column("id_venta", width=70, anchor=tk.CENTER)
        self.tree_ventas.column("fecha_hora", width=140, anchor=tk.CENTER)
        self.tree_ventas.column("usuario", width=90, anchor=tk.CENTER)
        self.tree_ventas.column("codigo", width=65, anchor=tk.CENTER)
        self.tree_ventas.column("producto", width=170, anchor=tk.W)
        self.tree_ventas.column("cantidad", width=55, anchor=tk.CENTER)
        self.tree_ventas.column("precio_unit", width=75, anchor=tk.E)
        self.tree_ventas.column("total", width=85, anchor=tk.E)

        scroll_v = ttk.Scrollbar(frame_tree_v, orient=tk.VERTICAL, command=self.tree_ventas.yview)
        self.tree_ventas.configure(yscrollcommand=scroll_v.set)

        self.tree_ventas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_v.pack(side=tk.RIGHT, fill=tk.Y)

        frame_resumen = tk.Frame(lf_tabla_ventas, bg="#f8fafc", bd=1, relief=tk.GROOVE)
        frame_resumen.pack(fill=tk.X, padx=8, pady=(4, 8))

        self.lbl_resumen_ventas = tk.Label(
            frame_resumen,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg="#f8fafc",
            fg="#1e293b"
        )
        self.lbl_resumen_ventas.pack(side=tk.LEFT, padx=12, pady=6)

        self._actualizar_tabla_ventas()
        self._actualizar_calculo_total()

    def _refrescar_combo_productos_venta(self) -> None:
        """Actualiza la lista desplegable de productos con stock vigente."""
        productos = self.restaurante_servicio.obtener_productos()
        valores_productos = [
            f"{p.codigo} - {p.nombre} (${p.precio:.2f} | Stock: {p.stock})"
            for p in productos
        ]
        if self.combo_venta_producto:
            self.combo_venta_producto["values"] = valores_productos
            if valores_productos:
                self.combo_venta_producto.current(0)

    def _extraer_codigo_producto_seleccionado(self) -> Optional[str]:
        """Obtiene el código limpio del producto a partir del texto del combobox."""
        texto = self.var_venta_producto.get().strip()
        if not texto:
            return None
        partes = texto.split(" - ")
        return partes[0].strip() if partes else None

    def _extraer_username_seleccionado(self) -> Optional[str]:
        """Obtiene el username del usuario a partir del texto del combobox."""
        texto = self.var_venta_usuario.get().strip()
        if not texto:
            return None
        partes = texto.split(" - ")
        return partes[0].strip() if partes else None

    def _actualizar_calculo_total(self) -> None:
        """Calcula y proyecta el precio, stock y total según la selección activa."""
        codigo = self._extraer_codigo_producto_seleccionado()
        if not codigo:
            return

        producto = self.restaurante_servicio.consultar_producto(codigo)
        if not producto:
            return

        if self.lbl_info_precio:
            self.lbl_info_precio.config(text=f"${producto.precio:.2f}")

        if self.lbl_info_stock:
            color_stock = "#16a34a" if producto.stock > 5 else ("#d97706" if producto.stock > 0 else "#dc2626")
            self.lbl_info_stock.config(text=f"{producto.stock} unidades", fg=color_stock)

        try:
            cantidad = int(self.var_venta_cantidad.get().strip())
            if cantidad < 1:
                cantidad = 1
        except (ValueError, TypeError):
            cantidad = 1

        total = round(cantidad * producto.precio, 2)
        if self.lbl_info_total:
            self.lbl_info_total.config(text=f"${total:.2f}")

    def _actualizar_tabla_ventas(self) -> None:
        """Consulta las ventas en el servicio y refresca la vista tabular."""
        if not self.tree_ventas:
            return

        for item in self.tree_ventas.get_children():
            self.tree_ventas.delete(item)

        ventas = self.restaurante_servicio.obtener_ventas()
        total_acumulado = 0.0

        for v in ventas:
            total_acumulado += v.total
            self.tree_ventas.insert(
                "",
                tk.END,
                values=(
                    v.id_venta,
                    v.fecha_hora,
                    v.username,
                    v.codigo_producto,
                    v.nombre_producto,
                    v.cantidad,
                    f"${v.precio_unitario:.2f}",
                    f"${v.total:.2f}"
                )
            )

        if self.lbl_resumen_ventas:
            self.lbl_resumen_ventas.config(
                text=f"📊 Total de Ventas: {len(ventas)} registros  |  💰 Importe Total Acumulado: ${total_acumulado:.2f}"
            )

    def _callback_registrar_venta(self) -> None:
        """Callback principal activado por el botón 'Registrar Venta'."""
        username = self._extraer_username_seleccionado()
        codigo = self._extraer_codigo_producto_seleccionado()
        cantidad_str = self.var_venta_cantidad.get().strip()

        if not username:
            self._mostrar_estado_venta("⚠️ Debe seleccionar un usuario registrado.", tipo="advertencia")
            messagebox.showwarning("Atención", "Por favor, seleccione un usuario de la lista.")
            return

        if not codigo:
            self._mostrar_estado_venta("⚠️ Debe seleccionar un producto del catálogo.", tipo="advertencia")
            messagebox.showwarning("Atención", "Por favor, seleccione un producto disponible.")
            return

        try:
            cantidad = int(cantidad_str)
            if cantidad <= 0:
                self._mostrar_estado_venta("⚠️ La cantidad debe ser un entero mayor a cero.", tipo="advertencia")
                messagebox.showwarning("Cantidad Inválida", "La cantidad debe ser mayor a 0.")
                return
        except ValueError:
            self._mostrar_estado_venta("⚠️ La cantidad ingresada no es válida.", tipo="error")
            messagebox.showwarning("Cantidad Inválida", "Ingrese un número entero válido para la cantidad.")
            return

        exito, mensaje, nueva_venta = self.restaurante_servicio.registrar_venta(
            username=username,
            codigo_producto=codigo,
            cantidad=cantidad
        )

        if exito and nueva_venta:
            self._mostrar_estado_venta(f"✅ {mensaje}", tipo="exito")
            self._actualizar_tabla_ventas()
            self._refrescar_combo_productos_venta()
            self._actualizar_calculo_total()
            self.var_venta_cantidad.set("1")
            messagebox.showinfo("Venta Registrada", mensaje)
        else:
            self._mostrar_estado_venta(f"❌ {mensaje}", tipo="error")
            messagebox.showwarning("No se pudo registrar la venta", mensaje)

    def _limpiar_formulario_venta(self) -> None:
        """Reinicia los valores del formulario de venta."""
        self.var_venta_cantidad.set("1")
        self._refrescar_combo_productos_venta()
        self._actualizar_calculo_total()
        self._mostrar_estado_venta("Formulario de venta restablecido.", tipo="info")

    def _mostrar_estado_venta(self, mensaje: str, tipo: str = "info") -> None:
        """Actualiza la barra de estado de ventas con estilo cromático."""
        colores = {
            "exito": "#16a34a",
            "error": "#dc2626",
            "advertencia": "#d97706",
            "info": "#475569"
        }
        if self.label_estado_ventas:
            color = colores.get(tipo, "#475569")
            self.label_estado_ventas.config(text=mensaje, fg=color)

    # =============================================================
    # SECCIÓN: GESTIÓN DE PRODUCTOS (CONSERVADA DE SEMANAS ANTERIORES)
    # =============================================================

    def mostrar_seccion_productos(self) -> None:
        """Construye la vista de productos con formulario, botones y catálogo."""
        self._limpiar_contenido()

        panel_horizontal = tk.Frame(self.frame_contenido, bg="#f1f5f9")
        panel_horizontal.pack(fill=tk.BOTH, expand=True)

        col_izquierda = tk.Frame(panel_horizontal, bg="#f1f5f9", width=380)
        col_izquierda.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        col_izquierda.pack_propagate(False)

        lf_formulario = ttk.LabelFrame(col_izquierda, text=" Formulario de Producto ")
        lf_formulario.pack(fill=tk.X, pady=(0, 8), ipady=4)
        lf_formulario.columnconfigure(1, weight=1)

        ttk.Label(lf_formulario, text="Código:", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=6
        )
        self.entry_codigo = ttk.Entry(lf_formulario, textvariable=self.var_codigo, font=("Segoe UI", 9))
        self.entry_codigo.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=6)

        ttk.Label(lf_formulario, text="Nombre:", font=("Segoe UI", 9, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=6
        )
        self.entry_nombre = ttk.Entry(lf_formulario, textvariable=self.var_nombre, font=("Segoe UI", 9))
        self.entry_nombre.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=6)

        ttk.Label(lf_formulario, text="Categoría:", font=("Segoe UI", 9, "bold")).grid(
            row=2, column=0, sticky=tk.W, padx=10, pady=6
        )
        categorias = ["Plato Fuerte", "Entrada", "Bebida", "Postre", "Acompañamiento", "General"]
        self.combo_categoria = ttk.Combobox(
            lf_formulario,
            textvariable=self.var_categoria,
            values=categorias,
            state="readonly",
            font=("Segoe UI", 9)
        )
        self.combo_categoria.grid(row=2, column=1, sticky=tk.EW, padx=10, pady=6)
        if categorias:
            self.combo_categoria.current(0)

        ttk.Label(lf_formulario, text="Precio ($):", font=("Segoe UI", 9, "bold")).grid(
            row=3, column=0, sticky=tk.W, padx=10, pady=6
        )
        self.entry_precio = ttk.Entry(lf_formulario, textvariable=self.var_precio, font=("Segoe UI", 9))
        self.entry_precio.grid(row=3, column=1, sticky=tk.EW, padx=10, pady=6)

        ttk.Label(lf_formulario, text="Stock:", font=("Segoe UI", 9, "bold")).grid(
            row=4, column=0, sticky=tk.W, padx=10, pady=6
        )
        self.spin_stock = ttk.Spinbox(
            lf_formulario,
            from_=0,
            to=9999,
            textvariable=self.var_stock,
            font=("Segoe UI", 9)
        )
        self.spin_stock.grid(row=4, column=1, sticky=tk.EW, padx=10, pady=6)

        lf_acciones = ttk.LabelFrame(col_izquierda, text=" Operaciones Disponibles ")
        lf_acciones.pack(fill=tk.X, pady=4, ipady=4)

        btn_registrar = tk.Button(
            lf_acciones,
            text="➕ Registrar Producto",
            font=("Segoe UI", 9, "bold"),
            bg="#16a34a",
            fg="#ffffff",
            activebackground="#15803d",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._accion_registrar_producto
        )
        btn_registrar.pack(fill=tk.X, padx=10, pady=4, ipady=3)

        btn_consultar = tk.Button(
            lf_acciones,
            text="🔍 Cargar / Consultar (por Código)",
            font=("Segoe UI", 9, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._accion_consultar_producto
        )
        btn_consultar.pack(fill=tk.X, padx=10, pady=4, ipady=3)

        btn_actualizar = tk.Button(
            lf_acciones,
            text="✏️ Actualizar Producto",
            font=("Segoe UI", 9, "bold"),
            bg="#d97706",
            fg="#ffffff",
            activebackground="#b45309",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._accion_actualizar_producto
        )
        btn_actualizar.pack(fill=tk.X, padx=10, pady=4, ipady=3)

        btn_eliminar = tk.Button(
            lf_acciones,
            text="🗑️ Eliminar Producto",
            font=("Segoe UI", 9, "bold"),
            bg="#dc2626",
            fg="#ffffff",
            activebackground="#b91c1c",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._accion_eliminar_producto
        )
        btn_eliminar.pack(fill=tk.X, padx=10, pady=4, ipady=3)

        btn_limpiar = tk.Button(
            lf_acciones,
            text="🧹 Limpiar Campos",
            font=("Segoe UI", 9),
            bg="#64748b",
            fg="#ffffff",
            activebackground="#475569",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self._limpiar_formulario_producto
        )
        btn_limpiar.pack(fill=tk.X, padx=10, pady=4, ipady=3)

        frame_estado = tk.Frame(col_izquierda, bg="#ffffff", bd=1, relief=tk.SOLID)
        frame_estado.pack(fill=tk.X, pady=(6, 0))

        self.label_estado_productos = tk.Label(
            frame_estado,
            text="Listo para gestionar productos.",
            font=("Segoe UI", 8),
            bg="#ffffff",
            fg="#475569",
            wraplength=340,
            justify=tk.LEFT
        )
        self.label_estado_productos.pack(fill=tk.X, padx=8, pady=6)

        col_derecha = tk.Frame(panel_horizontal, bg="#f1f5f9")
        col_derecha.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        lf_tabla = ttk.LabelFrame(col_derecha, text=" Catálogo de Productos Registrados ")
        lf_tabla.pack(fill=tk.BOTH, expand=True)

        frame_tree = tk.Frame(lf_tabla, bg="#ffffff")
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        columnas = ("codigo", "nombre", "categoria", "precio", "stock")
        self.tree_productos = ttk.Treeview(
            frame_tree,
            columns=columnas,
            show="headings",
            selectmode="browse"
        )

        self.tree_productos.heading("codigo", text="Código")
        self.tree_productos.heading("nombre", text="Nombre")
        self.tree_productos.heading("categoria", text="Categoría")
        self.tree_productos.heading("precio", text="Precio")
        self.tree_productos.heading("stock", text="Stock")

        self.tree_productos.column("codigo", width=80, anchor=tk.CENTER)
        self.tree_productos.column("nombre", width=180, anchor=tk.W)
        self.tree_productos.column("categoria", width=120, anchor=tk.CENTER)
        self.tree_productos.column("precio", width=90, anchor=tk.E)
        self.tree_productos.column("stock", width=80, anchor=tk.CENTER)

        scrollbar_y = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, command=self.tree_productos.yview)
        self.tree_productos.configure(yscrollcommand=scrollbar_y.set)

        self.tree_productos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self._actualizar_tabla_productos()

    def _actualizar_tabla_productos(self) -> None:
        """Refresca la tabla de productos consultando al servicio."""
        if not self.tree_productos:
            return

        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)

        productos = self.restaurante_servicio.obtener_productos()
        for p in productos:
            self.tree_productos.insert(
                "",
                tk.END,
                values=(
                    p.codigo,
                    p.nombre,
                    p.categoria,
                    f"${p.precio:.2f}",
                    p.stock
                )
            )

    def _accion_registrar_producto(self) -> None:
        """Coordina el registro de un producto delegando a RestauranteServicio."""
        codigo = self.var_codigo.get().strip()
        nombre = self.var_nombre.get().strip()
        categoria = self.var_categoria.get().strip()
        precio_str = self.var_precio.get().strip()
        stock_str = self.var_stock.get().strip()

        exito, mensaje = self.restaurante_servicio.registrar_producto(
            codigo=codigo,
            nombre=nombre,
            precio=precio_str,
            categoria=categoria,
            stock=stock_str
        )

        if exito:
            self._mostrar_estado_producto(f"✅ {mensaje}", tipo="exito")
            self._actualizar_tabla_productos()
            self._limpiar_formulario_producto(conservar_estado=True)
            messagebox.showinfo("Producto Registrado", mensaje)
        else:
            self._mostrar_estado_producto(f"❌ {mensaje}", tipo="error")
            messagebox.showwarning("Atención", mensaje)

    def _accion_consultar_producto(self) -> None:
        """Consulta un producto por código y carga sus valores en el formulario."""
        codigo = self.var_codigo.get().strip()
        if not codigo:
            self._mostrar_estado_producto("⚠️ Ingrese el código del producto para consultar.", tipo="advertencia")
            messagebox.showinfo("Consulta", "Por favor, ingrese un código en el campo correspondiente.")
            return

        producto = self.restaurante_servicio.consultar_producto(codigo)

        if producto:
            self.var_codigo.set(producto.codigo)
            self.var_nombre.set(producto.nombre)
            self.var_categoria.set(producto.categoria)
            self.var_precio.set(str(producto.precio))
            self.var_stock.set(str(producto.stock))
            self._mostrar_estado_producto(f"✅ Producto '{producto.nombre}' cargado en el formulario.", tipo="exito")
        else:
            self._mostrar_estado_producto(f"❌ No existe ningún producto con el código '{codigo.upper()}'.", tipo="error")
            messagebox.showinfo("No encontrado", f"No se encontró un producto con el código '{codigo.upper()}'.")

    def _accion_actualizar_producto(self) -> None:
        """Coordina la actualización de un producto existente."""
        codigo = self.var_codigo.get().strip()
        nombre = self.var_nombre.get().strip()
        categoria = self.var_categoria.get().strip()
        precio_str = self.var_precio.get().strip()
        stock_str = self.var_stock.get().strip()

        exito, mensaje = self.restaurante_servicio.actualizar_producto(
            codigo=codigo,
            nombre=nombre,
            precio=precio_str,
            categoria=categoria,
            stock=stock_str
        )

        if exito:
            self._mostrar_estado_producto(f"✅ {mensaje}", tipo="exito")
            self._actualizar_tabla_productos()
            messagebox.showinfo("Actualización Exitosa", mensaje)
        else:
            self._mostrar_estado_producto(f"❌ {mensaje}", tipo="error")
            messagebox.showwarning("Error de Actualización", mensaje)

    def _accion_eliminar_producto(self) -> None:
        """Coordina la eliminación de un producto con confirmación."""
        codigo = self.var_codigo.get().strip()
        if not codigo:
            self._mostrar_estado_producto("⚠️ Ingrese o consulte el código del producto a eliminar.", tipo="advertencia")
            messagebox.showwarning("Atención", "Debe especificar el código del producto a eliminar.")
            return

        producto = self.restaurante_servicio.consultar_producto(codigo)
        if not producto:
            self._mostrar_estado_producto(f"❌ No existe un producto con el código '{codigo.upper()}'.", tipo="error")
            messagebox.showwarning("No encontrado", f"No existe el producto '{codigo.upper()}'.")
            return

        confirmacion = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el producto '{producto.nombre}' [{producto.codigo}]?\nEsta acción no se puede deshacer."
        )

        if confirmacion:
            exito, mensaje = self.restaurante_servicio.eliminar_producto(codigo)
            if exito:
                self._mostrar_estado_producto(f"✅ {mensaje}", tipo="exito")
                self._actualizar_tabla_productos()
                self._limpiar_formulario_producto(conservar_estado=True)
                messagebox.showinfo("Producto Eliminado", mensaje)
            else:
                self._mostrar_estado_producto(f"❌ {mensaje}", tipo="error")
                messagebox.showerror("Error", mensaje)

    def _limpiar_formulario_producto(self, conservar_estado: bool = False) -> None:
        """Limpia los campos del formulario de producto."""
        self.var_codigo.set("")
        self.var_nombre.set("")
        if self.combo_categoria and self.combo_categoria["values"]:
            self.combo_categoria.current(0)
        self.var_precio.set("")
        self.var_stock.set("0")

        if not conservar_estado:
            self._mostrar_estado_producto("Formulario reiniciado. Ingrese nuevos datos o consulte.", tipo="info")

        if self.entry_codigo:
            self.entry_codigo.focus()

    def _mostrar_estado_producto(self, mensaje: str, tipo: str = "info") -> None:
        """Actualiza la barra de estado de productos."""
        colores = {
            "exito": "#16a34a",
            "error": "#dc2626",
            "advertencia": "#d97706",
            "info": "#475569"
        }
        if self.label_estado_productos:
            color = colores.get(tipo, "#475569")
            self.label_estado_productos.config(text=mensaje, fg=color)

    # =============================================================
    # MÉTODOS AUXILIARES Y CIERRE DE SESIÓN
    # =============================================================

    def _limpiar_contenido(self) -> None:
        """Limpia el contenedor dinámico para cambiar de sección."""
        if self.frame_contenido:
            for widget in self.frame_contenido.winfo_children():
                widget.destroy()

    def cerrar_sesion(self) -> None:
        """Confirma y regresa a la vista de Login."""
        respuesta = messagebox.askyesno(
            "Cerrar Sesión",
            f"¿Desea cerrar la sesión del usuario '{self.usuario_actual}'?"
        )
        if respuesta:
            self.cambiar_vista_callback("login", None)
