# Pitch Deck Hackathon Anthropic · auditoria-eg2026

> 10 slides · ~3 min presentación · audiencia jurado Anthropic (internacional)
> Autor: Jack Aguilar · Agentic AI Builder · Founder Neuracode · MIT · cero afiliación partidaria
> Ángulo: "1 humano + Claude Code auditó una elección entera en 8 días"
> Regla oro: jamás "fraude". Siempre "anomalía que ONPE debe explicar".

---

## Opening hook (≤10 palabras · 3 opciones)

- **V1 (número brutal):** "92,766 mesas. 8 días. 1 humano. Claude Code."
- **V2 (problema-solución):** "Auditar una elección cuesta 6 meses. Lo hice en 8 días."
- **V3 (callout Anthropic):** "Le di Claude Code a una elección. Esto pasó."

**Recomendado:** V1. Tres números y un stack. Audiencia técnica lo entiende en 2 segundos.

---

## Slide 1 · Portada

**Título:** auditoria-eg2026
**Subtitle:** One human + Claude Code audited 92,766 voting tables in 8 days
**Bullets (pantalla):**
- 3.79M actas analyzed
- 4 findings · p < 10⁻³⁰⁰
- $0 infra · MIT license

**Script hablado (20s):**
> "Soy Jack Aguilar, Agentic AI Builder, founder de Neuracode. Lo que van a ver no es una demo. Es una auditoría electoral real, en producción, corriendo sobre datos públicos del estado peruano. Una persona. Claude Code. Ocho días."

