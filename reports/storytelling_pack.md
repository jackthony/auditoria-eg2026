# Storytelling Pack — EG2026 · Hero H4 · v2-92k

**Fecha:** 2026-04-20 · **Autor:** Jack Aguilar (Tony) · **Marca:** Neuracode Academy
**Universo:** 92,766 mesas (88,063 normales + 4,703 especiales 900k+)
**Regla oro:** jamás "fraude". Siempre "anomalía que ONPE debe explicar".

**CIDs IPFS (cadena custodia nivel 4):**
- `CID-MANIFEST` = `QmSxcH2NQ22PTHDyQR6r4nkYHWvT71mAZqAh26mvpPynwS` (22.7 MB SHA-256)
- `CID-PARQUET` = `QmVCan4WeK2sq8LipRfP7PEz6QQV5kttFgwkhi6q62YX5L` (3.79M actas)
- `CID-FINDINGS` = `QmUopL1zep7UkJACBUVpBVKdAU6zcsPqwgbUwY97jLwPPp` (H1-H4 JSON)

Prefix gateway: `https://ipfs.filebase.io/ipfs/<CID>`.

---

## 1. Hook viral (3s) — 3 versiones

**V1 (número brutal):**
> 4,703 mesas. Un partido sacó 4× más votos ahí. Por azar: 1 entre billones.

**V2 (analogía bolsillo):**
> El 5% de las mesas pesa como el 20%. ¿Casualidad? z=698.

**V3 (callout directo):**
> Si votaste en Perú, mira esto: mesa 900k+ = 41.65%. Mesa normal = 10.91%.

Fuente: `HALL-0420-H4` · `CID-FINDINGS`.

---

## 2. Hilo X — 10 tweets, 280 chars c/u

**Tweet 1 (hook, sin link):**
> 4,703 mesas especiales (5% del país).
> Un partido sacó 41.65% ahí.
> En las otras 88,063 mesas: 10.91%.
> Ratio 3.82×. z=698. Azar ≈ 0.
> Esto no es opinión. Es aritmética.
> Hilo 🧵

**Tweet 2 (el problema):**
> Las mesas 900k+ son mesas regulares ONPE, distribuidas geográficamente.
> No son solo militares ni solo extranjero.
> Sin embargo, concentran 4× el voto de un partido específico.
> Finding ID: HALL-0420-H4.

**Tweet 3 (el test):**
> Método: z-test 2 proporciones (Newcombe 1998) + Cohen h + bootstrap Efron-Tibshirani B=10,000.
> Resultado: z=698, Cohen h=0.73 (efecto grande), IC95 diff [29.46%, 30.79%].
> Cero Benford. Aritmética pura.

**Tweet 4 (evidencia verificable):**
> Findings consolidados H1-H4 en IPFS (imposible de borrar):
> CID: QmUopL1zep7UkJACBUVpBVKdAU6zcsPqwgbUwY97jLwPPp
> Gateway: ipfs.filebase.io/ipfs/QmUopL1zep7UkJACBUVpBVKdAU6zcsPqwgbUwY97jLwPPp
> [IMG: tabla 41.65% vs 10.91%]

**Tweet 5 (dataset completo):**
> 3,793,246 actas auditables en parquet.
> SHA-256 firmado, subido a IPFS Filebase.
> CID: QmVCan4WeK2sq8LipRfP7PEz6QQV5kttFgwkhi6q62YX5L
> Bájalo, córrelo, verifica tú mismo.

**Tweet 6 (manifest custodia):**
> MANIFEST.jsonl de 92,766 mesas con SHA-256 por archivo.
> CID: QmSxcH2NQ22PTHDyQR6r4nkYHWvT71mAZqAh26mvpPynwS
> Cada captura inmutable. Commits GitHub firmados.
> Tag: v2-mesas-900k · Commit: 26b4cde.

**Tweet 7 (soporte H1):**
> Soporte H1 (CRÍTICO): tasa impugnación no es homogénea.
> Extranjero 26.27% (z=42). Loreto 14.87%. Ucayali 12.02%.
> Piso: Arequipa 1.83%. Global: 6.16%.
> Finding ID: HALL-0420-H1.

**Tweet 8 (soporte H2+H3):**
> H2 (MEDIA): FUERZA POPULAR +2.07pp en locales alta-imp. JPP +0.88pp.
> H3 (MEDIA): 5,304 mesas (5.72%) outliers nulos/blancos. 4 mesas Loreto 900k+ con >90% blancos.
> Finding IDs: HALL-0420-H2 y H3.

