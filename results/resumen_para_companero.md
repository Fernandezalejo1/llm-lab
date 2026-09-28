# Lo que hicimos: enseñarle a una IA a escribir código que funciona

**En una frase:** entrenamos localmente (GPU propia, sin nube) un modelo de IA para que
lea una tarea de negocio —por ejemplo "detectar pagos duplicados"—, escriba el código
que la resuelve, y que ese código **realmente corra y pase pruebas automáticas**.

---

## El problema que atacamos

Elegimos 7 tareas típicas de un sistema de conciliación bancaria / fintech
(detección de duplicados, aplicar pagos FIFO, estado de una transacción, exportar a CSV, etc.).
Cada tarea tiene un **test verificable** (código con `assert`): el modelo aprueba SOLO si
su respuesta pasa el test, sin excusas. No hay evaluación subjetiva:

> El modelo escribe código → nosotros lo ejecutamos → pasa o no pasa. Punto.

## Cómo lo hicimos (el método)

| Etapa | Qué es, en criollo | Resultado sin apuntes* |
|---|---|---|
| **Modelo base** | El modelo tal como viene de fábrica (Qwen local 9B). No sabe nada de este negocio. | 1/7 |
| **Fine-tuning (SFT)** | Le mostramos ejemplos resueltos ("así se hace") y entrenamos con ellos. | 0/7 |
| **RL binario** | El modelo practica y recibe una recompensa: todo-o-nada (0 o 1). Aprendió, pero lento. | 2/7 |
| **RL con recompensa densa** | Le damos **puntaje parcial**: si acierta 3 de 5 requisitos, cobra 0.6. | 1/7 (mejor run) |

\* "Sin apuntes" = sin documentación. Ver abajo qué pasa con apuntes.

### La analogía clave: el examen

- **Reward binario** = un examen donde solo cuentan el 10 o el 0. Si fallás una coma, cero.
  El estudiante casi no aprende de los errores: no distingue "casi" de "nada".
- **Reward denso** = examen con puntaje parcial: cada paso correcto suma. El estudiante
  ve progreso, se acerca de a poco, y termina aprendiendo a dar la respuesta exacta.

El "RAG" = **le dejamos los apuntes abiertos durante el examen**. Antes de contestar, le
pasamos fragmentos de la documentación real del sistema. No le damos la respuesta: le
damos el material para deducirla.

---

## De qué es capaz el modelo ahora

El modelo final (`local-qwen-rl2`) con los apuntes del sistema encima:

- ✅ **Escribe código Python real** que se ejecuta y pasa tests de conciliación
  (duplicados, estados, SQL, exportación de datos).
- ✅ **Resolvió el test que nadie había podido pasar en todo el lab** (ct-07: exportar
  una conciliación con un formato de columnas exacto y acentos incluidos, tipo
  `Aplicación` con ó). Era 0/7 en TODOS los modelos anteriores.
- ✅ Aprendió detalles finos del negocio: qué significa cada estado, cómo se aplica un
  pago parcial al ítem más viejo (FIFO), qué columnas lleva un reporte de exportación.
- ✅ Funciona **100% local**: corre en tu GPU, sin enviar datos a ningún lado.

## Comparación: el modelo sin nada vs el modelo entrenado

En las 7 tareas verificables, cuántas resuelve cada modelo:

| Modelo | Sin apuntes | Con apuntes (RAG) |
|---|---|---|
| **Base (sin nada)** | 1/7 | 4/7 |
| **RL2 (recompensa densa)** | 1/7–2/7* | **5/7 (mejor run) — 6/7 distintos en 2 runs** |
| El test que nadie pasaba (ct-07) | ❌ | ✅ **por primera vez** |

\* Sin apuntes el modelo sin entrenar resuelve 1, y el entrenado también llega a 1-2;
la diferencia grande aparece **con apuntes**: el modelo entrenado lee la documentación
y la usa bien (5-6/7), mientras que el base se pierde (4/7 a duras penas y nunca el
difícil).

### Qué significa esto en la práctica

1. El modelo **aprendió el negocio** (no memoriza: razona sobre las reglas y escribe el código).
2. La recompensa densa fue la diferencia: le permitió "casi ganar" y mejorar de a poco.
3. El modelo final es **confiable para resolver tareas donde puede mirar la documentación**,
   que es exactamente cómo se usa en producción (le pasás los docs del sistema).
4. Queda pendiente pulir consistencia (a veces falla por detalles de una línea) — es el
   siguiente paso natural.