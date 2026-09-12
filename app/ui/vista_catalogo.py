"""HU-01 — Catálogo: registrar, editar y buscar productos."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .. import config
from ..errores import ErrorDeNegocio
from ..servicios import ServicioCatalogo
from .formato import pesos


class VistaCatalogo(ttk.Frame):
    def __init__(self, padre: tk.Misc, servicio: ServicioCatalogo, al_cambiar=None):
        super().__init__(padre, padding=16)
        self.servicio = servicio
        self.al_cambiar = al_cambiar  # avisa a la vista de ventas que recargue
        self.seleccion_id: int | None = None

        self._construir()
        self.recargar()

    # ---------------- construcción de la interfaz ----------------
    def _construir(self) -> None:
        ttk.Label(self, text="Catálogo de productos", font=config.FUENTE_TITULO).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        formulario = ttk.LabelFrame(self, text="Producto", padding=12)
        formulario.grid(row=1, column=0, sticky="nw", padx=(0, 16))

        ttk.Label(formulario, text="Nombre").grid(row=0, column=0, sticky="w")
        self.entrada_nombre = ttk.Entry(formulario, width=28)
        self.entrada_nombre.grid(row=1, column=0, pady=(2, 10))

        ttk.Label(formulario, text="Precio").grid(row=2, column=0, sticky="w")
        self.entrada_precio = ttk.Entry(formulario, width=28)
        self.entrada_precio.grid(row=3, column=0, pady=(2, 4))
        ttk.Label(
            formulario,
            text="Puede escribir 2.500 o 2500",
            foreground="#6B7280",
        ).grid(row=4, column=0, sticky="w", pady=(0, 12))

        botones = ttk.Frame(formulario)
        botones.grid(row=5, column=0, sticky="we")
        self.boton_guardar = ttk.Button(botones, text="Guardar", command=self.guardar)
        self.boton_guardar.grid(row=0, column=0)
        ttk.Button(botones, text="Limpiar", command=self.limpiar).grid(
            row=0, column=1, padx=6
        )
        self.boton_quitar = ttk.Button(
            botones, text="Quitar", command=self.quitar, state="disabled"
        )
        self.boton_quitar.grid(row=0, column=2)

        self.mensaje = ttk.Label(formulario, text="", wraplength=220)
        self.mensaje.grid(row=6, column=0, sticky="w", pady=(12, 0))

        # ---- lista ----
        derecha = ttk.Frame(self)
        derecha.grid(row=1, column=1, sticky="nsew")
        derecha.rowconfigure(1, weight=1)
        derecha.columnconfigure(0, weight=1)

        buscador = ttk.Frame(derecha)
        buscador.grid(row=0, column=0, sticky="we", pady=(0, 8))
        ttk.Label(buscador, text="Buscar").grid(row=0, column=0, padx=(0, 6))
        self.entrada_buscar = ttk.Entry(buscador, width=30)
        self.entrada_buscar.grid(row=0, column=1)
        self.entrada_buscar.bind("<KeyRelease>", lambda _e: self.recargar())

        self.tabla = ttk.Treeview(
            derecha, columns=("nombre", "precio"), show="headings", height=14
        )
        self.tabla.heading("nombre", text="Producto")
        self.tabla.heading("precio", text="Precio")
        self.tabla.column("nombre", width=280)
        self.tabla.column("precio", width=110, anchor="e")
        self.tabla.grid(row=1, column=0, sticky="nsew")
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

        barra = ttk.Scrollbar(derecha, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        barra.grid(row=1, column=1, sticky="ns")

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

    # ---------------- acciones ----------------
    def recargar(self) -> None:
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for producto in self.servicio.listar(self.entrada_buscar.get()):
            self.tabla.insert(
                "",
                "end",
                iid=str(producto.id),
                values=(producto.nombre, pesos(producto.precio)),
            )

    def limpiar(self) -> None:
        self.seleccion_id = None
        self.entrada_nombre.delete(0, "end")
        self.entrada_precio.delete(0, "end")
        self.boton_guardar.configure(text="Guardar")
        self.boton_quitar.configure(state="disabled")
        self.tabla.selection_remove(self.tabla.selection())
        self._avisar("")

    def guardar(self) -> None:
        nombre = self.entrada_nombre.get()
        precio = self.entrada_precio.get()
        try:
            if self.seleccion_id is None:
                producto = self.servicio.crear(nombre, precio)
                texto = f"Producto “{producto.nombre}” guardado."
            else:
                producto = self.servicio.editar(self.seleccion_id, nombre, precio)
                texto = f"Producto “{producto.nombre}” actualizado."
        except ErrorDeNegocio as error:
            # Condición 5 del enunciado: el usuario se entera de forma útil.
            self._avisar(str(error), error=True)
            return
        self.limpiar()
        self.recargar()
        self._avisar(texto, error=False)
        if self.al_cambiar:
            self.al_cambiar()

    def quitar(self) -> None:
        if self.seleccion_id is None:
            return
        nombre = self.entrada_nombre.get()
        if not messagebox.askyesno(
            "Quitar producto",
            f"¿Quitar “{nombre}” del catálogo?\n\n"
            "Las ventas ya registradas no se borran.",
        ):
            return
        try:
            self.servicio.desactivar(self.seleccion_id)
        except ErrorDeNegocio as error:
            self._avisar(str(error), error=True)
            return
        self.limpiar()
        self.recargar()
        self._avisar("Producto quitado del catálogo.", error=False)
        if self.al_cambiar:
            self.al_cambiar()

    # ---------------- apoyo ----------------
    def _al_seleccionar(self, _evento) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        self.seleccion_id = int(seleccion[0])
        producto = self.servicio.productos.obtener(self.seleccion_id)
        if producto is None:
            self.limpiar()
            self.recargar()
            return
        self.entrada_nombre.delete(0, "end")
        self.entrada_nombre.insert(0, producto.nombre)
        self.entrada_precio.delete(0, "end")
        self.entrada_precio.insert(0, f"{producto.precio:.0f}")
        self.boton_guardar.configure(text="Actualizar")
        self.boton_quitar.configure(state="normal")

    def _avisar(self, texto: str, error: bool = False) -> None:
        color = config.COLOR_ERROR if error else config.COLOR_OK
        self.mensaje.configure(text=texto, foreground=color)
