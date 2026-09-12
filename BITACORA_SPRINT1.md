# Bitácora — Sprint 1

Registro exigido por los numerales 8 y 9 del enunciado. Se actualiza en cada
Daily; el tablero del equipo está en Planner (Teams).

## Daily Scrum

| Fecha | Quién | Qué hice | Qué voy a hacer | Impedimentos |
|---|---|---|---|---|
| [dd/mm] | [Integrante 1] | | | |
| [dd/mm] | [Integrante 2] | | | |
| [dd/mm] | [Integrante 3] | | | |
| [dd/mm] | [Integrante 4] | | | |

## Burndown del Sprint 1 (medido en tareas, no en puntos)

| Día | Tareas pendientes | Tareas terminadas |
|---|---|---|
| 1 | | |
| 2 | | |

Historias del sprint y su talla (los story points van como texto dentro de
cada tarjeta de Planner):

| Historia | Talla | Tareas | Responsable |
|---|---|---|---|
| HU-01 Catálogo de productos | S | | |
| HU-02 Registrar venta (persistencia) | S | | |
| HU-03 Cierre del día | S | | |

## Registro de uso de IA

El enunciado evalúa especialmente la última columna: un equipo que no puede
explicar qué descartó y con qué criterio, no leyó lo que entregó.

| Fecha | Qué le pedimos | Qué aceptamos | Qué rechazamos y por qué |
|---|---|---|---|
| [dd/mm] | | | |

Ejemplos de rechazo que sirven de guía (reemplazar por los reales del equipo):

- Se descartó guardar el precio como texto en la base de datos: impide sumar
  totales en SQL y obliga a convertir en cada consulta.
- Se descartó borrar productos con `DELETE`: dejaría ventas apuntando a un
  producto que ya no existe. Se usa un campo `activo` en su lugar.
- Se descartó mostrar los errores técnicos de sqlite3 directamente al
  usuario: el tendero no puede hacer nada con un mensaje de `IntegrityError`.

## Definition of Done

Está en el README del repositorio y aplica a todas las historias.
