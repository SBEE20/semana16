import json
from pathlib import Path
from typing import List, Dict, Any


class ArchivoServicio:
    """Servicio encargado de leer y persistir datos en archivos JSON con codificación UTF-8."""

    def __init__(self, ruta_datos: str = "datos"):
        """
        Inicializa el servicio de archivos.

        Args:
            ruta_datos: Ruta de la carpeta donde se encuentran los archivos JSON
        """
        self.ruta_datos = Path(ruta_datos)

    def cargar_json(self, nombre_archivo: str) -> List[Dict[str, Any]]:
        """
        Carga un archivo JSON y retorna su contenido como lista de diccionarios.

        Args:
            nombre_archivo: Nombre del archivo JSON (ej: 'usuarios.json', 'ventas.json')

        Returns:
            Lista de diccionarios con los datos del archivo
        """
        ruta_archivo = self.ruta_datos / nombre_archivo

        try:
            if ruta_archivo.exists():
                with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                    datos = json.load(archivo)
                    return datos if isinstance(datos, list) else []
            else:
                print(f"Advertencia: archivo {nombre_archivo} no encontrado en {self.ruta_datos}")
                return []
        except json.JSONDecodeError:
            print(f"Error: {nombre_archivo} no es un JSON válido")
            return []
        except Exception as e:
            print(f"Error al leer {nombre_archivo}: {e}")
            return []

    def guardar_json(self, nombre_archivo: str, datos: List[Dict[str, Any]]) -> bool:
        """
        Guarda datos en un archivo JSON de forma segura.

        Args:
            nombre_archivo: Nombre del archivo JSON
            datos: Lista de diccionarios a guardar

        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        ruta_archivo = self.ruta_datos / nombre_archivo

        try:
            self.ruta_datos.mkdir(parents=True, exist_ok=True)
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar {nombre_archivo}: {e}")
            return False