**Visual:** Fondo azul noche (#0a0e1a). Logo Neuracode top-left pequeño. Tres números en JetBrains Mono grande ámbar (#ffb800): `92,766` / `8` / `1`. Tagline en Inter blanco bajo los números. URL `auditoria.neuracode.dev` en footer pequeño.

**Transición:** Corte duro a slide 2. Sin animación. Urgencia.

---

## Slide 2 · Problem

**Título:** Electoral audit is expensive
**Subtitle:** The default assumption is "you need a team"

**Bullets:**
- Forensic statistics = PhDs + weeks
- Chain of custody = legal team
- Mesa-by-mesa scraping = infra $$
- Dashboard + reporting = designers
- Result: audits rarely happen in time

**Script hablado (25s):**
> "Auditar una elección hoy requiere: estadísticos forenses, abogados de cadena de custodia, ingenieros para scrapear acta por acta, diseñadores para el dashboard. Resultado: las auditorías llegan después del escrutinio, cuando ya no importan. La ventana crítica se cierra en días. Los equipos tardan meses."

**Visual:** Lista de roles a la izquierda (Statistician, Lawyer, Scraper, Designer, PM) con íconos. A la derecha un cronograma con barras semanales que suman "6 meses". Paleta gris-apagada para transmitir "viejo mundo".

**Transición:** Fade a slide 3 con cambio de paleta a alerta ámbar.

---

## Slide 3 · Insight

**Título:** 1 human + Claude Code = 5 analysts + 1 expert witness
**Subtitle:** Sub-agents specialized. Human in the loop. Reproducible.

**Bullets:**
- Haiku workers for QA (cheap)
- Sonnet for code gen + TDD
- Opus for forensic reasoning
- Human signs decisions
- Everything version-controlled

**Script hablado (25s):**
> "Claude Code cambia la ecuación. Sub-agents especializados: Haiku para QA de datos, Sonnet para código y TDD, Opus para razonamiento forense. El humano firma cada decisión, no tipea cada línea. Resultado: el trabajo de cinco analistas y un perito, hecho por una persona, en ocho días, auditable en GitHub."

**Visual:** Diagrama pipeline horizontal: `capture → build → analyze → report`. Debajo, fan-out con 4 agents chips (QA-Haiku, dev-Sonnet, forensic-Opus, review-Haiku). Flecha humana entra en cada nodo con ícono "approve". Fondo azul noche, agents en verde verificado (#10b981).

**Transición:** Corte a demo en vivo.

---

## Slide 4 · Live demo

**Título:** auditoria.neuracode.dev
**Subtitle:** 4 finding landings live · open data · SHA-256 verifiable

**Bullets:**
- H1 · Geographic imbalance · z=42.18
- H4 · 5% of tables = 20% of weight
- H9 · 11/11 tables impugned · p=4.83e-14
- H12 · Single table 90.43% winner

**Script hablado (30s):**
> "Entren ahora. auditoria punto neuracode punto dev. Cuatro landings, uno por finding. Cada número clickeable abre el hash SHA-256 en IPFS. El código abierto en GitHub. Si el jurado corre `py make.py analyze` en su laptop, obtiene exactamente los mismos números que yo. Reproducibilidad como contrato, no como promesa."

**Visual:** Screenshot del dashboard con las 4 landing cards visibles. Overlay con QR code que lleva a auditoria.neuracode.dev. Badge "LIVE" rojo (#ef4444) pulsante en esquina.

**Transición:** Cierra demo, abre stack técnico.

---

## Slide 5 · Stack

**Título:** Boring stack. Sharp choices.
**Subtitle:** Polars + DuckDB + IPFS + gh-pages

**Bullets:**
- Python 3.11 · Polars · DuckDB · PyArrow
- Pandas banned for >100k rows
- Cloudflare Worker proxy (peruvian IP needed)
- HuggingFace dataset public (3.79M rows)
- IPFS pins (Filebase + Pinata backup)
- gh-pages static dashboard · $0/mo

**Script hablado (20s):**
> "Stack aburrido a propósito. Polars y DuckDB porque Pandas muere con tres millones de filas. Cloudflare Worker porque ONPE bloquea datacenters fuera de Perú. HuggingFace para dataset público. IPFS para cadena de custodia inmutable. Todo en gh-pages. Infraestructura: cero dólares al mes."

**Visual:** Tabla de dos columnas. Izquierda: "Layer". Derecha: "Tool". Filas: Data / Polars+DuckDB · API / Cloudflare Worker · Dataset / HuggingFace · Custody / IPFS Filebase · Dashboard / gh-pages · Cost / $0. Números en verde.

**Transición:** Slide 6 hace zoom sobre Claude Code específicamente.

---

## Slide 6 · Claude Code in action

**Título:** Sub-agents did the heavy lifting
**Subtitle:** Specialized prompts · FinOps model routing · ECC workflow

**Bullets:**
- `storytelling-pe` · Opus · media narratives
- `data-engineer` · Haiku · QA at 99% cheaper
- `python-reviewer` · Haiku · every diff
- Custom commands for capture → analyze → report
- Chain of custody hooks on every commit

**Script hablado (30s):**
> "La magia no está en usar Claude, está en cómo. Sub-agents con prompts especializados. FinOps routing: Haiku para los obreros, Sonnet para orquestar, Opus sólo cuando realmente hay que razonar forense o legal. Hooks que validan cadena de custodia en cada commit. El workflow ECC cierra el loop: plan, TDD, review, verify, checkpoint. Claude Code no es un chatbot. Es un equipo."

**Visual:** Grid 2x3 con cards de agents. Cada card: nombre, modelo (badge color), 1 línea de función. Paleta: Haiku verde, Sonnet ámbar, Opus rojo crítico. Footer: "ECC loop: plan → tdd → review → verify → checkpoint".

**Transición:** Llega el hallazgo hero.

---

## Slide 7 · Hero finding · H4

**Título:** 5% of tables carry 20% of the weight
**Subtitle:** HALL-0420-H4 · z=698 · p ≈ 0 · Cohen h = 0.73

**Bullets:**
- Normal tables (88,063): JPP 10.91%
- Special 900k+ tables (4,703): JPP 41.65%
- Ratio 3.82× · IC95 [29.46pp, 30.79pp]
- Bootstrap B=10,000 (Efron-Tibshirani)
- Per-departamento 2.6× to 4.2× (not regional artifact)

**Script hablado (30s):**
> "El hallazgo principal. En las mesas normales, un partido sacó diez punto noventa y uno por ciento. En cuatro mil setecientas mesas especiales, cuarenta y uno punto sesenta y cinco. Tres punto ocho veces más. Z-score de seiscientos noventa y ocho. La probabilidad de que esto sea azar es literalmente cero en la precisión de un float. No digo fraude. Digo: ONPE, explícate."

**Visual:** Dos barras horizontales grandes. Barra 1: "Normal 88,063" ámbar al 10.91%. Barra 2: "Special 900k+ 4,703" rojo crítico al 41.65%. Debajo, en mono: `z=698 · p≈0 · Cohen h=0.73 · ratio 3.82×`. Al costado, mini-gráfico con 8 deptos y sus ratios (todos >2.6×).

**Transición:** Slide 8 muestra por qué esto es creíble.

---

## Slide 8 · Chain of custody · 4 levels

**Título:** If you can verify the hash, you can trust the number
**Subtitle:** Every capture immutable · SHA-256 · IPFS · HuggingFace

**Bullets:**
- Level 1 · Local `captures/{ts}/` · MANIFEST.jsonl
- Level 2 · GitHub main + signed commits
- Level 3 · HuggingFace `Neuracode/onpe-eg2026-mesa-a-mesa`
- Level 4 · IPFS Filebase + Pinata backup
- CID parquet: `QmVCan4...YX5L` (3.79M rows)

**Script hablado (25s):**
> "Cuatro niveles de custodia. Captura local con MANIFEST SHA-256. Commit firmado en GitHub. Parquet público en HuggingFace. Pins inmutables en IPFS con Filebase como primario y Pinata como backup. Cualquiera, en cualquier país, puede bajar el CID y verificar que el archivo que analicé es el mismo que ustedes están viendo ahora."

**Visual:** Pirámide invertida o escalera con 4 niveles. Cada nivel con ícono, tecnología, y badge verde "SHA-256 verified". CID parquet en mono en el footer, seleccionable. Un segundo elemento: botón "Copy CID" animado.

**Transición:** Slide 9 abre el código.

---

## Slide 9 · Open everything

**Título:** Clone. Run. Get the same numbers.
**Subtitle:** MIT license · public data · zero gatekeeping

**Bullets:**
- `rtk git clone github.com/...`
- `rtk pip install -r requirements.txt`
- `py make.py verify && py make.py analyze`
- Same z=698. Same p. Same findings.
- Data belongs to citizens, not to auditors.

**Script hablado (25s):**
> "Esto es lo que separa un informe de una auditoría. Si no puedo darte el código y los datos para que repliques, no es auditoría, es opinión. MIT license. Datos públicos ONPE. Tres comandos. Los mismos números. Nadie me pide permiso, nadie me cree por autoridad. El repo se cree solo."

**Visual:** Terminal mockup negro con los tres comandos en verde. Al costado, logo MIT + logo GitHub + logo HuggingFace. Frase debajo: "Data belongs to citizens" en ámbar.

**Transición:** Cierre.

---

## Slide 10 · Close

**Título:** Audit your own data with Claude Code
**Subtitle:** Electoral data today. Your vertical tomorrow.

**Bullets:**
- Healthcare claims · logistics · public procurement
- Same pattern: scrape → custody → test → publish
- Sub-agents scale the human, not the cost
- Neuracode builds agentic products for LATAM SMBs

**Script hablado (25s):**
> "No termino pidiendo gracias. Termino con un reto. Esto funcionó con datos electorales. Funciona con reclamos de seguros, con contratos públicos, con cadenas logísticas. El patrón se repite: capturar, custodiar, testear, publicar. Claude Code no escala la nómina, escala al humano. Si tienes datos públicos que nadie está mirando, clónalo. Úsalo. Audita. Gracias."

**Visual:** Call-to-action central grande: "Clone it. Run it. Ship it." en JetBrains Mono. Debajo, URL `github.com/jackdeneuracode/auditoria-eg2026` + `auditoria.neuracode.dev`. Footer branded: "Jack Aguilar · Agentic AI Builder · Neuracode · MIT · SHA-256 · neuracode.academy". Logo Anthropic discreto en esquina con "Built with [Claude Code](https://claude.ai/referral/Kj5b88VLag)".

**Transición:** Fin. Pausa de 2 segundos antes de abrir Q&A.

---

## Closing CTA (específico, no genérico)

**Recomendado:**
> "Clone it. Run `py make.py analyze`. If your numbers match mine, the audit holds. If they don't, open an issue. That's accountability at version-control speed."

**Backup corto:**
> "Audit your own data. Same 3 commands. Same reproducibility. Your move."

---

## FAQ anti-ataque (5 objeciones + rebuttal ≤20 palabras)

**Q1 · "This is political."**
> A: The arithmetic has no ideology. Code is MIT. Data is ONPE public. Run it yourself. No party affiliation.

**Q2 · "You're not a certified forensic auditor."**
> A: Correct. I'm an Agentic AI Builder. The methods are peer-reviewed (Newcombe 1998, Cohen 1988, Efron 1993). Cite the paper, not the person.

**Q3 · "ONPE official numbers are the valid ones."**
> A: I aggregate the same data ONPE publishes. If theirs are valid, mine are. The gap between them is the finding.

**Q4 · "Claude Code hallucinates. Can you trust the output?"**
> A: Human signs every commit. Tests run on every change. Chain of custody is SHA-256. The agent drafts, the human approves. No hallucination survives `pytest`.

**Q5 · "Why didn't you go to ONPE first?"**
> A: Code is public since day one. ONPE can read the repo. Transparency is not a courtesy, it's the method.

**Q6 · "Benford's law is pseudoscience."** (bonus, si alguien lo dice)
> A: Agreed in part (Deckert et al. 2011). That's why Benford isn't used as sole evidence. H4 uses z-test and bootstrap, not Benford.

**Q7 · "How do we know the 900k+ tables aren't just military or foreign?"** (técnico)
> A: Per-departamento analysis shows ratios 2.6× to 4.2× across 8 regions. If it were a single bucket, the effect wouldn't distribute geographically.

---

## Notas de presentación (para Jack)

- **Tiempo total:** ~3 min si hablas firme. Practica slide 4 (demo) en vivo: abre el dashboard real, no screenshot.
- **Slide 7 (hero)** es donde debes subir la voz y bajar el ritmo. El número 698 vale más pronunciado lento.
- **Slide 9:** ten terminal abierta. Si el jurado pregunta, corre `py make.py verify` en vivo. Es la jugada ganadora.
- **No uses la palabra "fraude"** en toda la presentación. Ni una vez. Regla oro del proyecto.
- **Evita títulos inflados:** no "forensic auditor", no "cyber expert". Eres "Agentic AI Builder · Founder Neuracode · en camino a CCA".
- **Claude Code como infraestructura no como chatbot:** ese es el diferenciador para el jurado Anthropic.

---

## Checklist pre-pitch (día del evento)

- [ ] Dashboard `auditoria.neuracode.dev` responde en <2s
- [ ] Repo GitHub público y `rtk git log` limpio
- [ ] Terminal con `py make.py verify` precargado
- [ ] Screenshot backup de demo por si falla wifi
- [ ] CID IPFS copiado al portapapeles (para Q&A)
- [ ] Headline LinkedIn actualizado: "Agentic AI Builder · Claude Code · Founder Neuracode"
- [ ] Cronometrar ensayo 3 veces. Meta: 2:50 - 3:05.

---

**Firma:**
Jack Aguilar · Agentic AI Builder · Founder Neuracode
MIT License · SHA-256 verified · Built with Claude Code
`auditoria.neuracode.dev` · `neuracode.academy`