**Tweet 9 (anti-ataque):**
> "Es casualidad" → z=698, IC95 [29.5%, 30.8%]. Azar ≈ 0.
> "Eres opositor" → cero afiliación. Corre `rtk pytest` tú mismo.
> "Es Benford" → no usé Benford.
> Anomalía ≠ fraude. Pido auditoría.

**Tweet 10 (CTA):**
> Dashboard: auditoria.neuracode.dev
> Repo: github.com/jackthony/auditoria-eg2026
> Dataset HF: Neuracode/onpe-eg2026-mesa-a-mesa
> ONPE: explica H4.
> Firma: Jack Aguilar · Neuracode Academy.

---

## 3. TikTok 60s — guion con timestamps

**Voz:** grave, rápida, indignada controlada. **Música:** trap oscuro low-bass, silencio dramático en 0:15 y 0:40.

```
[0-3s]  HOOK VISUAL
        Cara cámara. Texto pantalla grande amber:
        "4,703 MESAS. 41.65% vs 10.91%."
        Voz: "Esto lo tienes que ver."

[3-15s] PROBLEMA
        Corte a pantalla: tabla animada número crece de 0.
        Texto: "En 4,703 mesas especiales un partido sacó 4× más votos que en las otras 88,063."
        Voz: "El 5% de las mesas del país pesa como si fuera el 20%."
        [PAUSA 0.5s silencio]

[15-40s] EVIDENCIA
        Pantalla: código corriendo (pytest verde).
        Texto overlay: "z = 698 · Cohen h = 0.73 · IC95 [29.5%, 30.8%]"
        Voz: "Probabilidad por azar: uno entre billones."
        Corte: captura IPFS gateway abriendo findings JSON.
        Texto: "CID público. Imposible de borrar."
        Mostrar CID: QmUopL1zep...jLwPPp

[40-55s] CONTEXTO
        Cara cámara, tono bajado.
        Texto: "NO digo fraude. Digo anomalía."
        Voz: "ONPE tiene que explicar por qué 4,703 mesas se comportan distinto.
              La aritmética no milita."

[55-60s] CTA
        Pantalla final negra. Logo Neuracode amber.
        Texto grande: "auditoria.neuracode.dev"
        Voz: "Verifica tú mismo. Comparte si no quieres que te vean la cara."
```

**Hashtags:** #EleccionesPe2026 #ONPE #AuditoriaCiudadana #Neuracode #IPFS
**Pattern interrupt:** corte cada 8s (cara → pantalla → gráfico → cara).
**Subtítulos:** burn-in grandes, amber sobre bg-deep.

---

## 4. Instagram Reel 45s — variante IG

**Portada estática (obligatoria):** fondo `#0a0e1a`, número `41.65%` amber gigante, abajo `vs 10.91%`, logo Neuracode top-left.

```
[0-3s]  HOOK
        Portada animada: número 41.65% cuenta de 0.
        Subtítulo grande: "Un partido en 4,703 mesas."
        Sin audio necesario (80% IG ve muted).

[3-12s] CONTRASTE
        Split screen:
        Izq: "Mesas normales (88,063) → 10.91%"
        Der: "Mesas 900k+ (4,703)  → 41.65%"
        Flecha amber: "3.82× más"
        Voz (si activa): "Mismo país. Mismo día. Distinto resultado."

[12-30s] MÉTODO
        Pantalla: fórmula z-test 2 proporciones.
        Overlay números: z=698, Cohen h=0.73.
        Texto: "No es Benford. Es z-test publicado 1998."
        CID IPFS visible 2s: QmUopL1zep7UkJACBUVpBVKdAU6zcsPqwgbUwY97jLwPPp

[30-40s] REGLA ORO
        Cara cámara.
        Texto: "No afirmo fraude. Afirmo anomalía."
        "ONPE: explica H4."

[40-45s] CTA (adelantado respecto TikTok)
        Logo Neuracode.
        "Link en bio: auditoria.neuracode.dev"
        "Dataset IPFS verificable."
```

**CTA en 0:40 (no al final):** 80% no llega al final.
**Subtítulos:** burn-in siempre, Inter bold 48pt.

---

## 5. Titulares prensa — 5 medios con SCQA

