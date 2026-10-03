from typing import Optional


class Usuario:
    """
    Representa un usuario del sistema de restaurante con credenciales y rol asignado.
    Permite autenticación y control de acceso básico entre Administrador,
    Empleado y Cliente para la gestión del restaurante.
    """

    ROLES_PERMITIDOS = ("Administrador", "Empleado", "Cliente")

    def __init__(
        self,
        id_usuario: str,
        username: str,
        password: str,
        nombre: str,
        rol: str = "Empleado"
    ):
        """
        Inicializa una instancia de Usuario.

        Args:
            id_usuario: Identificador único del usuario (ej: 'U001')
            username: Nombre de usuario único para inicio de sesión
            password: Contraseña de acceso
            nombre: Nombre completo del usuario
            rol: Rol asignado ('Administrador', 'Empleado' o 'Cliente')
        """
        id_limpio = str(id_usuario).strip()
        user_limpio = str(username).strip()
        nombre_limpio = str(nombre).strip()
        rol_limpio = str(rol).strip()

        if not user_limpio:
            raise ValueError("El nombre de usuario (username) no puede estar vacío.")
        if not nombre_limpio:
            raise ValueError("El nombre del usuario no puede estar vacío.")

        # Normalizar y validar rol
        rol_normalizado = next(
            (r for r in self.ROLES_PERMITIDOS if r.lower() == rol_limpio.lower()),
            "Empleado"
        )

        self.id_usuario = id_limpio if id_limpio else "U000"
        self.username = user_limpio
        self.password = str(password)
        self.nombre = nombre_limpio
        self.rol = rol_normalizado

    def validar_credenciales(self, username: str, password: str) -> bool:
        """Valida que el nombre de usuario y contraseña coincidan."""
        return self.username.lower() == str(username).strip().lower() and self.password == str(password)

    def es_administrador(self) -> bool:
        """Retorna True si el usuario tiene rol de Administrador."""
        return self.rol.lower() == "administrador"

    def es_empleado(self) -> bool:
        """Retorna True si el usuario tiene rol de Empleado."""
        return self.rol.lower() == "empleado"

    def es_cliente(self) -> bool:
        """Retorna True si el usuario tiene rol de Cliente."""
        return self.rol.lower() == "cliente"

    def actualizar(self, nombre: str, rol: str, password: Optional[str] = None) -> None:
        """
        Actualiza los datos del usuario.

        Args:
            nombre: Nuevo nombre completo
            rol: Nuevo rol
            password: Nueva contraseña (opcional, si es None o vacía se conserva la actual)
        """
        nombre_limpio = str(nombre).strip()
        if not nombre_limpio:
            raise ValueError("El nombre no puede estar vacío.")

        rol_limpio = str(rol).strip()
        rol_normalizado = next(
            (r for r in self.ROLES_PERMITIDOS if r.lower() == rol_limpio.lower()),
            None
        )
        if not rol_normalizado:
            raise ValueError(f"El rol '{rol}' no es válido. Opciones: {', '.join(self.ROLES_PERMITIDOS)}")

        self.nombre = nombre_limpio
        self.rol = rol_normalizado

        if password is not None and str(password).strip():
            self.password = str(password).strip()

    def convertir_a_diccionario(self) -> dict:
        """Convierte el usuario a un diccionario serializable para JSON."""
        return {
            "id_usuario": self.id_usuario,
            "username": self.username,
            "password": self.password,
            "nombre": self.nombre,
            "rol": self.rol
        }

    @staticmethod
    def desde_diccionario(datos: dict) -> "Usuario":
        """Reconstruye un Usuario a partir de un diccionario."""
        username = datos.get("username", "")
        # Rol por defecto: si es admin -> Administrador, de lo contrario Empleado
        rol_defecto = "Administrador" if str(username).lower() == "admin" else "Empleado"
        rol = datos.get("rol", rol_defecto)
        id_usuario = datos.get("id_usuario", "")

        return Usuario(
            id_usuario=id_usuario,
            username=username,
            password=datos.get("password", ""),
            nombre=datos.get("nombre", ""),
            rol=rol
        )

    def __str__(self) -> str:
        return f"[{self.id_usuario}] {self.nombre} (@{self.username}) - Rol: {self.rol}"
