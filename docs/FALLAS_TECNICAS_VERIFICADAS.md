# Fallas técnicas verificadas — EG2026 Perú 1ra vuelta

Inventario de fallas operativas/técnicas del 12 de abril 2026 con **fuente
pública verificable**. Solo se listan hechos con trazabilidad documental.

**Corte:** ONPE 93.17% · **Fecha compilación:** 2026-04-17
**Responsable técnico:** Jack Aguilar (Neuracode). Aporte ciudadano, sin
afiliación política.

---

## Principio de admisibilidad

Cada ítem requiere al menos uno de:
- Declaración oficial ONPE / JNE / JEE con fecha y URL.
- Nota de medio con credenciales periodísticas (Ojo Público, La República
  Verificador, Gestión, El Comercio, RPP).
- Documento legal ingresado (memorial, resolución, denuncia).
- Pronunciamiento público de autoridad competente (Defensoría, Contraloría).

**No se incluyen:** rumores de redes sociales, videos virales sin verificación,
atribuciones sin fuente nombrada.

---

## 1. Falla de proveedor CALAG / Servicios Generales Galaga (CAPA L0)

### Hecho

15 locales de votación en Lima Metropolitana no abrieron normalmente el 12
de abril por incumplimiento del proveedor Servicios Generales Galaga S.A.C.
(en adelante CALAG).

### Cifras oficiales ONPE

- **Locales afectados:** 15.
- **Mesas afectadas:** 211.
- **Electores que no pudieron votar:** 63,300.
- **Declaración:** Presidente ONPE Piero Corvetto, conferencia 12-abril-2026.

### Contexto contractual

- Proveedor contratado vía **mecanismo excepcional** fuera de la Ley de
  Contrataciones del Estado 30225 (según reportes Gestión y Ojo Público).
- Monto contractual y detalle pendiente de Contraloría.

### Conflicto documental (importante)

- **CALAG desmintió públicamente a ONPE** y la denunció por atribución de
  negligencia. Este es un **conflicto entre las dos partes contractuales
  sobre los mismos hechos** — fuente testimonial-documental fuerte para
  peritaje.

### Severidad

**ALTA procesal.** Permite vía Art. 363 Ley 26859 si se demuestra que el
evento alteró el resultado.

### Estado legal

Corvetto citado al Ministerio Público el 2026-04-17 para declarar.

---

## 2. Sistema STAE (Sistema Técnico de Apoyo al Escrutinio) — fallas reportadas

### Hecho

Reportes periodísticos el 12-13 abril indican fallas en el sistema STAE que
usan las mesas para capturar resultados del escrutinio.

### Fuente

- La República Verificador, Gestión: múltiples locales de Lima y Callao con
  pantallas fuera de servicio durante la tarde.

### Impacto cuantificable

**Pendiente.** ONPE no ha publicado número de mesas que debieron volver a
escrutinio manual por fallas STAE.

### Pedido en memorial

Variable #10 del memorial: lista de mesas que reportaron falla STAE con
timestamp y duración de la falla.

---

## 3. Impresión y tinta en cédulas

### Hecho parcialmente verificado

Se difundieron narrativas sobre "cédulas destruidas por tinta" en un local
del Callao (IE 5031). La República Verificador aclaró que el incidente fue
por **falla del sistema de impresión**, no por tinta específicamente.

### Fuente

- La República Verificador, fact-check 13-abril-2026.

### Lo verificado

- Sí hubo locales con cédulas impresas incorrectamente.
- No hay cifra oficial consolidada del número de cédulas afectadas ni
  electores impactados.

### Lo NO verificado (excluir del memorial sin prueba)

- Narrativa de "sabotaje con tinta".
- Atribución a un partido o candidato específico.

### Severidad

**MEDIA hasta confirmar número.** Si n < 100 cédulas nacional, es ruido
operativo. Si n > 10,000, eventual nulidad de mesas.

---

## 4. Personeros ausentes — caso San Luis Gonzaga (ICA)

### Hecho

Universidad San Luis Gonzaga (ICA): 30 mesas sin personeros de ningún
partido. ~8,000 electores en el local.

### Fuente

- La República, Gestión, reportaje 12-abril-2026.

### Implicancia técnica

La ausencia de personeros **NO anula el acta** si los miembros de mesa
firmaron. Pero debilita la cadena de custodia adversarial (un personero
es el único que puede impugnar en tiempo real).

### Severidad

**MEDIA.** Es legítimo solicitar peritaje adicional de estas 30 mesas en
particular (revisión física del acta).