### Ojo Público (sobrio, SCQA completo)
> **S:** En 88,063 mesas un partido obtuvo 10.91% del voto.
> **C:** En 4,703 mesas especiales obtuvo 41.65%.
> **Q:** ¿Qué distingue a ese 5% del universo electoral?
> **A:** z=698, IC95 [29.5%, 30.8%]. Auditoría Neuracode publica dataset en IPFS.
> **Titular:** "Auditoría técnica detecta asimetría 3.82× en 4,703 mesas especiales ONPE"
> Fuente: `CID-FINDINGS` · finding ID `HALL-0420-H4`.

### IDL-Reporteros (directo, investigativo)
> **Titular:** "Aritmética contra ONPE: una auditoría ciudadana encuentra brecha estadística de 31 puntos en mesas especiales"
> **Lead:** Un perito técnico privado, Jack Aguilar (Neuracode), publicó dataset de 3,793,246 actas en IPFS. Los números no cuadran con la narrativa oficial: ratio 3.82× concentrado en 4,703 mesas 900k+.
> CID verificable: `QmUopL1zep7UkJACBUVpBVKdAU6zcsPqwgbUwY97jLwPPp`.

### La República (acusatorio moderado)
> **Titular:** "ONPE debe explicar: ¿por qué en 4,703 mesas un partido cuadruplica su voto nacional?"
> **Lead:** 41.65% vs 10.91%. Z-score 698. Auditoría Neuracode Academy la reproducible vía `rtk pytest`.

### El Comercio (institucional, factual)
> **Titular:** "Auditoría independiente identifica anomalía estadística en 5% de mesas electorales"
> **Lead:** El análisis aplica z-test 2 proporciones (Newcombe 1998) sobre universo de 92,766 mesas. Findings publicados en cadena custodia IPFS con SHA-256 por archivo. Commit GitHub firmado `26b4cde`, tag `v2-mesas-900k`.

### Convoca (técnico-investigativo)
> **Titular:** "3.79 millones de actas auditables en IPFS: el dataset que Neuracode publica contra la opacidad ONPE"
> **Lead:** Parquet firmado SHA-256 `02fa363e...dbd1`, CID `QmVCan4WeK2sq8...YX5L`. Metodología open-source, reproducible, citas académicas (Newcombe 1998, Cohen 1988, Efron-Tibshirani 1993).

---

## 6. Pitch TV 30s — guion visual + narrador

**Analogía aprobada:** "cajero que cuadra en 88,063 cuentas pero en 4,703 cobra 4× de más".

```
[0-10s]  NARRADOR (voz firme, ritmo rápido)
         "Imagínate un cajero que atiende 92 mil cuentas.
          En 88 mil, cobra normal.
          En 4 mil 700, cobra 4 veces más.
          ¿Casualidad?"
         VISUAL: animación cajero + tickets, número 3.82× crece.

[10-20s] NARRADOR (ritmo pausado, serio)
         "Eso es lo que pasa con un partido en las elecciones.
          En 4,703 mesas especiales: 41.65%.
          En el resto del país: 10.91%.
          La probabilidad que sea azar: uno entre billones."
         VISUAL: split tabla ONPE oficial vs auditoría, números amber
                 sobre bg-deep. CID IPFS en esquina: Qm...LwPPp.

[20-30s] NARRADOR (cierre, directivo)
         "No decimos fraude. Decimos: ONPE tiene que explicarlo.
          Los datos están en IPFS, imposibles de borrar.
          Audítalo tú mismo en auditoria.neuracode.dev."
         VISUAL: logo Neuracode Academy + URL grande +
                 hash SHA-256 impreso (señal de verificable).
```

**Tarjeta sobreimpresa permanente:** `HALL-0420-H4 · z=698 · IC95 [29.5%, 30.8%]`.
**CTA:** `auditoria.neuracode.dev`.

---

## 7. Dossier panelistas — 1 página A4

