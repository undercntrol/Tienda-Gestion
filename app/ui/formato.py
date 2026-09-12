"""Formato de moneda y fechas, en la convención colombiana."""

from __future__ import annotations

from datetime import datetime


def pesos(valor: float) -> str:
    """1500.0 -> '$ 1.500'. Sin decimales: en la tienda nadie los usa."""
    entero = f"{round(float(valor)):,}".replace(",", ".")
    return f"$ {entero}"


def hora(fecha_iso: str) -> str:
    """'2026-09-12 14:32:05' -> '02:32 p. m.'"""
    try:
        momento = datetime.strptime(fecha_iso, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return fecha_iso
    etiqueta = "a. m." if momento.hour < 12 else "p. m."
    doce = momento.hour % 12 or 12
    return f"{doce:02d}:{momento.minute:02d} {etiqueta}"


def dia_largo(fecha_iso: str) -> str:
    """'2026-09-12' -> '12 de septiembre de 2026'"""
    meses = (
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    )
    try:
        dia = datetime.strptime(fecha_iso, "%Y-%m-%d")
    except ValueError:
        return fecha_iso
    return f"{dia.day} de {meses[dia.month - 1]} de {dia.year}"
