# CHAIN_OF_CUSTODY.md — Protocolo de cadena de custodia

Este documento define el procedimiento formal para capturar, conservar y
verificar la integridad de los datos descargados de ONPE.

## 1. Principios

1. **Inmutabilidad:** una vez capturado, un archivo nunca se modifica. Si hay
   que corregir algo, se hace una nueva captura y se explica la relación.
2. **Trazabilidad:** cada archivo tiene timestamp UTC, hash SHA-256, URL de
   origen y autor de la captura.
3. **Reproducibilidad:** cualquier tercero con el repositorio puede verificar
   los hashes y re-ejecutar el análisis.
4. **Firma opcional:** los commits pueden firmarse con GPG para acreditar la
   identidad del capturante de manera criptográfica.

## 2. Procedimiento de captura

### 2.1 Pre-captura
- Verificar que estás en tu máquina personal, NO en un servidor remoto.
- Estar conectado desde una IP peruana (ONPE puede bloquear otros orígenes).
- Sincronizar el reloj del sistema con NTP (importante para timestamps):
  ```powershell
  w32tm /resync
  ```

### 2.2 Captura
Ejecutar desde la raíz del proyecto, con venv activado:

```powershell
py src\capture\fetch_onpe.py
```

El script hace:
1. Crea una carpeta `captures\YYYYMMDDTHHMMSSZ\`.
2. Descarga cada endpoint a `captures\YYYYMMDDTHHMMSSZ\raw\`.
3. Calcula SHA-256 inmediato tras cada descarga.
4. Registra cada archivo en `MANIFEST.jsonl` con:
   ```json
   {
     "endpoint": "snap1",
     "url": "https://resultadoelectoral.onpe.gob.pe/...",
     "fetched_at_utc": "2026-04-17T06:27:20Z",
     "local_path": "raw/snap1.json",
     "bytes": 4231,
     "sha256": "3b14fdedfa9bee2cd5f46bfc28beade05f31dd9638825ca61739430e51154d46",
     "http_status": 200,
     "user_agent": "AuditoriaEG2026/1.0 (personero tecnico Renovacion Popular)",
     "public_ip": "<tu-IP-pública>",
     "hostname": "<nombre-del-host>"
   }
   ```
5. Escribe `captures\YYYYMMDDTHHMMSSZ\README.md` con descripción humana.

### 2.3 Post-captura (commit)

Commit inmediato y push al repositorio remoto:

```powershell
git add captures\20260417T*
git status                             # revisar que SOLO se agrega lo nuevo
git commit -S -m "capture: ONPE backend at 06:27 UTC, 93.17%"
git push origin main
```

**NUNCA** ejecutar `git add .` ciegamente: podrías incluir archivos locales
no relacionados.

Si usas firma GPG (recomendado):
```powershell
# Configuración una sola vez:
git config --global user.signingkey <tu-key-id>
git config --global commit.gpgsign true
```

## 3. Verificación de integridad (tercero)

Cualquier auditor que quiera verificar una captura ejecuta:

```powershell
py src\capture\verify_manifest.py captures\20260417T062711Z\
```

El script:
1. Lee el `MANIFEST.jsonl`.
2. Recalcula SHA-256 de cada archivo listado.
3. Compara con el hash registrado.
4. Imprime "OK" por archivo verificado o "MISMATCH" con el delta.
5. Sale con código 0 si todo coincide, ≠ 0 si hay alguna discrepancia.

**Importante:** la verificación comprueba que los archivos no fueron
modificados *después* de la captura. NO comprueba que los datos originales
de ONPE fueran correctos al momento de la captura — para eso se usaría la
firma digital de ONPE, que actualmente no está publicada.

## 4. Qué hacer si detectas una inconsistencia

Si al ejecutar `verify_manifest.py` aparece un MISMATCH:

1. **No borres nada.** El propio mismatch es evidencia.
2. **Documenta** la discrepancia en un issue del repositorio.
3. **Ejecuta una nueva captura** con timestamp nuevo para contraste.
4. **Revisa el git log** para ver si alguien alteró el manifiesto o los
   archivos fuera del procedimiento.

## 5. Retención

Las capturas NUNCA se borran. El repositorio crece con el tiempo; eso es
deliberado. Si el tamaño excede los límites de GitHub (1GB recomendado, 100MB
por archivo), migrar a Git LFS o a un bucket S3/Cloud Storage con manifiesto
indexado en el repo.

## 6. Responsabilidades

| Rol | Responsabilidad |
|---|---|
| Capturante | Ejecutar `fetch_onpe.py` desde su máquina y hacer commit firmado |
| Revisor | Ejecutar `verify_manifest.py` tras cada commit para validar |
| Analista | Ejecutar pipeline de análisis SOLO sobre archivos con hash verificado |
| Autor del informe | Firmar el informe final asumiendo responsabilidad por las conclusiones |

Un mismo individuo puede asumir varios roles, pero las etapas siempre se
ejecutan en orden: capturar → verificar → analizar → informar.