```
════════════════════════════════════════════════════════════
  NEURACODE ACADEMY · AUDITORÍA EG2026 · 2026-04-20
  Contacto: Jack Aguilar (Tony) · @JackTonyAC
  auditoria.neuracode.dev
════════════════════════════════════════════════════════════

CONTEXTO (1 párrafo para productor):
Jack Aguilar, CEO Neuracode, publicó auditoría técnica
open-source del escrutinio ONPE EG2026. Dataset de 3.79M
actas en IPFS con SHA-256 por archivo. Cero afiliación
partidaria. Metodología revisable vía `rtk pytest`.

═══ HERO: H4 (CRÍTICO) ═══
• JPP en 4,703 mesas especiales 900k+:  41.65%
• JPP en 88,063 mesas normales:         10.91%
• Ratio:                                3.82×
• z-stat (Newcombe 1998):               698
• Cohen h:                              0.73 (grande)
• Bootstrap IC95 diff:                  [29.46%, 30.79%]
• Finding ID: HALL-0420-H4

═══ SOPORTE ═══
H1 (CRÍTICO) · Sesgo geográfico impugnadas
  Extranjero 26.27% (z=42) · Loreto 14.87% · Ucayali 12.02%
  Piso: Arequipa 1.83%. Global: 6.16%.

H2 (MEDIA) · Partidos en locales alta-imp
  FUERZA POPULAR +2.07pp · JPP +0.88pp
  Bajan: BUEN GOBIERNO -1.62pp

H3 (MEDIA) · Outliers nulos/blancos
  5,304 mesas (5.72%) outliers
  4 mesas Loreto 900k+ con >90% blancos

═══ GRÁFICO SUGERIDO ═══
Bar chart 2 barras:
  [Mesas normales 88,063] → 10.91% (amber claro)
  [Mesas 900k+  4,703]   → 41.65% (danger red)
Eje Y: % JPP. Barras con IC95 error bars.

═══ PREGUNTA DETONANTE (para invitado político) ═══
"¿Cómo explica ONPE que 4,703 mesas (5% del país)
 concentren 3.82× el voto de un partido?
 Si no es azar, ¿qué es?"

═══ CADENA CUSTODIA IPFS (4 niveles) ═══
MANIFEST  · CID: QmSxcH2NQ22PTHDyQR6r4nkYHWvT71mAZqAh26mvpPynwS
PARQUET   · CID: QmVCan4WeK2sq8LipRfP7PEz6QQV5kttFgwkhi6q62YX5L
FINDINGS  · CID: QmUopL1zep7UkJACBUVpBVKdAU6zcsPqwgbUwY97jLwPPp
Gateway: https://ipfs.filebase.io/ipfs/<CID>
GitHub tag: v2-mesas-900k · Commit: 26b4cde

═══ MÉTODO (cita académica) ═══
• Newcombe (1998). Statistics in Medicine.
• Cohen (1988). Statistical Power Analysis.
• Efron & Tibshirani (1993). Intro to the Bootstrap.

FIRMA: Jack Aguilar · Perito técnico IA · Neuracode Academy
Métricas open-source · SHA-256 · neuracode.academy
════════════════════════════════════════════════════════════
```

**Objetivo métrico:** 3 panelistas TV distintos citando al aire algún CID IPFS → viral threshold alcanzado.

---

## 8. 10 componentes Claude Design — specs técnicas

**Design tokens fijos (referenciar por nombre):**
`bg-deep #0a0e1a` · `alert-amber #ffb800` · `danger-red #ef4444` · `verified-green #10b981` · `ink-primary #f5f7fa` · `fonts.data JetBrains Mono` · `fonts.body Inter` · `radius.card 12px` · `spacing.grid 8px`.

---

### C1 · HeroFindingH4

```
GOAL:
  Mostrar número hero 41.65% vs 10.91% con contador animado
  0→valor, comunicar anomalía en 3s.

LAYOUT:
  Desktop 1920x1080. Hero full-viewport.
  Grid 12 col. Número centrado, contraste gigante.
  Subtítulo debajo, CID IPFS footer.

CONTENT:
  Título: "4,703 mesas. Un partido. 3.82× más votos."
  Big number izq: "41.65%" label "Mesas 900k+ (n=4,703)"
  Big number der: "10.91%" label "Mesas normales (n=88,063)"
  Metric strip: z=698 · Cohen h=0.73 · IC95 [29.46%, 30.79%]
  Footer: "HALL-0420-H4 · CID {{CID-FINDINGS}}"

AUDIENCE:
  Peruano promedio móvil, lectura 3s.

DESIGN SYSTEM:
  bg-deep · alert-amber en 41.65% · ink-muted en 10.91%
  fonts.data para números · fonts.body para labels
  motion.count-up 1.2s ease-out

EXPORT:
  Handoff a Claude Code → web/components/hero-finding-h4.html
```

---

### C2 · RankingDiffTable

