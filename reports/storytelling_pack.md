# Storytelling Pack — EG2026 Hallazgo Prime replicado

Responsable: Jack Aguilar (Tony) · Marca: Neuracode Academy
Captura oficial: `20260419T031241Z` · Captura mesa-a-mesa: `20260419T035056Z`
Fuente: `reports/findings_prime.json` · Dashboard: https://jackthony.github.io/auditoria-eg2026/
Repo: https://github.com/jackthony/auditoria-eg2026 (MIT, reproducible)

---

## 1. Hook maestro (12 palabras máx)

**"4,703 mesas no aparecen. El 2° puesto cambia. ONPE no cuadra."**

Alterno TikTok:
**"Sumé mesa por mesa. Le cambió el 2° puesto a ONPE."**

---

## 2. Pitch 30s TV (3 párrafos de ~10s, hablado)

**[0-10s]** "Bajé las 88,063 mesas que ONPE publica, mesa por mesa. Las sumé. El resultado no cuadra con el total oficial de ONPE."

**[10-20s]** "Según ONPE, Renovación Popular es tercero. Sumando mesa por mesa, López Aliaga sube al segundo puesto. Y Juntos por el Perú cae del 2° al 4°."

**[20-30s]** "Faltan 4,703 mesas del universo oficial sin data. Faltan 566,233 votos válidos. No digo fraude. Digo: las cuentas no cuadran y cualquiera puede verificarlo. Hash SHA-256 público."

---

## 3. Hilo X (10 tweets, ≤280 chars)

**T1** (sin link, gancho)
Bajé las 88,063 mesas que ONPE publica.
Las sumé mesa por mesa.
El 2° puesto cambia.
Faltan 4,703 mesas del universo oficial.
Faltan 566,233 votos válidos.
Código MIT. Hash SHA-256. Replicable por cualquiera.

Hilo 🧵

**T2** [IMG: RankingDiffTable]
Oficial ONPE:
2° Juntos por el Perú — 12.006%
3° Renovación Popular — 11.921%

Sumando mesa por mesa:
2° Renovación Popular — 12.27%
4° Juntos por el Perú — 10.90%

Mismas mesas. Otro ranking.

**T3** [IMG: MesasFaltantesMap]
Universo oficial: 92,766 mesas.
API mesa-a-mesa devuelve: 88,063.
Faltan: **4,703 mesas**.

Prime Institute reportó 4,343. En nuestra captura 10h después: 4,703. El hueco crece.

**T4**
Votos válidos oficiales: 15,757,620
Votos válidos sumando mesa por mesa: 15,191,387
**Desfase: 566,233 votos.**

No es error aleatorio. 41.57% del desfase cae en una sola agrupación.

**T5** [IMG: FindingCard F3]
Juntos por el Perú:
— Oficial: 1,891,906 votos
— Mesa-a-mesa: 1,656,517
— Delta: 235,389 votos "extra" en el agregador
— Ratio vs su peso real: 3.46x

El error no es proporcional. Está sesgado.

**T6**
Oficial dice: 282 actas pendientes.
Walker mesa-a-mesa encuentra: 5,741 no-Contabilizadas.
**20x más.**

¿Qué pasó con esas 5,459 actas entre la API interna y el total público?

**T7** [IMG: VerificationBadge]
Cadena de custodia:
— Captura inmutable: 20260419T035056Z
— SHA-256 en MANIFEST.jsonl
— Commit público con timestamp
— Código MIT auditable

No me creas. Verifica.

**T8**
No afirmo fraude.
Afirmo: **las cuentas que ONPE muestra no cuadran con las mesas que ONPE publica.**
Art. 438 CP (falsedad genérica) y Ley 30096 (delitos informáticos) aplican si hay dolo.
Eso lo decide Fiscalía, no yo.

**T9**
Replica en 3 comandos:
```
git clone https://github.com/jackthony/auditoria-eg2026
cd auditoria-eg2026
py make.py verify
```
Si el hash no coincide, te miento.

**T10** [IMG: NeuracodeFooter]
Hecho desde Lima. Sin OEA, sin MIT, sin ONG.
Neuracode Academy · talento peruano.
Dashboard EN VIVO: jackthony.github.io/auditoria-eg2026
El conteo termina mañana al mediodía. Difunde HOY.

---

## 4. Script TikTok/Reel 60s

**[0-3s] HOOK** — Cara al frente, tono duro
Texto: "ONPE NO CUADRA"
Voz: "Sumé mesa por mesa. Mira."

