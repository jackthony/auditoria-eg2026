# Dashboard Público — `web/`

Dashboard estático para GitHub Pages. HTML + JSON + Chart.js CDN. Sin build step.

## Publicar en GitHub Pages (3 pasos)

1. Push del repo a GitHub público: `github.com/neuracode/auditoria-eg2026`
2. Settings → Pages → Source: **Deploy from a branch** → Branch: `main` → Folder: `/web` → Save.
3. Esperar 1-2 min. URL: `https://neuracode.github.io/auditoria-eg2026/`

## Actualización continua del dashboard

Cada vez que hay una nueva captura:

```bash
py src/capture/fetch_onpe.py
py src/process/build_dataset.py
py src/analysis/run_all.py
py scripts/build_dashboard_json.py   # <-- regenera web/data.json
git add captures/ data/ reports/ web/data.json
git commit -m "update: corte YYYY-MM-DD HH:MM UTC"
git push
```

GitHub Pages sirve el HTML actualizado automáticamente tras el push.

## Loop completo automático

```bash
py scripts/capture_loop.py --interval 15
# En otro terminal, loop de publicación:
while true; do
  py scripts/build_dashboard_json.py
  git add -A web/data.json captures/
  git commit -m "auto: snapshot $(date -u +%Y-%m-%dT%H:%MZ)" || true
  git push || true
  sleep 900  # 15 min
done
```

## Archivos

- `index.html` — dashboard autocontenido (Chart.js via CDN)
- `data.json` — regenerado por `scripts/build_dashboard_json.py`
- `README.md` — este archivo