```
GOAL:
  Tabla comparativa partidos normales vs 900k+ con deltas
  coloreados, ordenable.

LAYOUT:
  Desktop 1200px ancho. 5 columnas:
  [Partido] [% normales] [% 900k+] [Δ pp] [Ratio]
  Fila JPP destacada danger-red.

CONTENT:
  Filas literales (H2 + H4):
    JPP            10.91%  41.65%  +30.74pp  3.82×
    FUERZA POP.    {{fp_norm}}  {{fp_900}}  +2.07pp  {{fp_ratio}}
    BUEN GOBIERNO  {{bg_norm}}  {{bg_900}}  -1.62pp  {{bg_ratio}}
  Badge SHA-256 arriba derecha clickeable.

AUDIENCE:
  Panelista TV / periodista leyendo en dossier.

DESIGN SYSTEM:
  bg-deep · fonts.data tabla · verified-green deltas positivos
  danger-red deltas negativos · radius.card 12px

EXPORT:
  web/components/ranking-diff-table.html
```

---

### C3 · MesasFaltantesMap (impugnadas H1)

```
GOAL:
  Choropleth Perú 26 deptos + Extranjero, color proporcional
  a tasa impugnación.

LAYOUT:
  Desktop 1080x1080 cuadrado (share-friendly).
  Mapa SVG geoJSON Perú INEI 2020 + caja Extranjero separada.
  Leyenda bottom: escala 0%-30%.

CONTENT:
  Datos H1 por depto:
    Extranjero 26.27% (z=42) → danger-red saturado
    Loreto 14.87% → naranja
    Ucayali 12.02% → naranja claro
    Arequipa 1.83% → verified-green
    Resto: interpolar.
  Tooltip hover: "depto · tasa · z-score · n_mesas"

AUDIENCE:
  Share Twitter/WhatsApp, panelista TV.

DESIGN SYSTEM:
  bg-deep · escala color alert-amber → danger-red
  fonts.data tooltip · motion hover-lift

EXPORT:
  web/components/mesas-impugnadas-map.html
```

---

### C4 · FindingCard (reutilizable H1-H4)

```
GOAL:
  Card componente repetible por finding con severidad,
  stat, método, fuente.

LAYOUT:
  320x400px card. Grid interno 3 filas:
  [Header severity + ID] [Body stat + interpretation] [Footer CID + source]

CONTENT:
  Props inyectables:
    {{severity}} (CRÍTICO|MEDIA) → color badge
    {{id}} (HALL-0420-H1..H4)
    {{test}} descripción
    {{statistic}} + {{threshold}}
    {{interpretation}} (texto ≤120 chars)
    {{cid}} IPFS verificable

AUDIENCE:
  Dashboard visitante, 4 cards lado a lado.

DESIGN SYSTEM:
  bg-deep card · danger-red badge CRÍTICO · alert-amber MEDIA
  radius.card 12px · shadow.lift
  fonts.data stat · fonts.body interpretation

VARIATIONS:
  2 opciones: compacta vs expandida click-to-detail.

EXPORT:
  web/components/finding-card.html
```

---

### C5 · VerificationBadgeIPFS

```
GOAL:
  Badge clickeable que muestra CID IPFS truncado y
  abre gateway en nueva pestaña.

LAYOUT:
  Inline pill 240x32px. Icono lock izquierda + texto
  "IPFS · Qm…LwPPp" + icono external right.

CONTENT:
  Props:
    {{cid}} full CID
    {{label}} (MANIFEST | PARQUET | FINDINGS)
  Tooltip hover muestra CID completo + SHA-256.
  onClick → https://ipfs.filebase.io/ipfs/{{cid}}

AUDIENCE:
  Usuario técnico, periodista verificando.

DESIGN SYSTEM:
  bg-deep fill · verified-green border · fonts.data CID
  radius.card 12px · cursor pointer

EXPORT:
  web/components/verification-badge-ipfs.html
```

---

### C6 · TimelineCaptures

```
GOAL:
  Serie temporal de capturas ONPE con scrubber interactivo,
  mostrar evolución tasa JPP 900k+.

LAYOUT:
  Full-width 1200x400px. Eje X tiempo UTC.
  Eje Y % JPP. Línea dual: 900k+ vs normales.
  Scrubber inferior con timestamps.

CONTENT:
  Puntos: capturas desde 20260419T... hasta 20260420T074202Z.
  Anotación evento: "Fix walker → +4,703 mesas 900k+"
  Tooltip: ts_utc + % JPP 900k+ + % JPP normales + delta.

AUDIENCE:
  Investigador, panelista TV mostrando evolución.

DESIGN SYSTEM:
  bg-deep · línea danger-red 900k+ · línea ink-muted normales
  fonts.data ejes · motion smooth 300ms

EXPORT:
  web/components/timeline-captures.html
```

---

