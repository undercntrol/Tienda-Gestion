"""Ventana principal: arma las tres pestañas del Sprint 1."""

from __future__ import annotations

import tkinter as tk
import traceback
from tkinter import messagebox, ttk

from .. import config
from ..servicios import ServicioCatalogo, ServicioVentas
from .vista_catalogo import VistaCatalogo
from .vista_dia import VistaDia
from .vista_venta import VistaVenta


class Ventana(tk.Tk):
    def __init__(self, conexion):
        super().__init__()
        self.conexion = conexion
        self.title(f"{config.APP_NOMBRE} — v{config.APP_VERSION}")
        self.geometry("1020x620")
        self.minsize(900, 560)
        self.configure(bg=config.COLOR_FONDO)

        self._estilos()

        catalogo = ServicioCatalogo(conexion)
        ventas = ServicioVentas(conexion)

        self.pestanas = ttk.Notebook(self)
        self.pestanas.pack(fill="both", expand=True, padx=10, pady=10)

        self.vista_dia = VistaDia(self.pestanas, ventas)
        self.vista_venta = VistaVenta(
            self.pestanas, ventas, catalogo, al_registrar=self.vista_dia.recargar
        )
        self.vista_catalogo = VistaCatalogo(
            self.pestanas, catalogo, al_cambiar=self.vista_venta.recargar_productos
        )

        self.pestanas.add(self.vista_venta, text="  Venta  ")
        self.pestanas.add(self.vista_catalogo, text="  Catálogo  ")
        self.pestanas.add(self.vista_dia, text="  Cierre del día  ")

        self.barra = ttk.Label(
            self,
            text=f"Datos guardados en {config.RUTA_BD}",
            foreground="#6B7280",
            padding=(12, 4),
        )
        self.barra.pack(fill="x", side="bottom")

        # Cualquier error no previsto se muestra en lugar de cerrar la
        # ventana en blanco: condición 5 del enunciado.
        self.report_callback_exception = self._error_inesperado
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    def _estilos(self) -> None:
        estilo = ttk.Style(self)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure(".", font=config.FUENTE, background=config.COLOR_FONDO)
        estilo.configure("TFrame", background=config.COLOR_FONDO)
        estilo.configure("TLabelframe", background=config.COLOR_FONDO)
        estilo.configure("TLabelframe.Label", foreground=config.COLOR_ACENTO)
        estilo.configure("TNotebook.Tab", padding=(14, 8))
        estilo.configure(
            "Treeview.Heading", background=config.COLOR_ACENTO, foreground="white"
        )
        estilo.configure("Treeview", rowheight=26, fieldbackground="white")

    def _error_inesperado(self, tipo, valor, rastro) -> None:
        traceback.print_exception(tipo, valor, rastro)
        messagebox.showerror(
            "Ocurrió un problema",
            "La acción no se pudo completar y la información no se guardó.\n\n"
            f"Detalle técnico: {valor}\n\n"
            "Puede seguir trabajando. Si vuelve a pasar, avísele al equipo.",
        )

    def _cerrar(self) -> None:
        try:
            self.conexion.close()
        finally:
            self.destroy()