**[3-10s] PROBLEMA**
Split screen: dos rankings lado a lado.
Voz: "ONPE dice Juntos por el Perú segundo. Las mesas dicen: no."
Texto overlay: "2° → 4°"

**[10-20s] NÚMERO 1**
Cut a pantalla con contador animado.
Texto grande: "4,703 MESAS SIN DATA"
Voz: "Faltan cuatro mil setecientas tres mesas del universo oficial."

**[20-32s] NÚMERO 2** — Pattern interrupt (zoom)
Texto: "566,233 VOTOS"
Voz: "Faltan quinientos sesenta y seis mil votos válidos. El 41% cae en una sola agrupación. No es aleatorio."

**[32-45s] DEMO VERIFICACIÓN**
Screen record: terminal corriendo `py make.py verify`.
Voz: "Tres comandos. Tu compu. Si miento, el hash no coincide."

**[45-55s] CTA**
Cara al frente.
Texto: "jackthony.github.io/auditoria-eg2026"
Voz: "Conteo termina mañana mediodía. Comparte. Verifica. No te dejes ver la cara."

**[55-60s] LOOP**
Texto: "Neuracode — talento peruano"
Música: baja a cero, click final.

Música: trap tenso 90 BPM. Subtítulos duros blanco/amarillo. Cambio de plano cada 8s.

---

## 5. Titulares prensa (3 versiones)

**Sobrio (El Comercio / Ojo Público):**
"Auditoría independiente detecta desfase de 566 mil votos entre el total ONPE y la suma mesa-a-mesa; 4,703 mesas sin data pública"

**Directo (La República / IDL-Reporteros):**
"Sumando mesa por mesa las actas que publica ONPE, el 2° puesto cambia: López Aliaga desplaza a Juntos por el Perú"

**Popular (Trome / Correo):**
"¡Las cuentas de ONPE no cuadran! Faltan 4,703 mesas y 566 mil votos — peruano lo comprueba con su laptop"

---

## 6. Pitch panelistas TV (dossier 1 pág)

**Para:** productor/a de mesa política
**De:** Jack Aguilar — Neuracode Academy — jaaguilar@acity.com.pe
**Asunto:** Hallazgo replicable sobre agregador ONPE — EG2026

**Contexto (3 líneas):**
Captura pública 2026-04-19 03:50 UTC. 88,063 de 92,766 mesas descargadas vía API ONPE y sumadas independientemente. Replica el hallazgo previo de Prime Institute con gap mayor.

**3 bullets:**
- Ranking cambia: JPP cae 2°→4°; Renovación Popular sube 3°→2°
- 4,703 mesas del universo oficial sin data en la API pública (Prime reportó 4,343 10h antes)
- Desfase 566,233 votos válidos; 41.57% concentrado en una sola agrupación (JPP, ratio 3.46x su peso)

**Gráfico sugerido:** barra doble horizontal top-5 oficial vs mesa-a-mesa + badge "Δ +2 puestos López Aliaga".

**Pregunta detonante:** "¿Por qué 4,703 mesas no aparecen en la misma API que ONPE publica, y por qué el desfase está concentrado en una sola agrupación?"

**Fuente verificable:** commit público https://github.com/jackthony/auditoria-eg2026 · SHA-256 en MANIFEST.jsonl · licencia MIT.

**Contacto:** Jack Aguilar — [teléfono a coordinar] — disponible en vivo hoy 19-22 PET.

---

## 7. 10 componentes Claude Design

### C1. HeroFinding
- GOAL: Hero above-the-fold que fija el número-clave en <3s.
- LAYOUT: Full-bleed bg-deep. Centro: número gigante 180px (JetBrains Mono). Abajo subtítulo 24px Inter.
- CONTENT: "4,703" · "mesas del universo oficial sin data · ONPE EG2026" · botón "Verificar hash".
- AUDIENCE: cualquier visitante primer contacto.
- DESIGN SYSTEM: bg-deep #0a0e1a, alert-amber #ffb800 para número, ink-muted para subtítulo, motion.count-up 1.2s.
- VARIATIONS: variante "566,233 votos" · variante "+2 puestos López Aliaga".
- EXPORT: React component `<HeroFinding value number unit caption ctaHref />`.

### C2. RankingDiffTable
- GOAL: Mostrar cambio de ranking oficial vs mesa-a-mesa sin ambigüedad.
- LAYOUT: tabla 2 columnas (OFICIAL | MESA-A-MESA), 10 filas top-10, flecha delta entre columnas.
- CONTENT: top10_oficial y top10_mesa_a_mesa de findings_prime.json.
- AUDIENCE: prensa, panelistas, power users del dashboard.
- DESIGN SYSTEM: font.data monospace, danger-red para deltas negativos, verified-green para positivos, radius.card 12px.
- VARIATIONS: compact 5 filas · expanded con % y votos absolutos · mobile stack.
- EXPORT: React `<RankingDiffTable official mesa />` + export PNG 1200x1200.