### C7 · OGImageSocial (1200x630)

```
GOAL:
  Imagen Open Graph para Twitter/WhatsApp/LinkedIn,
  hook + número + CID legible.

LAYOUT:
  1200x630 exact. Grid 2 col:
  Izq: título + número hero.
  Der: logo Neuracode + CID IPFS truncado.

CONTENT:
  Título: "4,703 mesas. 41.65% vs 10.91%."
  Subtítulo: "Anomalía z=698 · ONPE debe explicar."
  Footer centrado: "auditoria.neuracode.dev · CID Qm…LwPPp"
  Logo top-left.

AUDIENCE:
  Preview link al compartir (WhatsApp dominante PE).

DESIGN SYSTEM:
  bg-deep · 41.65% en alert-amber 240pt · fonts.data
  Logo Neuracode 64px top-left

EXPORT:
  web/components/og-image-h4.html → render PNG via headless
```

---

### C8 · TikTokTemplate (frames estáticos)

```
GOAL:
  Set de 5 frames exportables para video TikTok 60s,
  edición posterior en CapCut.

LAYOUT:
  1080x1920 vertical por frame. Secuencia:
  F1 (0-3s) hook · F2 (3-15s) contraste · F3 (15-40s) método
  F4 (40-55s) regla oro · F5 (55-60s) CTA.

CONTENT:
  F1: "4,703 MESAS" alert-amber gigante + "41.65% vs 10.91%"
  F2: Split screen números con barras animadas
  F3: Pantalla código + z=698 overlay + CID IPFS 2s
  F4: Cara-space holder (filmar) + texto "No es fraude. Es anomalía."
  F5: Logo + "auditoria.neuracode.dev"

AUDIENCE:
  Editor video (Tony o contratista).

DESIGN SYSTEM:
  bg-deep · alert-amber hero · fonts.data overlays
  Safe-zones TikTok UI (top 200px, bottom 300px sin texto crítico)

EXPORT:
  web/components/tiktok-frames-h4.html + zip PNG 1080x1920
```

---

### C9 · PressDossierPDF (A4 imprimible)

```
GOAL:
  1 página A4 para enviar a productores TV, periodistas.
  PDF descargable con hallazgos, contactos, CIDs.

LAYOUT:
  A4 portrait 210x297mm. Márgenes 15mm.
  Header banda Neuracode 20mm.
  Body 3 secciones: Hero H4 + Soporte H1-H3 + CIDs.
  Footer firma + contacto.

CONTENT:
  Literal de sección 7 del pack (dossier panelistas).
  Gráfico barra H4 embebido como SVG.

AUDIENCE:
  Productor TV impresión, periodista leyendo offline.

DESIGN SYSTEM:
  bg blanco (imprimible) · tinta bg-deep texto
  danger-red número hero · fonts.body Inter 11pt
  radius.card 4px (más conservador impreso)

EXPORT:
  web/components/press-dossier.html → render PDF via Puppeteer
```

---

### C10 · NeuracodeFooter

```
GOAL:
  Footer branded presente en todo componente
  con CTA academia + CID captura actual + firma.

LAYOUT:
  Full-width 80px alto. Grid 3 col:
  Izq: logo Neuracode + "auditoria.neuracode.dev"
  Centro: CID IPFS captura actual (truncado) + SHA-256
  Der: "Metodología open-source · Firma: Jack Aguilar"

CONTENT:
  Literal: "Metodología open-source · Código reproducible
            · SHA-256 · neuracode.academy"
  CID dinámico inyectado por dashboard: {{current_cid}}
  Timestamp captura: {{universo_ts}} (2026-04-20T07:42:02Z)

AUDIENCE:
  Visitante dashboard, preservar marca + verificabilidad.

DESIGN SYSTEM:
  bg-deep · ink-muted texto · verified-green CID
  fonts.data CID · fonts.body firma
  Divider top alert-amber 2px

EXPORT:
  web/components/neuracode-footer.html
```

---

**Flujo integración post-Claude-Design:**

```
rtk ls web/components/
rtk git status
rtk git add web/components/
rtk git commit -m "feat(ui): 10 componentes H4 via Claude Design"
rtk git push
```

---

**Firma:** Jack Aguilar (Tony) · Perito técnico IA · CEO Neuracode Academy
**Cadena custodia:** GitHub `26b4cde` · tag `v2-mesas-900k` · IPFS `CID-FINDINGS`
**Métricas open-source · Código reproducible · SHA-256 · neuracode.academy**
