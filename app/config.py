"""Configuración central de Tienda Gestión.

Todo lo que pueda cambiar entre equipos o entre el computador de
desarrollo y el de la tienda vive aquí, para no dejar rutas ni
constantes repartidas por el código.
"""

from pathlib import Path

APP_NOMBRE = "Tienda Gestión"
APP_VERSION = "0.1.0"  # Sprint 1

# La base de datos queda junto al proyecto, en una carpeta "datos".
# Es un solo archivo: el tendero puede copiarlo a una USB.
CARPETA_DATOS = Path(__file__).resolve().parent.parent / "datos"
RUTA_BD = CARPETA_DATOS / "tienda.db"

# Métodos de pago con los que arranca la tienda.
METODOS_PAGO_INICIALES = ("Efectivo", "Nequi", "Daviplata", "Tarjeta")

# Límites de validación (reglas que salieron de la observación).
PRECIO_MAXIMO = 5_000_000
CANTIDAD_MAXIMA = 999

# Paleta y tipografía de la interfaz.
COLOR_FONDO = "#F4F4F0"
COLOR_TEXTO = "#1F2933"
COLOR_ACENTO = "#1E3A5F"
COLOR_ERROR = "#B42318"
COLOR_OK = "#1E7A46"
FUENTE = ("Segoe UI", 10)
FUENTE_TITULO = ("Segoe UI", 14, "bold")
FUENTE_TOTAL = ("Segoe UI", 22, "bold")
