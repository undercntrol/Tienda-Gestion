"""HU-02 — Registrar una venta: producto, cantidad y método de pago."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .. import config
from ..errores import ErrorDeNegocio
from ..servicios import ServicioCatalogo, ServicioVentas, limpiar_precio
from .formato import hora, pesos


class VistaVenta(ttk.Frame):
    def __init__(
        self,
        padre: tk.Misc,
        ventas: ServicioVentas,
        catalogo: ServicioCatalogo,
        al_registrar=None,
    ):
        super().__init__(padre, padding=16)
        self.ventas = ventas
        self.catalogo = catalogo
        self.al_registrar = al_registrar
        self.productos: list = []
        self.ultima_venta_id: int | None = None

        self._construir()
        self.recargar_productos()

    # ---------------- construcción ----------------
    def _construir(self) -> None:
        ttk.Label(self, text="Registrar venta", font=config.FUENTE_TITULO).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        caja = ttk.LabelFrame(self, text="Venta", padding=12)
        caja.grid(row=1, column=0, sticky="nw", padx=(0, 16))

        ttk.Label(caja, text="Producto").grid(row=0, column=0, sticky="w")
        self.combo_producto = ttk.Combobox(caja, width=30, state="readonly")
        self.combo_producto.grid(row=1, column=0, columnspan=2, pady=(2, 10))
        self.combo_producto.bind("<<ComboboxSelected>>", self._al_elegir_producto)

        ttk.Label(caja, text="Cantidad").grid(row=2, column=0, sticky="w")
        self.entrada_cantidad = ttk.Entry(caja, width=12)
        self.entrada_cantidad.insert(0, "1")
        self.entrada_cantidad.grid(row=3, column=0, sticky="w", pady=(2, 10))
        self.entrada_cantidad.bind("<KeyRelease>", lambda _e: self._calcular_total())

        ttk.Label(caja, text="Precio unitario").grid(row=2, column=1, sticky="w")
        self.entrada_precio = ttk.Entry(caja, width=16)
        self.entrada_precio.grid(row=3, column=1, sticky="w", pady=(2, 10))
        self.entrada_precio.bind("<KeyRelease>", lambda _e: self._calcular_total())

        ttk.Label(
            caja,
            text="El precio viene del catálogo y se puede cambiar\n"
            "para esta venta (menudeo o paquete).",
            foreground="#6B7280",
            justify="left",
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Label(caja, text="Método de pago").grid(row=5, column=0, sticky="w")
        self.combo_metodo = ttk.Combobox(caja, width=20, state="readonly")
        self.combo_metodo.grid(row=6, column=0, columnspan=2, sticky="w", pady=(2, 12))

        ttk.Label(caja, text="Total de la venta").grid(row=7, column=0, sticky="w")
        self.etiqueta_total = ttk.Label(caja, text=pesos(0), font=config.FUENTE_TOTAL)
        self.etiqueta_total.grid(row=8, column=0, columnspan=2, sticky="w", pady=(0, 12))

        botones = ttk.Frame(caja)
        botones.grid(row=9, column=0, columnspan=2, sticky="we")
        ttk.Button(botones, text="Registrar venta", command=self.registrar).grid(
            row=0, column=0
        )
        self.boton_anular = ttk.Button(
            botones, text="Anular la última", command=self.anular_ultima, state="disabled"
        )
        self.boton_anular.grid(row=0, column=1, padx=6)

        self.mensaje = ttk.Label(caja, text="", wraplength=260)
        self.mensaje.grid(row=10, column=0, columnspan=2, sticky="w", pady=(12, 0))

        # ---- últimas ventas, para confirmar que quedó guardada ----
        derecha = ttk.Frame(self)
        derecha.grid(row=1, column=1, sticky="nsew")
        derecha.rowconfigure(1, weight=1)
        derecha.columnconfigure(0, weight=1)

        ttk.Label(derecha, text="Últimas ventas de hoy").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        self.tabla = ttk.Treeview(
            derecha,
            columns=("hora", "producto", "cant", "metodo", "monto"),
            show="headings",
            height=14,
        )
        for col, titulo, ancho, anclaje in (
            ("hora", "Hora", 90, "w"),
            ("producto", "Producto", 200, "w"),
            ("cant", "Cant.", 55, "center"),
            ("metodo", "Método", 100, "w"),
            ("monto", "Monto", 100, "e"),
        ):
            self.tabla.heading(col, text=titulo)
            self.tabla.column(col, width=ancho, anchor=anclaje)
        self.tabla.grid(row=1, column=0, sticky="nsew")

        barra = ttk.Scrollbar(derecha, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        barra.grid(row=1, column=1, sticky="ns")

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

    # ---------------- acciones ----------------
    def recargar_productos(self) -> None:
        self.productos = self.catalogo.listar()
        self.combo_producto["values"] = [p.nombre for p in self.productos]
        metodos = [m.nombre for m in self.ventas.metodos_pago()]
        self.combo_metodo["values"] = metodos
        if metodos and not self.combo_metodo.get():
            self.combo_metodo.current(0)
        if not self.productos:
            self._avisar(
                "El catálogo está vacío. Registre primero un producto "
                "en la pestaña Catálogo.",
                error=True,
            )
        self.recargar_ventas()

    def recargar_ventas(self) -> None:
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for venta in self.ventas.ventas_del_dia():
            self.tabla.insert(
                "",
                "end",
                iid=str(venta.id),
                values=(
                    hora(venta.fecha),
                    venta.producto,
                    venta.cantidad,
                    venta.metodo,
                    pesos(venta.monto),
                ),
            )

    def registrar(self) -> None:
        producto = self._producto_elegido()
        try:
            venta = self.ventas.registrar(
                producto_id=producto.id if producto else None,
                cantidad=self.entrada_cantidad.get(),
                metodo_nombre=self.combo_metodo.get(),
                precio_unitario=self.entrada_precio.get(),
            )
        except ErrorDeNegocio as error:
            self._avisar(str(error), error=True)
            return

        self.ultima_venta_id = venta.id
        self.boton_anular.configure(state="normal")
        self._avisar(
            f"Venta registrada: {venta.cantidad} × {venta.producto} "
            f"por {pesos(venta.monto)} en {venta.metodo}.",
            error=False,
        )
        self.entrada_cantidad.delete(0, "end")
        self.entrada_cantidad.insert(0, "1")
        self._calcular_total()
        self.recargar_ventas()
        if self.al_registrar:
            self.al_registrar()

    def anular_ultima(self) -> None:
        if self.ultima_venta_id is None:
            return
        self.ventas.anular(self.ultima_venta_id)
        self.ultima_venta_id = None
        self.boton_anular.configure(state="disabled")
        self._avisar("Se anuló la última venta registrada.", error=False)
        self.recargar_ventas()
        if self.al_registrar:
            self.al_registrar()

    # ---------------- apoyo ----------------
    def _producto_elegido(self):
        indice = self.combo_producto.current()
        if indice < 0 or indice >= len(self.productos):
            return None
        return self.productos[indice]

    def _al_elegir_producto(self, _evento) -> None:
        producto = self._producto_elegido()
        if producto is None:
            return
        self.entrada_precio.delete(0, "end")
        self.entrada_precio.insert(0, f"{producto.precio:.0f}")
        self._calcular_total()
        self._avisar("")

    def _calcular_total(self) -> None:
        """Total en vivo. Si lo escrito no sirve, se muestra en cero."""
        try:
            cantidad = int(self.entrada_cantidad.get().strip() or 0)
            precio = limpiar_precio(self.entrada_precio.get())
            self.etiqueta_total.configure(text=pesos(precio * cantidad))
        except (ValueError, ErrorDeNegocio):
            self.etiqueta_total.configure(text=pesos(0))

    def _avisar(self, texto: str, error: bool = False) -> None:
        color = config.COLOR_ERROR if error else config.COLOR_OK
        self.mensaje.configure(text=texto, foreground=color)
