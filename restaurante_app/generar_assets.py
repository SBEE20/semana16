"""
Generador de assets visuales (logotipo e íconos en formato PNG con canal alfa)
para la aplicación del restaurante (Semana 15).
No requiere dependencias externas como Pillow, utilizando compresión zlib estándar.
"""
import zlib
import struct
from pathlib import Path

def guardar_png(ancho: int, alto: int, pixeles: list, ruta_salida: Path) -> None:
    """Guarda una matriz de píxeles RGBA en un archivo PNG válido."""
    raw = bytearray()
    for fila in pixeles:
        raw.append(0)  # Filtro None
        for r, g, b, a in fila:
            raw.extend([int(r), int(g), int(b), int(a)])

    comprimido = zlib.compress(bytes(raw), 9)

    def chunk(tipo: bytes, data: bytes) -> bytes:
        c = bytearray(tipo) + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return struct.pack('>I', len(data)) + c + crc

    png = bytearray(b'\x89PNG\r\n\x1a\n')
    ihdr = struct.pack('>IIBBBBB', ancho, alto, 8, 6, 0, 0, 0)
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', comprimido)
    png += chunk(b'IEND', b'')

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_salida, 'wb') as f:
        f.write(png)


def crear_logo(tamano: int = 56) -> list:
    """Genera un logotipo circular moderno con un sombrero de chef y cubiertos."""
    pixeles = [[(0, 0, 0, 0) for _ in range(tamano)] for _ in range(tamano)]
    cx, cy = tamano / 2.0, tamano / 2.0
    r_circulo = tamano / 2.0 - 2.0

    for y in range(tamano):
        for x in range(tamano):
            dx = x - cx
            dy = y - cy
            dist = (dx * dx + dy * dy) ** 0.5
            if dist <= r_circulo:
                # Fondo circular en degradado elegante azul marino / petróleo
                factor = (y / tamano)
                r = int(15 * (1 - factor) + 30 * factor)
                g = int(23 * (1 - factor) + 41 * factor)
                b = int(42 * (1 - factor) + 59 * factor)
                # Borde dorado suave
                if dist >= r_circulo - 2:
                    pixeles[y][x] = (245, 158, 11, 255)  # Dorado / Amber
                else:
                    pixeles[y][x] = (r, g, b, 255)

    # Dibujar gorro de chef estilizado en blanco / marfil
    # Base del gorro (rectángulo en la parte inferior)
    base_y1, base_y2 = int(cy + 4), int(cy + 10)
    base_x1, base_x2 = int(cx - 13), int(cx + 13)
    for y in range(base_y1, base_y2):
        for x in range(base_x1, base_x2):
            pixeles[y][x] = (255, 255, 255, 255)

    # Pliegues del gorro (3 cúpulas)
    cupulas = [
        (cx - 8, cy, 7.5),
        (cx, cy - 4, 8.5),
        (cx + 8, cy, 7.5)
    ]
    for ccx, ccy, cr in cupulas:
        for y in range(int(ccy - cr), int(ccy + cr + 1)):
            for x in range(int(ccx - cr), int(ccx + cr + 1)):
                if 0 <= y < tamano and 0 <= x < tamano:
                    if (x - ccx)**2 + (y - ccy)**2 <= cr**2:
                        pixeles[y][x] = (255, 255, 255, 255)

    # Detalle dorado en la banda del gorro
    banda_y = int(cy + 6)
    for x in range(base_x1 + 2, base_x2 - 2):
        pixeles[banda_y][x] = (245, 158, 11, 255)

    # Plato / campana base decorativa
    for x in range(int(cx - 16), int(cx + 17)):
        y = int(cy + 13)
        if 0 <= y < tamano:
            pixeles[y][x] = (245, 158, 11, 255)

    return pixeles


def crear_icono_productos(tamano: int = 20) -> list:
    """Genera un ícono de caja / paquete de productos (20x20)."""
    pixeles = [[(0, 0, 0, 0) for _ in range(tamano)] for _ in range(tamano)]
    # Caja isométrica estilizada en tonos cian / azul
    for y in range(3, 17):
        for x in range(3, 17):
            # Límites de la caja
            if y == 3 or y == 16 or x == 3 or x == 16:
                pixeles[y][x] = (255, 255, 255, 255)
            elif y in (9, 10) or x in (9, 10):
                pixeles[y][x] = (186, 230, 253, 230)  # Cinta de paquete
            else:
                pixeles[y][x] = (2, 132, 199, 240)    # Relleno azul
    return pixeles


