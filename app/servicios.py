"""Reglas de negocio y validaciones.

La interfaz nunca valida por su cuenta: llama a estos servicios y
muestra el mensaje del error que reciba. Así las mismas reglas aplican
desde la ventana, desde una prueba o desde cualquier pantalla que se
agregue en los sprints siguientes.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime

from . import config
from .errores import DatoInvalido, NoEncontrado, ProductoDuplicado
from .modelos import MetodoPago, Producto, ResumenDia, Venta
from .repositorios import (
    RepositorioMetodosPago,
    RepositorioProductos,
    RepositorioVentas,
)


def limpiar_precio(texto: str) -> float:
    """Convierte lo que el usuario escribió en un número.

    El tendero escribe "2.500", "2500", "$ 2.500" o "2,500" para el mismo
    valor. Aceptarlo todo evita que tenga que aprender un formato nuevo.
    """
    bruto = str(texto).strip().replace("$", "").replace(" ", "")
    if not bruto:
        raise DatoInvalido("Escriba el precio del producto.")
    bruto = bruto.replace(".", "").replace(",", ".")
    try:
        valor = float(bruto)
    except ValueError:
        raise DatoInvalido(
            f"“{texto}” no es un precio válido. Escriba solo números, por ejemplo 2500."
        ) from None
    if valor <= 0:
        raise DatoInvalido("El precio debe ser mayor que cero.")
    if valor > config.PRECIO_MAXIMO:
        raise DatoInvalido(
            f"El precio no puede pasar de {config.PRECIO_MAXIMO:,.0f}. "
            "Revise si sobra un cero."
        )
    return round(valor, 2)


def limpiar_cantidad(texto: str) -> int:
    bruto = str(texto).strip()
    if not bruto:
        raise DatoInvalido("Escriba la cantidad.")
    if not bruto.isdigit():
        raise DatoInvalido(
            f"“{texto}” no es una cantidad válida. Escriba un número entero."
        )
    cantidad = int(bruto)
    if cantidad <= 0:
        raise DatoInvalido("La cantidad debe ser al menos 1.")
    if cantidad > config.CANTIDAD_MAXIMA:
        raise DatoInvalido(
            f"La cantidad no puede pasar de {config.CANTIDAD_MAXIMA} unidades."
        )
    return cantidad


def limpiar_nombre(texto: str) -> str:
    nombre = " ".join(str(texto).split())
    if not nombre:
        raise DatoInvalido("Escriba el nombre del producto.")
    if len(nombre) < 2:
        raise DatoInvalido("El nombre es demasiado corto.")
    if len(nombre) > 60:
        raise DatoInvalido("El nombre no puede pasar de 60 caracteres.")
    return nombre


class ServicioCatalogo:
    """HU-01 — Registrar y consultar productos con su precio."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.productos = RepositorioProductos(conn)

    def crear(self, nombre: str, precio: str | float) -> Producto:
        nombre = limpiar_nombre(nombre)
        valor = limpiar_precio(precio)
        if self.productos.buscar_por_nombre(nombre):
            raise ProductoDuplicado(
                f"Ya existe un producto llamado “{nombre}”. "
                "Edite el que está en la lista en lugar de crear otro."
            )
        producto_id = self.productos.crear(nombre, valor)
        return Producto(id=producto_id, nombre=nombre, precio=valor)

    def editar(self, producto_id: int, nombre: str, precio: str | float) -> Producto:
        if self.productos.obtener(producto_id) is None:
            raise NoEncontrado("Ese producto ya no existe en el catálogo.")
        nombre = limpiar_nombre(nombre)
        valor = limpiar_precio(precio)
        otro = self.productos.buscar_por_nombre(nombre)
        if otro and otro.id != producto_id:
            raise ProductoDuplicado(f"Ya existe otro producto llamado “{nombre}”.")
        self.productos.actualizar(producto_id, nombre, valor)
        return Producto(id=producto_id, nombre=nombre, precio=valor)

    def desactivar(self, producto_id: int) -> None:
        if self.productos.obtener(producto_id) is None:
            raise NoEncontrado("Ese producto ya no existe en el catálogo.")
        self.productos.desactivar(producto_id)

    def listar(self, texto: str = "") -> list[Producto]:
        return self.productos.listar(texto)


class ServicioVentas:
    """HU-02 y HU-03 — Registrar una venta y ver el día."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.ventas = RepositorioVentas(conn)
        self.productos = RepositorioProductos(conn)
        self.metodos = RepositorioMetodosPago(conn)

    def metodos_pago(self) -> list[MetodoPago]:
        return self.metodos.listar()

    def registrar(
        self,
        producto_id: int | None,
        cantidad: str | int,
        metodo_nombre: str,
        precio_unitario: str | float | None = None,
    ) -> Venta:
        """Registra la venta y devuelve lo que quedó guardado.

        El precio unitario se puede sobrescribir porque el mismo producto
        vale distinto al menudeo y por paquete: esa regla salió de la
        observación en el local.
        """
        if producto_id is None:
            raise DatoInvalido("Seleccione el producto que vendió.")
        producto = self.productos.obtener(producto_id)
        if producto is None:
            raise NoEncontrado("Ese producto ya no está en el catálogo.")

        unidades = limpiar_cantidad(cantidad)
        valor_unitario = (
            producto.precio
            if precio_unitario in (None, "")
            else limpiar_precio(precio_unitario)
        )

        metodo = self.metodos.buscar_por_nombre(metodo_nombre or "")
        if metodo is None:
            raise DatoInvalido("Seleccione el método de pago.")

        monto = round(valor_unitario * unidades, 2)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        venta_id = self.ventas.registrar(
            producto.id, metodo.id, unidades, monto, fecha
        )
        return Venta(
            id=venta_id,
            producto_id=producto.id,
            producto=producto.nombre,
            metodo=metodo.nombre,
            cantidad=unidades,
            monto=monto,
            fecha=fecha,
        )

    def anular(self, venta_id: int) -> None:
        self.ventas.anular(venta_id)

    def ventas_del_dia(self, dia: str | None = None) -> list[Venta]:
        return self.ventas.listar_del_dia(dia)

    def resumen_del_dia(self, dia: str | None = None) -> ResumenDia:
        return self.ventas.resumen_del_dia(dia)