---

## 5. 13% de mesas en Lima Metropolitana no abrieron hasta las 2 pm

### Hecho

RLA presentó ante JNE un informe indicando que, al corte de las 14:00 del
12 de abril, **13% de mesas en Lima Metropolitana aún no habían abierto**.
Lima Metropolitana representa ~30% del padrón nacional.

### Fuente

- Petitorio formal RLA al JNE, 13-abril-2026.

### Cálculo indicativo (no definitivo)

- Padrón Lima Metropolitana ≈ 8.0M electores.
- 13% de mesas no abiertas a 14:00 ≈ 1.04M electores potencialmente
  impactados **si esas mesas hubieran estado cerradas todo el día**.
- **Caveat:** esas mesas abrieron después — la cifra de *electores que
  efectivamente no votaron* por esa razón es **menor**, pero no hay
  dato oficial consolidado.

### Problema de honestidad

El horario oficial de votación es 7:00–16:00. Que una mesa abra después
de las 7 am es una falla operativa, pero **no equivale a que el elector
no pudo votar**. La pregunta clave es: ¿cuántos electores llegaron al
local en la mañana y se retiraron antes de que la mesa abriera?

Respuesta honesta: **no se sabe sin encuesta dirigida**.

### Severidad

**MEDIA.** Contribuye al ausentismo atípico 2026 vs 2016 (+7.95 pp), pero
no se puede atribuir toda la diferencia a las aperturas tardías.

---

## 6. Ausentismo comparativo (contexto agregado)

### Hechos

| Elección | Padrón | Emitidos | Ausentismo |
|----------|--------|----------|------------|
| 2016 1ra vuelta | 22.9M | 18.7M | **18.21%** (pre-pandemia) |
| 2021 1ra vuelta | 25.3M | 17.9M | **29.15%** (durante pandemia) |
| 2026 1ra vuelta (proy 100%) | 27.4M | ~20.2M | **~26.16%** (post-pandemia) |

### Delta relevante (HONESTO)

- **2026 vs 2016 (pre/post pandemia limpio):** +7.95 pp. Equivale a ~3.0M
  electores adicionales que no votaron.
- **2026 vs 2021:** −2.99 pp. El ausentismo 2026 es **MENOR** que 2021 —
  efecto pandemia inflaba 2021. **La narrativa "post-pandemia subió
  ausentismo vs pandemia" NO se sostiene con datos oficiales.**

### Severidad

**MEDIA.** +7.95 pp es clínicamente significativo pero no imputable a una
sola causa (fallas técnicas, desconfianza, clima, protesta política).

---

## Síntesis (lo que aguanta peritaje)

| # | Falla | Cifra verificada | Severidad | Estado |
|---|-------|------------------|-----------|--------|
| 1 | CALAG/Galaga 15 locales | 63,300 electores | ALTA | Fiscal + Contraloría |
| 2 | STAE fallas mesas | SIN CIFRA | MEDIA | Pedir a ONPE |
| 3 | Cédulas mal impresas | SIN CIFRA | MEDIA | Pedir a ONPE |
| 4 | Personeros ausentes San Luis Gonzaga | 30 mesas / 8,000 electores | MEDIA | Peritaje actas |
| 5 | Mesas cerradas 14:00 Lima | 13% (est. 1.04M potencial) | MEDIA | Encuesta dirigida |
| 6 | Ausentismo vs 2016 | +7.95 pp / ~3.0M | MEDIA | Contexto |

---

## Lo que se excluye del memorial (sin fuente dura)

- "Digitadores venezolanos contratados por ONPE" — **sin contratos públicos
  verificables**.
- "Corvetto trabajó en Venezuela" — **falso, desmentido por Ojo Público**
  (fact-check).
- "Operación Morrocoy como inteligencia cubana aplicada en Perú" — **sin
  peer-review que lo tipifique**.
- "Robo a Keiko 2021 por 44 votos" — **OEA y UE descartaron fraude**;
  incluirlo en el memorial debilita todo.
- Rumores de redes sociales sin fuente periodística verificable.

---

**Documento reproducible.** Cuando el Fiscal compela a ONPE/JEE a entregar
los datasets faltantes, cada cifra "SIN CIFRA" será reemplazada por el
dato oficial.

**Repositorio:** `github.com/jackthony/auditoria-eg2026`
**Licencia:** CC-BY-4.0
**Autoría:** Neuracode · Jack Aguilar (aporte ciudadano, sin retribución,
sin afiliación política).