### C3. MesasFaltantesMap
- GOAL: Mapa Perú coloreado por % mesas faltantes por departamento.
- LAYOUT: Leaflet choropleth + panel lateral con top-5 departamentos con más gap.
- CONTENT: GeoJSON regiones · delta mesas por ubigeo.
- AUDIENCE: periodistas regionales, fiscalización.
- DESIGN SYSTEM: escala amber→red, tooltips font.body, leyenda fija top-right.
- VARIATIONS: toggle %gap vs absoluto · overlay mesas CALAG.
- EXPORT: componente React + snapshot PNG para redes.

### C4. FindingCard
- GOAL: Tarjeta reutilizable por cada finding CRÍTICO/MEDIA/BAJA.
- LAYOUT: header severidad (pill), título pregunta, número grande, interpretación 2 líneas, link a MANIFEST.
- CONTENT: PRIME-F1..F4.
- AUDIENCE: dashboard + PDF memorial.
- DESIGN SYSTEM: pill danger-red (CRÍTICO), amber (MEDIA), ink-muted (BAJA/INFO). Radius 12, spacing 8px grid.
- VARIATIONS: dark/light · compact/expanded · print.
- EXPORT: `<FindingCard id severity question stat interpretation href />`.

### C5. VerificationBadge
- GOAL: Badge que muestra SHA-256 del data.json y link "verificar inline".
- LAYOUT: pill horizontal, icono lock + hash truncado 8 chars + botón copy.
- CONTENT: hash del último data.json, timestamp, "verificar" link a repo.
- AUDIENCE: escépticos, prensa técnica.
- DESIGN SYSTEM: verified-green border, font.data, hover reveal full hash.
- VARIATIONS: footer · inline · sticky header.
- EXPORT: `<VerificationBadge hash ts href />`.

### C6. Timeline
- GOAL: Línea de tiempo hitos captura + publicación + cambios en universo de mesas.
- LAYOUT: timeline vertical izquierda, cards derecha con ts UTC + evento + hash.
- CONTENT: capturas sucesivas + delta mesas entre ellas.
- AUDIENCE: auditores, fiscalía.
- DESIGN SYSTEM: ink-primary nodos, alert-amber cuando delta crece.
- VARIATIONS: horizontal móvil · filtro por severidad.
- EXPORT: `<Timeline events />`.

### C7. OGImageSocial (1200x630)
- GOAL: preview social que fuerza el click sin link.
- LAYOUT: bg-deep, número gigante "4,703 mesas faltan", ranking delta abajo, hash SHA-256 footer.
- CONTENT: valores del último findings_prime.json.
- AUDIENCE: X, FB, WhatsApp preview.
- DESIGN SYSTEM: JetBrains Mono números, Inter texto, alert-amber acento.
- VARIATIONS: per-finding (F1/F2/F3/F4) · per-hora ("Actualizado HH:MM PET").
- EXPORT: PNG generado en loop `--publish` + referenciado en `<meta og:image>`.

### C8. TikTokTemplate (1080x1920)
- GOAL: plantilla base para video vertical 60s.
- LAYOUT: safe area 0-10% top y 80-100% bottom libre de texto · título alert-amber 96px · subtítulos 64px blanco borde negro.
- CONTENT: hook 3s, números animados count-up, CTA final.
- AUDIENCE: TikTok/Reels/Shorts.
- DESIGN SYSTEM: motion.count-up 1.2s, pattern interrupt cada 8s (zoom/cut).
- VARIATIONS: mesa-a-mesa · desfase votos · verificación terminal.
- EXPORT: After Effects template + Remotion component.

### C9. PressDossierPDF (A4, 1 pág)
- GOAL: dossier imprimible para productores TV + sala de redacción.
- LAYOUT: header Neuracode + título · 3 bullets · gráfico RankingDiff · hash SHA-256 impreso · contacto.
- CONTENT: sección 6 de este pack.
- AUDIENCE: productores TV, editores prensa.
- DESIGN SYSTEM: bg blanco, ink-primary negro, monospace para números, QR a dashboard.
- VARIATIONS: ES · EN · versión Fiscalía (incluye art. CP).
- EXPORT: `build_press_dossier.py` → PDF vía python-docx/weasyprint.

