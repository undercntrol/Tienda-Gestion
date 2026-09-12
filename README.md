# Tienda Gestión — Sprint 1

Sistema de ventas y cuentas por cobrar para una cigarrería de barrio.
Proyecto Integrador — Práctica Aplicada · TIC42695 · Semestre 2026-2

**Equipo:** [Integrante 1] · [Integrante 2] · [Integrante 3] · [Integrante 4]
**Repositorio:** github.com/[organización]/[repositorio]

---

## Product Goal

Lograr que la cigarrería lleve digitalmente sus ventas y cuentas por cobrar,
de modo que al cierre de cada día el tendero conozca el total vendido por
método de pago y el saldo exacto de cada cliente, reduciendo el tiempo de
cuadre diario de 20 a menos de 5 minutos y eliminando las deudas no
registradas, dentro de las 16 semanas del semestre.

## Sprint Goal del Sprint 1

Que el tendero pueda registrar una venta y ver cuánto vendió en el día, con
la información guardada en disco.

## Historias del Sprint 1

El enunciado pone tope de tres historias pequeñas y exige que al menos una
involucre persistencia de datos.

### HU-01 · Registrar productos en el catálogo — talla S

> Como dueño de la tienda quiero registrar mis productos con su precio,
> para no tener que acordarme del precio de cada cosa cuando vendo.

Criterios de aceptación:

1. Al guardar un producto con nombre y precio, aparece en la lista ordenada
   alfabéticamente.
2. El precio se acepta escrito como `2500`, `2.500` o `$ 2.500`.
3. Si el nombre ya existe (con cualquier combinación de mayúsculas), la
   aplicación lo avisa y no crea un duplicado.
4. Si el precio está vacío, es cero, es negativo o tiene letras, se muestra
   un mensaje que explica qué corregir y no se guarda nada.
5. Al quitar un producto, este desaparece del catálogo pero las ventas ya
   registradas se conservan.

### HU-02 · Registrar una venta — talla S · **incluye persistencia**

> Como quien atiende el mostrador quiero registrar la venta con producto,
> cantidad y método de pago, para que quede guardada sin tener que anotarla
> en la libreta.

Criterios de aceptación:

1. Al elegir el producto, el precio del catálogo se carga automáticamente.
2. El precio unitario se puede cambiar para esa venta (menudeo o paquete).
3. El total se recalcula en pantalla al cambiar cantidad o precio.
4. Al registrar, la venta queda guardada con fecha y hora y aparece en la
   lista de las últimas ventas del día.
5. Sin producto o sin método de pago, la venta no se registra y se explica
   por qué.
6. **Al cerrar y volver a abrir la aplicación, la venta sigue ahí.**
7. La última venta registrada se puede anular.

### HU-03 · Ver el cierre del día — talla S

> Como dueño quiero ver el total vendido hoy y cómo se reparte entre
> efectivo, Nequi, Daviplata y tarjeta, para cuadrar sin hacerlo de memoria.

Criterios de aceptación:

1. Se muestra el total vendido del día, el número de ventas y las unidades.
2. Hay un desglose por método de pago.
3. Se listan las ventas del día con hora, producto, cantidad, método y monto.
4. Si no hay ventas, los totales aparecen en cero y no se cae la pantalla.

## Definition of Done del equipo

Una historia está terminada cuando:

- [ ] Cumple todos sus criterios de aceptación, probados a mano en la
      aplicación corriendo.
- [ ] Tiene pruebas automáticas de sus reglas de negocio y `python -m
      unittest discover -s tests` pasa completo.
- [ ] El código está en una rama propia, revisado por otro integrante y
      mezclado a `main` por pull request.
- [ ] Los errores posibles muestran un mensaje que el tendero entiende.
- [ ] La documentación del repositorio quedó actualizada.
- [ ] El uso de IA quedó registrado en la bitácora del sprint.

## Cómo ejecutarlo

Requiere Python 3.10 o superior. No hay dependencias externas: solo la
librería estándar (`tkinter` y `sqlite3`).

```bash
cd tienda_gestion
python main.py
```

La base de datos se crea sola en `tienda_gestion/datos/tienda.db`. Es un
solo archivo: se puede copiar a una USB para respaldarlo.

Pruebas automáticas:

```bash
cd tienda_gestion
python -m unittest discover -s tests -v
```

## Estructura del proyecto

```
tienda_gestion/
├── main.py                  punto de entrada
├── app/
│   ├── config.py            rutas, colores, límites de validación
│   ├── errores.py           errores de dominio (lo que el usuario puede corregir)
│   ├── db.py                conexión SQLite, esquema y migraciones
│   ├── modelos.py           Producto, Venta, ResumenDia
│   ├── repositorios.py      todo el SQL del proyecto
│   ├── servicios.py         reglas de negocio y validaciones
│   └── ui/
│       ├── ventana.py       ventana principal y pestañas
│       ├── vista_venta.py   HU-02
│       ├── vista_catalogo.py HU-01
│       ├── vista_dia.py     HU-03
│       └── formato.py       moneda y fechas en formato colombiano
└── tests/
    └── test_servicios.py    22 pruebas de reglas y persistencia
```

La separación en capas no es adorno: cada sprint siguiente agrega una vista
y un servicio sin tocar lo anterior, y las reglas se pueden probar sin abrir
la ventana.

## Modelo de datos

```
productos      (id, nombre único, precio, activo)
metodos_pago   (id, nombre único)          ← se siembran Efectivo, Nequi, Daviplata, Tarjeta
transacciones  (id, producto_id, metodo_id, cantidad, monto, fecha)
```

Los nombres de tablas y columnas son los mismos del prototipo previo, para
que los datos que ya existen sigan sirviendo. `db.MIGRACIONES` permite
agregar columnas sin romper una base que ya está en uso en la tienda; así se
agregarán `clientes` y los saldos en el Sprint 2.

## Condiciones técnicas del enunciado — estado al cerrar el Sprint 1

| # | Condición | Estado |
|---|---|---|
| 1 | Persistencia real | **Cumplida.** SQLite en archivo; hay prueba automática de que los datos sobreviven al cierre |
| 2 | Sesión o control de acceso | Pendiente — Sprint 2 |
| 3 | Integración externa | Pendiente — Sprint 4 |
| 4 | Consulta con filtrado | Parcial — búsqueda en el catálogo; los filtros completos van en el Sprint 3 |
| 5 | Manejo de errores visible | **Cumplida** para el alcance de este sprint |
| 6 | Repositorio en GitHub | **Cumplida** |
| 7 | Documentación versionada | **Cumplida** — este archivo |

## Lo que sigue

- **Sprint 2:** clientes, fiado, abonos parciales, cobro con comprobante,
  usuarios con rol y login.
- **Sprint 3:** cierre de caja con filtros por periodo y exportación.
- **Sprint 4:** recordatorio de cobro (integración externa) y release
  empaquetado.
