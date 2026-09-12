"""Objetos del dominio.

Son dataclasses sin lógica de base de datos: se pueden crear en una
prueba sin necesidad de conexión.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Producto:
    id: int
    nombre: str
    precio: float
    activo: bool = True


@dataclass(frozen=True)
class MetodoPago:
    id: int
    nombre: str


@dataclass(frozen=True)
class Venta:
    id: int
    producto_id: int | None
    producto: str
    metodo: str
    cantidad: int
    monto: float
    fecha: str  # ISO 8601: "2026-09-12 14:32:05"


@dataclass(frozen=True)
class ResumenDia:
    """Lo que el tendero necesita ver al cerrar: total y desglose."""

    fecha: str
    total: float
    unidades: int
    ventas: int
    por_metodo: dict[str, float]
