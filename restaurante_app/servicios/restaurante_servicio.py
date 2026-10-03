from datetime import datetime
import re
from typing import List, Optional, Tuple
from modelos.usuario import Usuario
from modelos.producto import Producto
from modelos.venta import Venta
from servicios.archivo_servicio import ArchivoServicio


class RestauranteServicio:
    """
    Servicio principal que gestiona la lógica de negocio del restaurante (Semana 16).
    Administra la autenticación, CRUD y control de acceso de usuarios con roles,
    gestión completa de productos y catálogo, y registro de ventas con persistencia
    en archivos JSON.
    """

    def __init__(self, archivo_servicio: ArchivoServicio):
        """
        Inicializa el servicio del restaurante.

        Args:
            archivo_servicio: Instancia de ArchivoServicio para persistencia
        """
        self.archivo_servicio = archivo_servicio
        self.usuarios: List[Usuario] = []
        self.productos: List[Producto] = []
        self.ventas: List[Venta] = []
        self._cargar_datos()

    def _cargar_datos(self) -> None:
        """Carga usuarios, productos y ventas desde los archivos JSON correspondientes."""
        # 1. Cargar usuarios
        datos_usuarios = self.archivo_servicio.cargar_json("usuarios.json")
        self.usuarios = []
        necesita_guardar_usuarios = False

        for idx, u in enumerate(datos_usuarios):
            usuario_obj = Usuario.desde_diccionario(u)
            # Asegurar que tenga ID válido si venía de versión anterior
            if not usuario_obj.id_usuario or usuario_obj.id_usuario == "U000":
                usuario_obj.id_usuario = f"U{idx + 1:03d}"
                necesita_guardar_usuarios = True
            self.usuarios.append(usuario_obj)

        if necesita_guardar_usuarios:
            self._guardar_usuarios()

        # 2. Cargar productos
        datos_productos = self.archivo_servicio.cargar_json("productos.json")
        self.productos = [Producto.desde_diccionario(p) for p in datos_productos]

        # 3. Cargar ventas
        datos_ventas = self.archivo_servicio.cargar_json("ventas.json")
        self.ventas = [Venta.desde_diccionario(v) for v in datos_ventas]

    def _guardar_usuarios(self) -> bool:
        """Persiste la lista actual de usuarios en el archivo usuarios.json."""
        datos = [u.convertir_a_diccionario() for u in self.usuarios]
        return self.archivo_servicio.guardar_json("usuarios.json", datos)

    def _guardar_productos(self) -> bool:
        """Persiste la lista actual de productos en el archivo productos.json."""
        datos = [p.convertir_a_diccionario() for p in self.productos]
        return self.archivo_servicio.guardar_json("productos.json", datos)

    def _guardar_ventas(self) -> bool:
        """Persiste la lista actual de ventas en el archivo ventas.json."""
        datos = [v.convertir_a_diccionario() for v in self.ventas]
        return self.archivo_servicio.guardar_json("ventas.json", datos)

    # -------------------------------------------------------------
    # GESTIÓN DE USUARIOS Y AUTENTICACIÓN (SEMANA 16 - CRUD Y ROLES)
    # -------------------------------------------------------------

    def validar_acceso(self, username: str, password: str) -> bool:
        """
        Valida las credenciales de un usuario para inicio de sesión.

        Args:
            username: Nombre de usuario
            password: Contraseña del usuario

        Returns:
            True si las credenciales son válidas, False de lo contrario.
        """
        if not username or not password:
            return False

        for usuario in self.usuarios:
            if usuario.validar_credenciales(username, password):
                return True
        return False

    def obtener_usuarios(self) -> List[Usuario]:
        """Retorna la lista de todos los usuarios registrados."""
        return self.usuarios

    def consultar_usuario(self, identificador: str) -> Optional[Usuario]:
        """
        Busca un usuario por su identificador único (id_usuario) o por su username.

        Args:
            identificador: id_usuario (ej: 'U001') o username (ej: 'admin')

        Returns:
            Instancia de Usuario si se encuentra, o None si no existe.
        """
        if not identificador:
            return None
        id_limpio = str(identificador).strip().lower()

        # 1. Buscar por id_usuario
        for usuario in self.usuarios:
            if usuario.id_usuario.lower() == id_limpio:
                return usuario

        # 2. Buscar por username
        for usuario in self.usuarios:
            if usuario.username.lower() == id_limpio:
                return usuario

        return None

    def obtener_usuario_por_username(self, username: str) -> Optional[Usuario]:
        """Busca y retorna un usuario específicamente por su nombre de usuario."""
        username_limpio = str(username).strip().lower()
        for usuario in self.usuarios:
            if usuario.username.lower() == username_limpio:
                return usuario
        return None

    def es_usuario_admin(self, username: str) -> bool:
        """
        Determina si un usuario determinado posee rol de Administrador.

        Args:
            username: Nombre de usuario a evaluar

        Returns:
            True si el usuario existe y es Administrador, False en caso contrario.
        """
        usuario = self.obtener_usuario_por_username(username)
        return usuario.es_administrador() if usuario else False

    def _generar_siguiente_id_usuario(self) -> str:
        """Genera un nuevo identificador secuencial para usuario (ej. U001, U002)."""
        max_num = 0
        patron = re.compile(r"^U(\d+)$", re.IGNORECASE)
        for u in self.usuarios:
            match = patron.match(u.id_usuario.strip())
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num

        nuevo_num = max_num + 1
        return f"U{nuevo_num:03d}"

    def registrar_usuario(
        self,
        username: str,
        password: str,
        nombre: str,
        rol: str
    ) -> Tuple[bool, str, Optional[Usuario]]:
        """
        Registra un nuevo usuario en el sistema con validaciones de negocio.

        Args:
            username: Nombre de usuario único
            password: Contraseña de acceso
            nombre: Nombre completo del usuario
            rol: Rol asignado ('Administrador', 'Empleado' o 'Cliente')

        Returns:
            Tupla (éxito: bool, mensaje: str, nuevo_usuario: Optional[Usuario])
        """
        username = str(username).strip()
        password = str(password).strip()
        nombre = str(nombre).strip()
        rol = str(rol).strip()

        # 1. Validaciones de presencia
        if not username:
            return False, "El nombre de usuario (username) es obligatorio.", None
        if not password:
            return False, "La contraseña es obligatoria.", None
        if not nombre:
            return False, "El nombre completo del usuario es obligatorio.", None
        if not rol:
            return False, "Debe seleccionar un rol para el usuario.", None

        # 2. Validación de longitud
        if len(username) < 3:
            return False, "El nombre de usuario debe tener al menos 3 caracteres.", None
        if len(password) < 4:
            return False, "La contraseña debe contener al menos 4 caracteres.", None

        # 3. Validación de formato de username
        if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
            return False, "El nombre de usuario solo puede contener letras, números, puntos y guiones.", None

        # 4. Validar unicidad del nombre de usuario
        if self.obtener_usuario_por_username(username) is not None:
            return False, f"El nombre de usuario '{username}' ya se encuentra registrado.", None

        # 5. Validar rol permitido
        rol_normalizado = next(
            (r for r in Usuario.ROLES_PERMITIDOS if r.lower() == rol.lower()),
            None
        )
        if not rol_normalizado:
            return False, f"El rol '{rol}' no es válido. Opciones permitidas: {', '.join(Usuario.ROLES_PERMITIDOS)}.", None

        # 6. Crear usuario y persistir
        try:
            nuevo_id = self._generar_siguiente_id_usuario()
            nuevo_usuario = Usuario(
                id_usuario=nuevo_id,
                username=username,
                password=password,
                nombre=nombre,
                rol=rol_normalizado
            )
            self.usuarios.append(nuevo_usuario)

            if self._guardar_usuarios():
                mensaje = (
                    f"Usuario '{nombre}' (@{username}) registrado con éxito "
                    f"con ID [{nuevo_id}] y rol '{rol_normalizado}'."
                )
                return True, mensaje, nuevo_usuario
            else:
                return False, "Error al persistir el nuevo usuario en el archivo JSON.", None
        except Exception as e:
            return False, f"Error inesperado al crear usuario: {str(e)}", None

    def actualizar_usuario(
        self,
        id_usuario: str,
        nombre: str,
        rol: str,
        password: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Actualiza los datos de un usuario existente.

        Args:
            id_usuario: Identificador único del usuario a actualizar
            nombre: Nuevo nombre completo
            rol: Nuevo rol asignado
            password: Nueva contraseña (opcional; si está vacía no se altera)

        Returns:
            Tupla (éxito: bool, mensaje: str)
        """
        id_limpio = str(id_usuario).strip()
        nombre = str(nombre).strip()
        rol = str(rol).strip()

        if not id_limpio:
            return False, "Debe especificar el identificador del usuario a actualizar."

        usuario = self.consultar_usuario(id_limpio)
        if usuario is None:
            return False, f"No se encontró ningún usuario con el identificador '{id_limpio}'."

        if not nombre:
            return False, "El nombre completo no puede quedar vacío."

        # Validar rol
        rol_normalizado = next(
            (r for r in Usuario.ROLES_PERMITIDOS if r.lower() == rol.lower()),
            None
        )
        if not rol_normalizado:
            return False, f"El rol '{rol}' no es válido. Opciones permitidas: {', '.join(Usuario.ROLES_PERMITIDOS)}."

        # Regla de seguridad: no dejar el sistema sin administradores
        if usuario.es_administrador() and rol_normalizado != "Administrador":
            otros_admins = [u for u in self.usuarios if u.es_administrador() and u.id_usuario != usuario.id_usuario]
            if not otros_admins:
                return False, "No se puede retirar el rol de Administrador al único administrador registrado en el sistema."

        # Validar contraseña opcional
        if password is not None and str(password).strip():
            pass_limpio = str(password).strip()
            if len(pass_limpio) < 4:
                return False, "La nueva contraseña debe tener al menos 4 caracteres."
            usuario.password = pass_limpio

        # Aplicar cambios
        try:
            usuario.nombre = nombre
            usuario.rol = rol_normalizado

            if self._guardar_usuarios():
                return True, f"Usuario '{usuario.username}' [{usuario.id_usuario}] actualizado exitosamente."
            else:
                return False, "Error al persistir la actualización del usuario en el archivo JSON."
        except Exception as e:
            return False, f"Error al actualizar el usuario: {str(e)}"

    def eliminar_usuario(self, id_usuario: str, username_en_sesion: str) -> Tuple[bool, str]:
        """
        Elimina un usuario del sistema aplicando las reglas de seguridad requeridas:
        1. No permite eliminar la cuenta con la que actualmente se ha iniciado sesión.
        2. No permite eliminar al único usuario con rol Administrador.

        Args:
            id_usuario: Identificador del usuario a eliminar
            username_en_sesion: Nombre de usuario autenticado actualmente

        Returns:
            Tupla (éxito: bool, mensaje: str)
        """
        id_limpio = str(id_usuario).strip()
        if not id_limpio:
            return False, "Debe especificar el identificador del usuario a eliminar."

        usuario = self.consultar_usuario(id_limpio)
        if usuario is None:
            return False, f"No se encontró ningún usuario con el identificador '{id_limpio}'."

        # Regla de seguridad 1: No eliminar la cuenta en sesión activa
        if usuario.username.lower() == str(username_en_sesion).strip().lower():
            return False, "Acción bloqueada: No puede eliminar la cuenta administrativa con la que ha iniciado sesión actualmente."

        # Regla de seguridad 2: No eliminar al último administrador
        if usuario.es_administrador():
            total_admins = [u for u in self.usuarios if u.es_administrador()]
            if len(total_admins) <= 1:
                return False, "Acción bloqueada: No se puede eliminar al único Administrador disponible en el sistema."

        # Eliminar y persistir
        nombre_eliminado = usuario.nombre
        username_eliminado = usuario.username
        self.usuarios.remove(usuario)

        if self._guardar_usuarios():
            return True, f"Usuario '{nombre_eliminado}' (@{username_eliminado}) eliminado exitosamente."
        else:
            return False, "Error al persistir la eliminación del usuario en el archivo JSON."

    # -------------------------------------------------------------
    # GESTIÓN DE PRODUCTOS (CRUD Y VALIDACIONES)
    # -------------------------------------------------------------

    def obtener_productos(self) -> List[Producto]:
        """Retorna la lista de todos los productos disponibles."""
        return self.productos

    def consultar_producto(self, codigo: str) -> Optional[Producto]:
        """Busca un producto por su código identificador."""
        if not codigo:
            return None
        codigo_limpio = str(codigo).strip().upper()
        for producto in self.productos:
            if producto.codigo.upper() == codigo_limpio:
                return producto
        return None

    def registrar_producto(
        self,
        codigo: str,
        nombre: str,
        precio: float,
        categoria: str,
        stock: int
    ) -> Tuple[bool, str]:
        """Registra un nuevo producto tras validar las reglas de negocio."""
        codigo = str(codigo).strip().upper()
        nombre = str(nombre).strip()
        categoria = str(categoria).strip()

        if not codigo:
            return False, "El código del producto es obligatorio."
        if not nombre:
            return False, "El nombre del producto es obligatorio."
        if not categoria:
            return False, "La categoría del producto es obligatoria."

        if self.consultar_producto(codigo) is not None:
            return False, f"El código '{codigo}' ya está asignado a otro producto."

        try:
            precio_float = float(precio)
            if precio_float <= 0:
                return False, "El precio debe ser un valor mayor a $0.00."
        except (ValueError, TypeError):
            return False, "El precio ingresado no es un número válido."

        try:
            stock_int = int(stock)
            if stock_int < 0:
                return False, "El stock no puede ser un número negativo."
        except (ValueError, TypeError):
            return False, "El stock debe ser un número entero válido."

        try:
            nuevo_producto = Producto(
                codigo=codigo,
                nombre=nombre,
                precio=precio_float,
                categoria=categoria,
                stock=stock_int
            )
            self.productos.append(nuevo_producto)

            if self._guardar_productos():
                return True, f"Producto '{nombre}' registrado exitosamente."
            else:
                return False, "Error al guardar el producto en el archivo de datos."
        except Exception as e:
            return False, f"Error inesperado al crear producto: {str(e)}"

    def actualizar_producto(
        self,
        codigo: str,
        nombre: str,
        precio: float,
        categoria: str,
        stock: int
    ) -> Tuple[bool, str]:
        """Actualiza la información de un producto existente."""
        codigo = str(codigo).strip().upper()
        nombre = str(nombre).strip()
        categoria = str(categoria).strip()

        if not codigo:
            return False, "Debe especificar el código del producto a actualizar."

        producto = self.consultar_producto(codigo)
        if producto is None:
            return False, f"No se encontró ningún producto con el código '{codigo}'."

        if not nombre:
            return False, "El nombre del producto no puede estar vacío."
        if not categoria:
            return False, "La categoría no puede estar vacía."

        try:
            precio_float = float(precio)
            if precio_float <= 0:
                return False, "El precio debe ser mayor a $0.00."
        except (ValueError, TypeError):
            return False, "El precio ingresado no es válido."

        try:
            stock_int = int(stock)
            if stock_int < 0:
                return False, "El stock no puede ser negativo."
        except (ValueError, TypeError):
            return False, "El stock debe ser un entero válido."

        try:
            producto.actualizar(
                nombre=nombre,
                precio=precio_float,
                categoria=categoria,
                stock=stock_int
            )

            if self._guardar_productos():
                return True, f"Producto '{codigo}' actualizado exitosamente."
            else:
                return False, "Error al persistir la actualización en el archivo."
        except Exception as e:
            return False, f"Error al actualizar producto: {str(e)}"

    def eliminar_producto(self, codigo: str) -> Tuple[bool, str]:
        """Elimina un producto del restaurante según su código."""
        codigo = str(codigo).strip().upper()
        if not codigo:
            return False, "Debe especificar el código del producto a eliminar."

        producto = self.consultar_producto(codigo)
        if producto is None:
            return False, f"No se encontró ningún producto con el código '{codigo}'."

        nombre = producto.nombre
        self.productos.remove(producto)

        if self._guardar_productos():
            return True, f"Producto '{nombre}' [{codigo}] eliminado exitosamente."
        else:
            return False, "Error al persistir la eliminación en el archivo."

    # -------------------------------------------------------------
    # GESTIÓN DE VENTAS (MÉTODOS Y PERSISTENCIA)
    # -------------------------------------------------------------

    def obtener_ventas(self) -> List[Venta]:
        """Retorna la lista histórica de todas las ventas registradas."""
        return self.ventas

    def consultar_venta(self, id_venta: str) -> Optional[Venta]:
        """Busca una venta registrada por su identificador."""
        id_limpio = str(id_venta).strip().upper()
        for venta in self.ventas:
            if venta.id_venta.upper() == id_limpio:
                return venta
        return None

    def _generar_siguiente_id_venta(self) -> str:
        """Genera un nuevo identificador secuencial para la venta (ej. V001, V002)."""
        max_num = 0
        patron = re.compile(r"^V(\d+)$", re.IGNORECASE)
        for v in self.ventas:
            match = patron.match(v.id_venta.strip())
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num

        nuevo_num = max_num + 1
        return f"V{nuevo_num:03d}"

    def registrar_venta(
        self,
        username: str,
        codigo_producto: str,
        cantidad: int = 1
    ) -> Tuple[bool, str, Optional[Venta]]:
        """
        Registra una venta que relaciona un usuario con un producto y persiste
        la transacción en ventas.json descontando simultáneamente el stock.

        Args:
            username: Nombre de usuario registrado que realiza o autoriza la venta
            codigo_producto: Código del producto vendido
            cantidad: Cantidad de unidades solicitadas (debe ser > 0)

        Returns:
            Tupla (éxito: bool, mensaje: str, venta: Optional[Venta])
        """
        username_limpio = str(username).strip()
        codigo_limpio = str(codigo_producto).strip().upper()

        if not username_limpio:
            return False, "Debe seleccionar un usuario para registrar la venta.", None

        usuario = self.obtener_usuario_por_username(username_limpio)
        if usuario is None:
            return False, f"El usuario '{username_limpio}' no existe en el sistema.", None

        if not codigo_limpio:
            return False, "Debe seleccionar un producto para registrar la venta.", None

        producto = self.consultar_producto(codigo_limpio)
        if producto is None:
            return False, f"El producto con código '{codigo_limpio}' no existe en el catálogo.", None

        try:
            cantidad_int = int(cantidad)
            if cantidad_int <= 0:
                return False, "La cantidad a vender debe ser un número entero mayor a cero.", None
        except (ValueError, TypeError):
            return False, "La cantidad ingresada no es un número entero válido.", None

        if producto.stock < cantidad_int:
            return False, (
                f"Stock insuficiente para '{producto.nombre}'. "
                f"Disponibles: {producto.stock}, Solicitados: {cantidad_int}."
            ), None

        exito_descuento = producto.vender(cantidad_int)
        if not exito_descuento:
            return False, "No fue posible descontar las existencias del producto.", None

        id_venta = self._generar_siguiente_id_venta()
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = round(cantidad_int * producto.precio, 2)

        nueva_venta = Venta(
            id_venta=id_venta,
            username=usuario.username,
            codigo_producto=producto.codigo,
            nombre_producto=producto.nombre,
            cantidad=cantidad_int,
            precio_unitario=producto.precio,
            total=total,
            fecha_hora=fecha_hora
        )

        self.ventas.append(nueva_venta)

        exito_ventas = self._guardar_ventas()
        exito_productos = self._guardar_productos()

        if exito_ventas and exito_productos:
            mensaje = (
                f"Venta '{id_venta}' registrada con éxito: "
                f"{cantidad_int}x '{producto.nombre}' para '{usuario.username}' "
                f"(Total: ${total:.2f}). Stock restante: {producto.stock}."
            )
            return True, mensaje, nueva_venta
        else:
            return False, "Error al persistir la venta o actualizar el stock en disco.", None
