# Evidencia Ciudadana — Auditoría Estadística EG2026 1ra vuelta

**Versión pública para difusión.** Lenguaje accesible, fuentes citables,
hallazgos honestos (incluyendo los que no favorecen al cliente RLA).

**Autoría:** Jack Aguilar · Neuracode
**Fecha:** 2026-04-17 · **Corte ONPE analizado:** 93.17%
**Repositorio público:** `github.com/jackthony/auditoria-eg2026`
**Licencia:** CC-BY-4.0

---

## ¿Qué es este documento?

Una auditoría estadística independiente del proceso de cómputo oficial
ONPE de la primera vuelta de las Elecciones Generales 2026 en Perú.

**No es un peritaje oficial.** Es evidencia técnica ciudadana reproducible.
Cualquier persona puede descargar el código, re-ejecutar los análisis, y
obtener los mismos resultados.

**No imputa fraude.** Detecta anomalías estadísticas y pide explicación
formal a ONPE y JEE.

---

## Contexto

- Margen Sánchez−RLA al 93.17%: **+5,875 votos**.
- Separación 3º–4º puesto: **<0.04 puntos porcentuales**.
- Actas aún en JEE (pendientes): **5,555**.
- Electores que no pudieron votar en Lima el 12-abril por fallas CALAG:
  **63,300 (oficial ONPE)**.

El resultado final de quién pasa a 2ª vuelta puede ser alterado por
cualquiera de estos factores.

---

## Los hallazgos (15 en total)

### 1. Inconsistencia de agregación ONPE (finding A0)

Al comparar el total nacional publicado por ONPE con la suma de las 26
regiones, **21 actas no reconcilian**. Nacional dice 86,438 contabilizadas,
suma regional dice 86,434. Nacional dice 773 pendientes JEE, suma regional
dice 794.

Esto equivale a ~4,582 votos potenciales en zona gris. **Ratio 0.78× del
margen final.** No alcanza para invertir el resultado por sí solo, pero
requiere explicación formal de ONPE.

**Importante:** este finding NO prueba error en conteo de votos. Sí prueba
que el sistema de ONPE tiene integridad de agregación débil.

**Origen:** fue denunciado públicamente por un ciudadano el 17-abril-2026
(reportó "633 vs 773 actas"). Verificado con snapshots propios.

---

### 2. Fallas del proveedor CALAG / Servicios Generales Galaga (A-AUS-3)

**Hecho oficial ONPE:** 15 locales, 211 mesas, 63,300 electores no pudieron
votar en Lima. Proveedor contratado vía mecanismo excepcional fuera de la
Ley de Contrataciones.

**Ratio clave (corte 93.474% al 2026-04-18):** 63,300 afectados / 13,624 margen = **4.64×**. El número
oficial de afectados supera en 4.64 veces al margen que define la elección.
*Margen vivo en `data/processed/meta.json`; valor histórico al 93.17%: 5,898 (ratio 10.73×).*

Si incluso un 10% de esos electores hubieran preferido a RLA sobre Sánchez,
el resultado se invierte. Esto abre el estándar del **Art. 363 de la Ley
26859** (nulidad parcial por evento que *podría* alterar resultado).

CALAG desmintió a ONPE y la denunció. Es conflicto entre las dos partes
contractuales sobre los mismos hechos — **evidencia testimonial fuerte**
para peritaje.

---

### 3. Ausentismo post-pandemia (A-AUS-1)

| Elección | Ausentismo |
|----------|-----------|
| 2016 pre-pandemia | 18.21% |
| 2021 durante pandemia | 29.15% |
| 2026 post-pandemia (proy. 100%) | **26.16%** |

**Comparación limpia:** 2026 vs 2016 (pre/post pandemia). Delta: **+7.95 pp**
= ~3.0 millones de electores adicionales no votaron.

### Hallazgo adverso (honestidad obligatoria)

Ausentismo 2026 está **por debajo** de 2021. La narrativa "ausentismo subió
post-pandemia vs pandemia" NO se sostiene con datos oficiales. La
comparación válida es 2026 vs 2016 (pre-pandemia).

---

### 4. Velocidad de procesamiento JEE (H1, H2)

Después del cruce en que Sánchez superó a RLA, la velocidad de
procesamiento de actas en el JEE cambió significativamente:

- ±6h antes: +182.6 actas/h. Después: +92.4 actas/h.
- Mann-Whitney p=0.013.

**Hallazgo adverso:** la desaceleración es **0.45× (más lenta, no más
rápida)** post-cruce. Esto **contradice** la narrativa viral de
"aceleración post-cruce para perjudicar a RLA". Hubo desaceleración.

Dos interpretaciones alternativas:
1. Procesamiento natural (actas fáciles primero).
2. Cambio de política post-cruce.

Requiere explicación formal de JEE.

---

### 5. Forecast bayesiano (F1)

Modelo bayesiano Dirichlet-Multinomial + Beta prior sobre JEE, 10,000
simulaciones:

- **P(RLA supera a Sánchez) = 42.3% (central) / 43.2% (mixto)**.

Esto significa: **estamos en empate estadístico**. La distribución de
resultados finales es bimodal — hay probabilidad relevante en ambos
escenarios de ganador.

---

### 6. Moran's I espacial (M2)

- RLA tiene clustering geográfico fuerte (I=+0.317, p=0.011). Normal
  para un candidato con base electoral concentrada.
- Sánchez es disperso (p=0.854). Normal.
- **Hallazgo adverso:** la tasa de impugnación **NO co-clusteriza** con
  el share de RLA a nivel regional (bivariado I=−0.023, p=0.837). Esto
  **debilita** la hipótesis de focalización geográfica dirigida contra RLA.

A nivel mesa puede ser distinto — pendiente de data bajo apercibimiento.

---

### 7. Último dígito y primer dígito (M1, C1)

Tests Mebane/Beber-Scacco y Benford: **conformes a uniforme/Benford**.
No se detecta adulteración manual a escala regional.

**Caveat:** con n=26 por candidato, el poder estadístico es limitado.
"Conforme" no descarta manipulación a menor escala (mesa).

---

## Lo que esta auditoría NO dice

1. **No afirma fraude ni dolo.** Los tests detectan anomalías; la
   intención la determina el juez con evidencia adicional.
2. **No valida la narrativa "Operación Morrocoy".** El término existe
   (Venezuela 2012) pero no hay peer-review que lo tipifique como
   inteligencia cubana aplicada en Perú.
3. **No valida "Corvetto trabajó en Venezuela".** FALSO, desmentido por
   Ojo Público.
4. **No valida "digitadores venezolanos contratados por ONPE".** Sin
   contratos verificables.
5. **No valida "robo a Keiko 2021 por 44 votos".** OEA y UE descartaron
   fraude. Incluirlo debilita todo.

---

## Lo que se pide formalmente

Al Fiscal de la Nación, al JNE, y al JEE, bajo apercibimiento:

1. Explicación del finding A0 (42 actas que no reconcilian).
2. Data mesa-a-mesa en formato CSV/JSON (≈90,000 registros).
3. Clasificación de motivos de rechazo/impugnación del JEE (5,555 actas).
4. Logs de digitación con operador ID y timestamp.
5. Acta física digitalizada para comparar con sistema (muestra aleatoria).
6. Contratos y bitácoras del proveedor CALAG/Galaga.

---

## Verificación independiente

```bash
git clone https://github.com/jackthony/auditoria-eg2026.git
cd auditoria-eg2026
pip install -r requirements.txt
python src/process/build_dataset.py
python -m src.analysis.run_all
# Abre reports/findings.json para ver los 15 hallazgos con metadata completa
```

**Commit pre-registro hipótesis:** `413d6a1` (rama `main`).

---

## Invitación

Esta es una auditoría **ciudadana**, no partidaria. Si detectas errores
en el código, en los datos, o en la metodología, **abre un issue** en el
repositorio. Si eres investigador académico y quieres replicar, adelante
— la licencia CC-BY-4.0 te lo permite.

Si eres periodista y quieres citar, cita la versión congelada con su hash
SHA-256. Si eres funcionario de ONPE/JNE/JEE y quieres aportar data, se
publicará bajo el mismo estándar de reproducibilidad.

---

**Neuracode · Jack Aguilar**
Aporte ciudadano, sin retribución, sin afiliación política.
Propósito: fortalecer el control ciudadano sobre el proceso electoral.
