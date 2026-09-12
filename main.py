"""Punto de entrada de Tienda Gestión.

Ejecutar con:  python main.py
"""

from __future__ import annotations

import sys
import traceback

from app import db
from app.ui.ventana import Ventana


def main() -> int:
    try:
        conexion = db.conectar()
    except Exception as error:  # la base de datos es lo único sin lo que no se puede arrancar
        traceback.print_exc()
        print(
            "\nNo se pudo abrir la base de datos.\n"
            "Revise que la carpeta 'datos' se pueda escribir.\n"
            f"Detalle: {error}"
        )
        return 1

    Ventana(conexion).mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
