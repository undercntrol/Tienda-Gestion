"""Repositorios: todo el SQL del proyecto vive aquí.

Reciben la conexión por parámetro (inyección simple) para que las
pruebas puedan usar una base en memoria.
"""

from __future__ import annotations

import sqlite3
from datetime import date

from .modelos import MetodoPago, Producto, ResumenDia, Venta


class RepositorioProductos:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def crear(self, nombre: str, precio: float) -> int:
        cur = self.conn.execute(
            "INSERT INTO productos (nombre, precio) VALUES (?, ?)",
            (nombre, precio),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def actualizar(self, producto_id: int, nombre: str, precio: float) -> None:
        self.conn.execute(
            "UPDATE productos SET nombre = ?, precio = ? WHERE id = ?",
            (nombre, precio, producto_id),
        )
        self.conn.commit()

    def desactivar(self, producto_id: int) -> None:
        """No se borra: un producto borrado dejaría ventas huérfanas."""
        self.conn.execute(
            "UPDATE productos SET activo = 0 WHERE id = ?", (producto_id,)
        )
        self.conn.commit()

    def obtener(self, producto_id: int) -> Producto | None:
        fila = self.conn.execute(
            "SELECT id, nombre, precio, activo FROM productos WHERE id = ?",
            (producto_id,),
        ).fetchone()
        return self._a_producto(fila) if fila else None

    def buscar_por_nombre(self, nombre: str) -> Producto | None:
        fila = self.conn.execute(
            "SELECT id, nombre, precio, activo FROM productos "
            "WHERE lower(nombre) = lower(?)",
            (nombre.strip(),),
        ).fetchone()
        return self._a_producto(fila) if fila else None

    def listar(self, texto: str = "", solo_activos: bool = True) -> list[Producto]:
        sql = "SELECT id, nombre, precio, activo FROM productos WHERE 1 = 1"
        params: list[object] = []
        if solo_activos:
            sql += " AND activo = 1"
        if texto.strip():
            sql += " AND nombre LIKE ?"
            params.append(f"%{texto.strip()}%")
        sql += " ORDER BY nombre COLLATE NOCASE"
        filas = self.conn.execute(sql, params).fetchall()
        return [self._a_producto(f) for f in filas]

    @staticmethod
    def _a_producto(fila: sqlite3.Row) -> Producto:
        return Producto(
            id=fila["id"],
            nombre=fila["nombre"],
            precio=float(fila["precio"]),
            activo=bool(fila["activo"]),
        )


class RepositorioMetodosPago:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def listar(self) -> list[MetodoPago]:
        filas = self.conn.execute(
            "SELECT id, nombre FROM metodos_pago ORDER BY id"
        ).fetchall()
        return [MetodoPago(id=f["id"], nombre=f["nombre"]) for f in filas]

    def buscar_por_nombre(self, nombre: str) -> MetodoPago | None:
        fila = self.conn.execute(
            "SELECT id, nombre FROM metodos_pago WHERE lower(nombre) = lower(?)",
            (nombre.strip(),),
        ).fetchone()
        return MetodoPago(id=fila["id"], nombre=fila["nombre"]) if fila else None


class RepositorioVentas:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def registrar(
        self,
        producto_id: int,
        metodo_id: int,
        cantidad: int,
        monto: float,
        fecha: str,
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO transacciones (producto_id, metodo_id, cantidad, monto, fecha) "
            "VALUES (?, ?, ?, ?, ?)",
            (producto_id, metodo_id, cantidad, monto, fecha),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    def anular(self, venta_id: int) -> None:
        self.conn.execute("DELETE FROM transacciones WHERE id = ?", (venta_id,))
        self.conn.commit()

    def listar_del_dia(self, dia: str | None = None) -> list[Venta]:
        dia = dia or date.today().isoformat()
        filas = self.conn.execute(
            """
            SELECT t.id,
                   t.producto_id,
                   COALESCE(p.nombre, '(producto eliminado)') AS producto,
                   COALESCE(m.nombre, '(sin método)')         AS metodo,
                   t.cantidad, t.monto, t.fecha
              FROM transacciones t
              LEFT JOIN productos    p ON p.id = t.producto_id
              LEFT JOIN metodos_pago m ON m.id = t.metodo_id
             WHERE date(t.fecha) = ?
             ORDER BY t.id DESC
            """,
            (dia,),
        ).fetchall()
        return [
            Venta(
                id=f["id"],
                producto_id=f["producto_id"],
                producto=f["producto"],
                metodo=f["metodo"],
                cantidad=int(f["cantidad"]),
                monto=float(f["monto"]),
                fecha=f["fecha"],
            )
            for f in filas
        ]

    def resumen_del_dia(self, dia: str | None = None) -> ResumenDia:
        dia = dia or date.today().isoformat()
        totales = self.conn.execute(
            """
            SELECT COUNT(*)                  AS ventas,
                   COALESCE(SUM(monto), 0)   AS total,
                   COALESCE(SUM(cantidad),0) AS unidades
              FROM transacciones
             WHERE date(fecha) = ?
            """,
            (dia,),
        ).fetchone()
        filas = self.conn.execute(
            """
            SELECT COALESCE(m.nombre, '(sin método)') AS metodo,
                   COALESCE(SUM(t.monto), 0)          AS total
              FROM transacciones t
              LEFT JOIN metodos_pago m ON m.id = t.metodo_id
             WHERE date(t.fecha) = ?
             GROUP BY metodo
             ORDER BY total DESC
            """,
            (dia,),
        ).fetchall()
        return ResumenDia(
            fecha=dia,
            total=float(totales["total"]),
            unidades=int(totales["unidades"]),
            ventas=int(totales["ventas"]),
            por_metodo={f["metodo"]: float(f["total"]) for f in filas},
        )
