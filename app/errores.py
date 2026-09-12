"""Errores propios del dominio.

Se separan de las excepciones de sqlite3 a propósito: la interfaz solo
debe mostrarle al tendero mensajes que él entienda. Cualquier error que
no sea de esta familia es un error técnico y se registra distinto.
"""


class ErrorDeNegocio(Exception):
    """Algo que el usuario hizo mal y puede corregir."""


class DatoInvalido(ErrorDeNegocio):
    """Un campo llegó vacío, con letras donde van números, o fuera de rango."""


class ProductoDuplicado(ErrorDeNegocio):
    """Ya existe un producto con ese nombre."""


class NoEncontrado(ErrorDeNegocio):
    """Se pidió un registro que no está en la base de datos."""
