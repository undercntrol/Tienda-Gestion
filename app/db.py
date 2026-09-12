"""Acceso a SQLite: conexión, creación del esquema y migraciones.

Es la única parte del programa que sabe que la persistencia es SQLite.
Si en algún sprint se cambia el motor, se cambia este archivo y los
repositorios, no la interfaz.

Nombres de tablas y columnas se mantienen iguales a los del prototipo
previo, para que los datos que ya existen sigan sirviendo.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from . import config


ESQUEMA = (
    """
    CREATE TABLE IF NOT EXISTS productos (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre  TEXT    NOT NULL UNIQUE,
        precio  REAL    NOT NULL DEFAULT 0,
        activo  INTEGER NOT NULL DEFAULT 1
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS metodos_pago (
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT    NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS transacciones (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id INTEGER,
        metodo_id   INTEGER,
        cantidad    INTEGER NOT NULL DEFAULT 1,
        monto       REAL    NOT NULL,
        fecha       TEXT    NOT NULL,
        FOREIGN KEY (producto_id) REFERENCES productos(id)   ON DELETE SET NULL,
        FOREIGN KEY (metodo_id)   REFERENCES metodos_pago(id) ON DELETE SET NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_transacciones_fecha ON transacciones(fecha)",
)

# Migraciones: cada entrada es (tabla, columna, definición).
# Permite agregar columnas sin romper una base de datos que ya está en uso
# en la tienda. Es el patrón que se seguirá en los sprints siguientes.
MIGRACIONES = (
    ("productos", "activo", "INTEGER NOT NULL DEFAULT 1"),
    ("transacciones", "cantidad", "INTEGER NOT NULL DEFAULT 1"),
)


def conectar(ruta: Path | str | None = None) -> sqlite3.Connection:
    """Abre la conexión, crea el esquema si hace falta y lo migra.

    Pasar ruta=":memory:" sirve para las pruebas automáticas.
    """
    if ruta is None:
        config.CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
        ruta = config.RUTA_BD
    elif ruta != ":memory:":
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(ruta))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    _crear_esquema(conn)
    _migrar(conn)
    _sembrar_metodos_pago(conn)
    return conn


def _crear_esquema(conn: sqlite3.Connection) -> None:
    for sentencia in ESQUEMA:
        conn.execute(sentencia)
    conn.commit()


def _columnas(conn: sqlite3.Connection, tabla: str) -> set[str]:
    filas = conn.execute(f"PRAGMA table_info({tabla})").fetchall()
    return {fila["name"] for fila in filas}


def _migrar(conn: sqlite3.Connection) -> None:
    for tabla, columna, definicion in MIGRACIONES:
        if columna not in _columnas(conn, tabla):
            conn.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")
    conn.commit()


def _sembrar_metodos_pago(conn: sqlite3.Connection) -> None:
    """Sin métodos de pago no se puede vender, así que se crean solos."""
    hay = conn.execute("SELECT COUNT(*) FROM metodos_pago").fetchone()[0]
    if hay:
        return
    conn.executemany(
        "INSERT INTO metodos_pago (nombre) VALUES (?)",
        [(nombre,) for nombre in config.METODOS_PAGO_INICIALES],
    )
    conn.commit()
