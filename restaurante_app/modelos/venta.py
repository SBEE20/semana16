class Venta:
    """
    Representa una operación de venta realizada en el restaurante.
    Relaciona un usuario con un producto, la cantidad vendida, el precio
    unitario, el total calculado y la fecha y hora de la transacción.
    """

    def __init__(
        self,
        id_venta: str,
        username: str,
        codigo_producto: str,
        nombre_producto: str,
        cantidad: int,
        precio_unitario: float,
        total: float,
        fecha_hora: str
    ):
        id_venta = str(id_venta).strip()
        username = str(username).strip()
        codigo_producto = str(codigo_producto).strip()
        nombre_producto = str(nombre_producto).strip()
        fecha_hora = str(fecha_hora).strip()

        if not id_venta:
            raise ValueError("El identificador de venta (id_venta) es obligatorio.")
        if not username:
            raise ValueError("El nombre de usuario es obligatorio para la venta.")
        if not codigo_producto:
            raise ValueError("El código del producto es obligatorio.")
        if int(cantidad) <= 0:
            raise ValueError("La cantidad vendida debe ser mayor a cero.")
        if float(precio_unitario) < 0:
            raise ValueError("El precio unitario no puede ser negativo.")
        if float(total) < 0:
            raise ValueError("El total de la venta no puede ser negativo.")

        self.id_venta = id_venta
        self.username = username
        self.codigo_producto = codigo_producto
        self.nombre_producto = nombre_producto
        self.cantidad = int(cantidad)
        self.precio_unitario = float(precio_unitario)
        self.total = float(total)
        self.fecha_hora = fecha_hora

    def convertir_a_diccionario(self) -> dict:
        """Convierte la venta a un diccionario serializable en formato JSON."""
        return {
            "id_venta": self.id_venta,
            "username": self.username,
            "codigo_producto": self.codigo_producto,
            "nombre_producto": self.nombre_producto,
            "cantidad": self.cantidad,
            "precio_unitario": round(self.precio_unitario, 2),
            "total": round(self.total, 2),
            "fecha_hora": self.fecha_hora
        }

    @staticmethod
    def desde_diccionario(datos: dict) -> "Venta":
        """Reconstruye una instancia de Venta a partir de un diccionario."""
        return Venta(
            id_venta=datos.get("id_venta", ""),
            username=datos.get("username", ""),
            codigo_producto=datos.get("codigo_producto", ""),
            nombre_producto=datos.get("nombre_producto", ""),
            cantidad=int(datos.get("cantidad", 1)),
            precio_unitario=float(datos.get("precio_unitario", 0.0)),
            total=float(datos.get("total", 0.0)),
            fecha_hora=datos.get("fecha_hora", "")
        )

    def __str__(self) -> str:
        return (
            f"Venta [{self.id_venta}] {self.fecha_hora} | "
            f"Usuario: {self.username} | {self.nombre_producto} "
            f"x{self.cantidad} = ${self.total:.2f}"
        )
