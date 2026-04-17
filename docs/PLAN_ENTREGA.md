# Plan de Entrega — 3 Vías Paralelas

**Fecha:** 2026-04-17
**Clasificación por vía:** A (confidencial cliente) · B (público técnico) · C (opinión personal)

---

## VÍA A — Entrega directa al equipo técnico RP y a RLA

**Destinatarios:** Equipo técnico designado + Rafael López Aliaga (vía jefe de campaña)
**Clasificación:** Confidencial — uso del cliente
**Marca:** Sin logo propio. Identificación como "Informe técnico independiente".

### Paquete A (pendrive cifrado + correo)

| Archivo | Propósito |
|---|---|
| `reports/Informe_Tecnico_RP_v2.pdf` | Informe ejecutivo |
| `docs/BRIEFING_FORENSE.md` | Handoff al perito que designen |
| `docs/AGENDA_REUNION_FORENSE.md` | Agenda reunión 60 min |
| Repo completo (`captures/`, `src/`, `data/`, `scripts/`) | Reproducibilidad |
| `MANIFEST.jsonl` con hashes SHA-256 | Cadena de custodia |

**Entrega:** pendrive cifrado AES-256 con contraseña compartida por canal separado.
**Acompañamiento:** carta de entrega de 1 página, firma del analista como ciudadano técnico.

---

## VÍA B — Publicación pública técnica

**Destinatarios:** opinión pública, prensa, academia, otros peritos
**Clasificación:** Público — licencia abierta
**Marca:** Ciudadano técnico independiente. **Sin calificativos políticos**.

### Paquete B

| Canal | Contenido | Estado |
|---|---|---|
| Repositorio GitHub público | Todo el repo con README público | Por configurar |
| Espejo IPFS / Archive.org | Snapshot inmutable | Por configurar |
| Dashboard web (live) | Monitor en tiempo real | Por construir |
| Comunicado web (Twitter/X + LinkedIn) | Texto neutro 280/600 caracteres | Por redactar |
| PDF público | Mismo PDF v2 pero sin referencias al cliente | Por generar |

### Por qué sin calificativos

- "Mafia caviar", "comunistas tramposos", "dictadura" = **destruye la credibilidad técnica**.
- Los hallazgos son fuertes **solos**: +5,392 margen vs 1.15M votos en disputa; tasa impugnación Extranjero 4× nacional; palanca P0 Lima+Extranjero = ~77k votos recuperables.
- Un informe neutro es **viral entre técnicos y prensa seria**. Uno partidarizado se queda en la burbuja.

### Reglas de lenguaje para la publicación

✅ SÍ usar:
- "Patrón temporal que amerita investigación"
- "Anomalía estadística al 1% de significancia"
- "Hallazgo que debe ser respondido por ONPE/JNE"
- "Universo en disputa = 1.15M votos, 195× el margen"

❌ NO usar:
- "Fraude", "robo", "mafia", "dictadura", "caviar", "comunista", "golpe"
- Atribución de intención a personas o partidos sin evidencia directa
- Afirmaciones absolutas cuando el test es no concluyente

---

## VÍA C — Opinión personal del analista (ciudadano)

**Destinatarios:** red personal del analista, simpatizantes
**Clasificación:** Público — opinión personal
**Marca:** Nombre del analista como ciudadano. **NUNCA** bajo el documento técnico.

- Cuenta personal de Twitter/X, LinkedIn, etc.
- Texto libre: agradecimientos, frustraciones, posición política, denuncia de afiliación indebida.
- Enlazar al paquete B como "data independiente disponible en [url]".

### Importante

La Vía C es tu derecho ciudadano. Pero va firmada **solo con tu nombre personal**, no con el del informe. Mezclar las vías A/B con C es un error operativo grave.

---

## Orden de ejecución (próximas 12 horas)

| Hora | Tarea | Responsable |
|---|---|---|
| 04:00 | Cerrar laptop, dormir 5h | Analista |
| 08:00 | Reunión handoff con forense | Analista + perito |
| 10:00 | Entrega Vía A (pendrive) | Analista + legal cliente |
| 11:00 | Publicación Vía B (GitHub) | Analista |
| 12:00 | Publicación Vía B (comunicado web) | Analista |
| 12:30 | Vía C opcional (posición personal) | Analista (ciudadano) |
| 13:00 | Denuncia afiliación indebida ante JNE-ROP | Analista |

---

## Pendientes de decisión del analista

1. Plataforma para dashboard live: GitHub Pages / Vercel / Netlify / servidor propio
2. ¿Incluir al "ingeniero que dateaba" como co-autor (con su permiso) o anónimo?
3. Seudónimo técnico o nombre real
4. Definición exacta de "teoría morrocoy" para no atribuir mal
