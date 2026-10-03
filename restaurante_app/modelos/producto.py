class Producto:
    """Clase que representa un producto disponible en el restaurante."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        precio: float,
        categoria: str,
        stock: int = 0
    ):
        codigo = str(codigo).strip()
        nombre = str(nombre).strip()
        categoria = str(categoria).strip()

        if not codigo or not nombre:
            raise ValueError("El código y nombre son obligatorios")
        if precio < 0:
            raise ValueError("El precio no puede ser negativo")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo")

        self.codigo = codigo
        self.nombre = nombre
        self.precio = float(precio)
        self.categoria = categoria
        self.stock = int(stock)

    def actualizar(self, nombre: str, precio: float, categoria: str, stock: int) -> None:
        """Actualiza los datos del producto."""
        nombre = str(nombre).strip()
        categoria = str(categoria).strip()

        if not nombre:
            raise ValueError("El nombre del producto no puede estar vacío")
        if precio < 0:
            raise ValueError("El precio no puede ser negativo")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo")

        self.nombre = nombre
        self.precio = float(precio)
        self.categoria = categoria
        self.stock = int(stock)

    def vender(self, cantidad: int) -> bool:
        """Reduce el stock si hay cantidad suficiente."""
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero")
        if cantidad > self.stock:
            return False
        self.stock -= cantidad
        return True

    def convertir_a_diccionario(self) -> dict:
        """Convierte el producto a un diccionario para serialización JSON."""
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "precio": round(self.precio, 2),
            "categoria": self.categoria,
            "stock": self.stock
        }

    @staticmethod
    def desde_diccionario(datos: dict) -> "Producto":
        """Reconstruye un Producto desde un diccionario."""
        return Producto(
            codigo=datos.get("codigo", ""),
            nombre=datos.get("nombre", ""),
            precio=float(datos.get("precio", 0.0)),
            categoria=datos.get("categoria", "General"),
            stock=int(datos.get("stock", 0))
        )

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.nombre} ({self.categoria}) - ${self.precio:.2f} (Stock: {self.stock})"
