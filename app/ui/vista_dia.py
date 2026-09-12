"""HU-03 — Ver las ventas del día con el total por método de pago."""

from __future__ import annotations

import tkinter as tk
from datetime import date
from tkinter import ttk

from .. import config
from ..servicios import ServicioVentas
from .formato import dia_largo, hora, pesos


class VistaDia(ttk.Frame):
    def __init__(self, padre: tk.Misc, ventas: ServicioVentas):
        super().__init__(padre, padding=16)
        self.ventas = ventas
        self._construir()
        self.recargar()

    def _construir(self) -> None:
        encabezado = ttk.Frame(self)
        encabezado.grid(row=0, column=0, sticky="we", pady=(0, 12))
        ttk.Label(encabezado, text="Cierre del día", font=config.FUENTE_TITULO).grid(
            row=0, column=0, sticky="w"
        )
        self.etiqueta_fecha = ttk.Label(encabezado, text="", foreground="#6B7280")
        self.etiqueta_fecha.grid(row=1, column=0, sticky="w")
        ttk.Button(encabezado, text="Actualizar", command=self.recargar).grid(
            row=0, column=1, rowspan=2, padx=12
        )

        tarjetas = ttk.Frame(self)
        tarjetas.grid(row=1, column=0, sticky="we", pady=(0, 12))
        self.etiqueta_total = self._tarjeta(tarjetas, 0, "Total vendido", config.FUENTE_TOTAL)
        self.etiqueta_ventas = self._tarjeta(tarjetas, 1, "Ventas registradas")
        self.etiqueta_unidades = self._tarjeta(tarjetas, 2, "Unidades vendidas")

        cuerpo = ttk.Frame(self)
        cuerpo.grid(row=2, column=0, sticky="nsew")
        cuerpo.columnconfigure(0, weight=3)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)

        self.tabla = ttk.Treeview(
            cuerpo,
            columns=("hora", "producto", "cant", "metodo", "monto"),
            show="headings",
            height=13,
        )
        for col, titulo, ancho, anclaje in (
            ("hora", "Hora", 90, "w"),
            ("producto", "Producto", 220, "w"),
            ("cant", "Cant.", 55, "center"),
            ("metodo", "Método", 110, "w"),
            ("monto", "Monto", 110, "e"),
        ):
            self.tabla.heading(col, text=titulo)
            self.tabla.column(col, width=ancho, anchor=anclaje)
        self.tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        caja = ttk.LabelFrame(cuerpo, text="Por método de pago", padding=12)
        caja.grid(row=0, column=1, sticky="nsew")
        self.tabla_metodos = ttk.Treeview(
            caja, columns=("metodo", "total"), show="headings", height=8
        )
        self.tabla_metodos.heading("metodo", text="Método")
        self.tabla_metodos.heading("total", text="Total")
        self.tabla_metodos.column("metodo", width=110)
        self.tabla_metodos.column("total", width=100, anchor="e")
        self.tabla_metodos.grid(row=0, column=0, sticky="nsew")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

    def _tarjeta(self, padre: tk.Misc, columna: int, titulo: str, fuente=None):
        marco = ttk.LabelFrame(padre, text=titulo, padding=10)
        marco.grid(row=0, column=columna, sticky="we", padx=(0, 12))
        etiqueta = ttk.Label(marco, text="—", font=fuente or config.FUENTE_TITULO)
        etiqueta.grid(row=0, column=0, sticky="w")
        padre.columnconfigure(columna, weight=1)
        return etiqueta

    def recargar(self) -> None:
        hoy = date.today().isoformat()
        resumen = self.ventas.resumen_del_dia(hoy)
        self.etiqueta_fecha.configure(text=dia_largo(hoy))
        self.etiqueta_total.configure(text=pesos(resumen.total))
        self.etiqueta_ventas.configure(text=str(resumen.ventas))
        self.etiqueta_unidades.configure(text=str(resumen.unidades))

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for venta in self.ventas.ventas_del_dia(hoy):
            self.tabla.insert(
                "",
                "end",
                values=(
                    hora(venta.fecha),
                    venta.producto,
                    venta.cantidad,
                    venta.metodo,
                    pesos(venta.monto),
                ),
            )

        for fila in self.tabla_metodos.get_children():
            self.tabla_metodos.delete(fila)
        for metodo, total in resumen.por_metodo.items():
            self.tabla_metodos.insert("", "end", values=(metodo, pesos(total)))
