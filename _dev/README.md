# web/_dev/ — Design system primitivas

> Catálogo de componentes reutilizables para landings de findings. `web-builder` agente consulta aquí antes de inventar layouts.

**Reglas:**
- `robots.txt` los bloquea (no indexar).
- Cada primitiva = HTML self-contained con CSS inline.
- Al crear landing nueva: **componer** primitivas, no duplicar patrones.

## Catálogo

| Primitiva | URL dev | Usa cuando |
|---|---|---|
| `ascii-preview/` | /ascii-preview/ | Hero dramático con arte ASCII (H4 usa esto) |
| `bento-preview/` | /bento-preview/ | Grid de bloques desiguales — cadena custodia, capas de evidencia |
| `dual-voice-preview/` | /dual-voice-preview/ | Columna popular ↔ técnico lado a lado (traducción señora mercado ↔ perito) |
| `scrollama-preview/` | /scrollama-preview/ | Scroll-telling sincronizado — progresión narrativa, steps |
| `storytelling-preview/` | /storytelling-preview/ | Sistema completo storytelling — hook + beats + cierre |
| `timeline-preview/` | /timeline-preview/ | Cronología — "cómo lo hice", evolución temporal, fases captura |

## Tokens de diseño (compartidos)

```css
--ink: #0c1a2e       /* texto principal */
--paper: #faf7f2     /* fondo */
--blood: #e63946     /* alertas, números críticos */
--rule: #d4ccbd      /* separadores */
--muted: #5a5a5a     /* secundario */
```

Fuentes: Fraunces (títulos) + Inter (cuerpo) + JetBrains Mono (código) + Caveat (handwriting acento).

## Cómo componer landing finding nueva

1. Hero: elegir entre `ascii-preview` (impacto) o estático H1 (directo).
2. Cuerpo principal: `dual-voice-preview` si hay 2 audiencias en misma página.
3. Evidencia: `bento-preview` para grid de capas/custodia/artefactos.
4. Narrativa: `scrollama-preview` para progresión.
5. Contexto: `timeline-preview` para método/cronología.
6. Remate: `storytelling-preview` para CTA + hook social.

## Extender catálogo

Nueva primitiva = nueva carpeta `web/_dev/<nombre>-preview/index.html` + fila aquí. Mantener self-contained (inline CSS, sin dependencias web/).

## Referencias prod

- `web/h4/index.html` usa `ascii-preview` como hero
- `web/h12/index.html` usa `dual-voice-preview` parcial