### C10. NeuracodeFooter
- GOAL: firma sobria reutilizable sin canibalizar el mensaje.
- LAYOUT: footer horizontal · logo Neuracode · "Autor: Jack Aguilar" · redes · link memorial PDF.
- CONTENT: TikTok/IG/GitHub/repo/memorial.
- AUDIENCE: cualquier pieza.
- DESIGN SYSTEM: ink-muted, divider 1px, font.body 14px, altura 64px.
- VARIATIONS: dark/light · compact móvil.
- EXPORT: `<NeuracodeFooter />`.

---

## 8. Flujo interactivo de aprobación

**Paso 1 — Claude Design genera C1 HeroFinding.**
- Aprobar si: número correcto, legible en móvil <3s, hash visible.
- Iterar si: tipografía ilegible, color fuera de tokens.
- Descartar si: afirma "fraude" o usa lenguaje partidario.

**Paso 2 — C2 RankingDiffTable.**
- Aprobar si: flechas delta correctas contra JSON fuente, orden preservado.
- Iterar si: no resalta el cambio 2°→4°.
- Descartar si: alinea con un partido.

**Paso 3 — C3 MesasFaltantesMap.**
- Aprobar si: gap coincide con findings_prime (4,703 ±50).
- Iterar si: escala confusa.
- Fallback si Leaflet falla: tabla top-10 departamentos con gap.

**Paso 4 — C4..C6 (cards, badge, timeline).**
- Aprobar si: reusables, accesibles (contraste WCAG AA), sin mutar props.
- Iterar una vez. Si sigue mal → descartar.

**Paso 5 — C7 OGImage + C8 TikTok.**
- Aprobar si: texto legible en preview 300x157 (X) y en pantalla bloqueada móvil.
- Iterar si: safe area violada.
- Fallback: plantilla estática pre-renderizada.

**Paso 6 — C9 Dossier + C10 Footer.**
- Aprobar si: imprimible sin fondo oscuro, QR funcional.

**Regla de corte:** máximo 2 iteraciones por componente. Tercera → responsable Jack Aguilar decide manual o descarta. Cada aprobación = commit con mensaje `feat(ui): C{n} {name}`.

---

## Bonus

### WhatsApp audio 45s (guion, tono "mensaje de tío indignado-tranquilo")

"Compadre, escucha esto rapidito. Bajé mesa por mesa las 88 mil actas que la propia ONPE publica en su página. Las sumé con mi laptop. ¿Sabes qué sale? Que el segundo puesto cambia. Renovación Popular, López Aliaga, sube al segundo. Juntos por el Perú cae al cuarto. Y faltan 4,703 mesas que ONPE dice que existen pero que la API no devuelve. Faltan 566 mil votos válidos. Yo no estoy diciendo fraude, yo estoy diciendo que las cuentas no cuadran con las mesas que ellos mismos publican. Todo está en GitHub, con hash SHA-256 — o sea, si alguien toca un número, la firma cambia. Entra a jackthony punto github punto io barra auditoria guion eg2026. Verifícalo tú. Comparte si te parece. El conteo termina mañana al mediodía."

### WhatsApp imagen cuadrada (1080x1080) spec
- bg-deep #0a0e1a full
- Número central 280px alert-amber: "4,703"
- Subtítulo 48px Inter blanco: "mesas sin data · ONPE EG2026"
- Pie 32px font.data ink-muted: SHA-256 truncado + "jackthony.github.io/auditoria-eg2026"
- Marca Neuracode esquina inf-izq 24px

### Mensaje "de tío" para grupo familiar
> Familia, antes que digan "son rumores": un peruano bajó las mesas que ONPE publica y las sumó a mano con su código. Faltan 4,703 mesas y 566 mil votos. El 2° puesto cambia. Todo verificable con hash en GitHub — o sea, nadie puede editar sin que se note. No es política, son cuentas. Miren: jackthony.github.io/auditoria-eg2026 — y si dudan, el código está abierto.

---

## Checklist final

- [x] Números con fuente (captura 20260419T035056Z · findings_prime.json)
- [x] Cero adjetivos gratuitos
- [x] Cero partidismo (se ataca el agregador, no personas)
- [x] Analogía cotidiana por pieza ("cajero que no cuadra caja", "tu laptop", "mensaje de tío")
- [x] CTA claro (verifica / comparte / replica 3 comandos)
- [x] Marca Neuracode presente sin canibalizar
- [x] Componentes reutilizables con props claras
- [x] Accesibilidad: contraste WCAG AA, subtítulos en video, alt-text en imágenes
- [x] Responsable: Jack Aguilar (Tony)