def crear_icono_ventas(tamano: int = 20) -> list:
    """Genera un ícono de carrito de compras / bolsa de venta (20x20)."""
    pixeles = [[(0, 0, 0, 0) for _ in range(tamano)] for _ in range(tamano)]
    # Bolsa de compras con asa
    # Asa
    for x in range(7, 13):
        pixeles[3][x] = (255, 255, 255, 255)
    pixeles[4][7] = (255, 255, 255, 255)
    pixeles[4][12] = (255, 255, 255, 255)
    pixeles[5][7] = (255, 255, 255, 255)
    pixeles[5][12] = (255, 255, 255, 255)

    # Cuerpo de la bolsa (verde esmeralda)
    for y in range(6, 17):
        for x in range(4, 16):
            if y == 6 or y == 16 or x == 4 or x == 15:
                pixeles[y][x] = (255, 255, 255, 255)
            else:
                pixeles[y][x] = (22, 163, 74, 245)

    # Símbolo '$' en el centro
    pixeles[9][9] = (255, 255, 255, 255)
    pixeles[9][10] = (255, 255, 255, 255)
    pixeles[10][9] = (255, 255, 255, 255)
    pixeles[11][10] = (255, 255, 255, 255)
    pixeles[12][9] = (255, 255, 255, 255)
    pixeles[12][10] = (255, 255, 255, 255)
    pixeles[8][10] = (255, 255, 255, 255)
    pixeles[13][9] = (255, 255, 255, 255)

    return pixeles


def crear_icono_usuarios(tamano: int = 20) -> list:
    """Genera un ícono de usuario / perfil (20x20)."""
    pixeles = [[(0, 0, 0, 0) for _ in range(tamano)] for _ in range(tamano)]
    # Cabeza (círculo)
    cx, cy, r = 9.5, 6.0, 3.5
    for y in range(2, 11):
        for x in range(5, 15):
            if (x - cx)**2 + (y - cy)**2 <= r**2:
                pixeles[y][x] = (255, 255, 255, 255)

    # Hombros / torso
    for y in range(11, 18):
        for x in range(2, 18):
            dx = abs(x - cx)
            dy = y - 11
            if dx <= 2 + dy * 0.9 and y <= 16:
                pixeles[y][x] = (255, 255, 255, 255)

    return pixeles


def crear_icono_logout(tamano: int = 20) -> list:
    """Genera un ícono de salida / puerta (20x20)."""
    pixeles = [[(0, 0, 0, 0) for _ in range(tamano)] for _ in range(tamano)]
    # Marco de puerta
    for y in range(3, 17):
        pixeles[y][4] = (255, 255, 255, 255)
        pixeles[y][5] = (255, 255, 255, 255)
    for x in range(4, 12):
        pixeles[3][x] = (255, 255, 255, 255)
        pixeles[16][x] = (255, 255, 255, 255)

    # Flecha saliente
    for x in range(8, 16):
        pixeles[10][x] = (255, 255, 255, 255)
    # Punta flecha
    pixeles[8][13] = (255, 255, 255, 255)
    pixeles[9][14] = (255, 255, 255, 255)
    pixeles[11][14] = (255, 255, 255, 255)
    pixeles[12][13] = (255, 255, 255, 255)

    return pixeles


def main():
    carpeta_assets = Path(__file__).resolve().parent / "assets"
    carpeta_assets.mkdir(parents=True, exist_ok=True)

    guardar_png(56, 56, crear_logo(56), carpeta_assets / "logo.png")
    guardar_png(20, 20, crear_icono_productos(20), carpeta_assets / "icon_productos.png")
    guardar_png(20, 20, crear_icono_ventas(20), carpeta_assets / "icon_ventas.png")
    guardar_png(20, 20, crear_icono_usuarios(20), carpeta_assets / "icon_usuarios.png")
    guardar_png(20, 20, crear_icono_logout(20), carpeta_assets / "icon_logout.png")

    print(f"Assets generados exitosamente en: {carpeta_assets}")


if __name__ == "__main__":
    main()
