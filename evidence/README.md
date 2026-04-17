# evidence/

Carpeta para evidencias complementarias al análisis cuantitativo.

## Subcarpetas

### `legal_references/`
Copias locales de los textos normativos citados en el informe.
Recomendado tener al menos:
- Reglamento JNE 0182-2025 sobre Actas Observadas, Impugnadas y Solicitud de Nulidad
- Ley Orgánica de Elecciones (Ley N° 26859)
- Ley Orgánica de la ONPE (Ley N° 26487)
- Plan Operativo Electoral EG2026 v03 (publicado por ONPE)

### `public_documents/`
Captura de documentos públicos (oficios, notas de prensa, actas de comisiones).
Formato sugerido: PDF + captura completa (wayback machine o archive.today).

Nomenclatura recomendada:
```
YYYYMMDD_<fuente>_<tema_breve>.pdf
```
Ejemplo:
```
20260414_congreso_comision_fiscalizacion_corvetto.pdf
20260415_jnj_investigacion_corvetto.pdf
```

### `personero_copies/`
Copias físicas de actas en poder del partido.

**IMPORTANTE**: Esta carpeta está excluida del repositorio público por defecto
(ver `.gitignore`). Subir solo si el partido y su equipo legal lo autorizan
explícitamente — las actas pueden contener información identificable.

Nomenclatura recomendada:
```
ACTA_<odpe>_<mesa>_<candidato_congreso>_<tipo>.{pdf,jpg}
```
Ejemplo:
```
ACTA_LIMA01_12345_presidencial_copia_personero.jpg
```

## Buenas prácticas

1. Cada archivo debería tener su propio hash SHA-256 registrado.
2. Timestamps y ubicación del origen documentados al momento de subir.
3. Si es una foto tomada por un personero, conservar los metadatos EXIF
   (fecha, GPS) — NO limpiarlos hasta que el equipo legal lo indique.
