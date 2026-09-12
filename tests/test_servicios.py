"""Pruebas de las reglas del Sprint 1.

Corren sin interfaz y sin tocar la base de datos real: cada prueba usa
una base en memoria. Ejecutar desde la carpeta del proyecto:

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db  # noqa: E402
from app.errores import DatoInvalido, NoEncontrado, ProductoDuplicado  # noqa: E402
from app.servicios import (  # noqa: E402
    ServicioCatalogo,
    ServicioVentas,
    limpiar_cantidad,
    limpiar_nombre,
    limpiar_precio,
)


class PruebasDeLimpieza(unittest.TestCase):
    def test_acepta_los_formatos_que_usa_el_tendero(self):
        for texto in ("2500", "2.500", "$ 2.500", " 2500 "):
            self.assertEqual(limpiar_precio(texto), 2500.0, texto)

    def test_rechaza_precio_con_letras(self):
        with self.assertRaises(DatoInvalido):
            limpiar_precio("dos mil")

    def test_rechaza_precio_cero_o_negativo(self):
        for texto in ("0", "-100"):
            with self.assertRaises(DatoInvalido):
                limpiar_precio(texto)

    def test_rechaza_precio_absurdo(self):
        with self.assertRaises(DatoInvalido):
            limpiar_precio("99999999")

    def test_cantidad_debe_ser_entero_positivo(self):
        self.assertEqual(limpiar_cantidad("3"), 3)
        for texto in ("", "0", "-2", "dos", "1.5"):
            with self.assertRaises(DatoInvalido):
                limpiar_cantidad(texto)

    def test_nombre_se_normaliza(self):
        self.assertEqual(limpiar_nombre("  gaseosa   350   "), "gaseosa 350")
        with self.assertRaises(DatoInvalido):
            limpiar_nombre("   ")


class PruebasDeCatalogo(unittest.TestCase):
    def setUp(self):
        self.conn = db.conectar(":memory:")
        self.catalogo = ServicioCatalogo(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_crear_producto_queda_guardado(self):
        producto = self.catalogo.crear("Gaseosa 350", "2.500")
        self.assertEqual(producto.precio, 2500.0)
        self.assertEqual(len(self.catalogo.listar()), 1)

    def test_no_permite_nombre_repetido_ni_con_otras_mayusculas(self):
        self.catalogo.crear("Gaseosa 350", "2500")
        with self.assertRaises(ProductoDuplicado):
            self.catalogo.crear("gaseosa 350", "3000")

    def test_editar_cambia_precio(self):
        producto = self.catalogo.crear("Pan", "500")
        self.catalogo.editar(producto.id, "Pan", "700")
        self.assertEqual(self.catalogo.listar()[0].precio, 700.0)

    def test_editar_producto_inexistente_avisa(self):
        with self.assertRaises(NoEncontrado):
            self.catalogo.editar(999, "Pan", "700")

    def test_producto_desactivado_sale_de_la_lista(self):
        producto = self.catalogo.crear("Cigarrillo suelto", "1000")
        self.catalogo.desactivar(producto.id)
        self.assertEqual(self.catalogo.listar(), [])

    def test_busqueda_filtra_por_texto(self):
        self.catalogo.crear("Gaseosa 350", "2500")
        self.catalogo.crear("Pan tajado", "4800")
        self.assertEqual(len(self.catalogo.listar("gaseo")), 1)


class PruebasDeVentas(unittest.TestCase):
    def setUp(self):
        self.conn = db.conectar(":memory:")
        self.catalogo = ServicioCatalogo(self.conn)
        self.ventas = ServicioVentas(self.conn)
        self.producto = self.catalogo.crear("Gaseosa 350", "2500")

    def tearDown(self):
        self.conn.close()

    def test_metodos_de_pago_vienen_sembrados(self):
        nombres = [m.nombre for m in self.ventas.metodos_pago()]
        self.assertIn("Efectivo", nombres)
        self.assertIn("Nequi", nombres)

    def test_registrar_calcula_el_monto(self):
        venta = self.ventas.registrar(self.producto.id, "3", "Efectivo")
        self.assertEqual(venta.monto, 7500.0)
        self.assertEqual(venta.cantidad, 3)

    def test_precio_se_puede_sobrescribir_para_paquete(self):
        venta = self.ventas.registrar(self.producto.id, "10", "Efectivo", "2000")
        self.assertEqual(venta.monto, 20000.0)

    def test_exige_producto(self):
        with self.assertRaises(DatoInvalido):
            self.ventas.registrar(None, "1", "Efectivo")

    def test_exige_metodo_de_pago_valido(self):
        with self.assertRaises(DatoInvalido):
            self.ventas.registrar(self.producto.id, "1", "Bitcoin")

    def test_producto_borrado_no_se_puede_vender(self):
        self.conn.execute("DELETE FROM productos WHERE id = ?", (self.producto.id,))
        self.conn.commit()
        with self.assertRaises(NoEncontrado):
            self.ventas.registrar(self.producto.id, "1", "Efectivo")

    def test_resumen_del_dia_suma_y_desglosa(self):
        self.ventas.registrar(self.producto.id, "2", "Efectivo")   # 5.000
        self.ventas.registrar(self.producto.id, "1", "Nequi")      # 2.500
        resumen = self.ventas.resumen_del_dia(date.today().isoformat())
        self.assertEqual(resumen.total, 7500.0)
        self.assertEqual(resumen.ventas, 2)
        self.assertEqual(resumen.unidades, 3)
        self.assertEqual(resumen.por_metodo["Efectivo"], 5000.0)
        self.assertEqual(resumen.por_metodo["Nequi"], 2500.0)

    def test_anular_quita_la_venta_del_dia(self):
        venta = self.ventas.registrar(self.producto.id, "1", "Efectivo")
        self.ventas.anular(venta.id)
        self.assertEqual(self.ventas.resumen_del_dia().total, 0.0)


class PruebasDePersistencia(unittest.TestCase):
    """La prueba que respalda la condición 1: los datos sobreviven al cierre."""

    def test_los_datos_siguen_ahi_despues_de_cerrar(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "prueba.db"

            conn = db.conectar(ruta)
            producto = ServicioCatalogo(conn).crear("Arepa", "1500")
            ServicioVentas(conn).registrar(producto.id, "2", "Efectivo")
            conn.close()

            conn = db.conectar(ruta)  # se vuelve a abrir, como al día siguiente
            self.assertEqual(len(ServicioCatalogo(conn).listar()), 1)
            self.assertEqual(ServicioVentas(conn).resumen_del_dia().total, 3000.0)
            conn.close()

    def test_la_migracion_no_rompe_una_base_ya_creada(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "vieja.db"
            conn = db.conectar(ruta)
            conn.close()
            conn = db.conectar(ruta)  # segunda apertura: no debe fallar
            columnas = {
                fila["name"]
                for fila in conn.execute("PRAGMA table_info(transacciones)")
            }
            self.assertIn("cantidad", columnas)
            conn.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
