---
description: Crea spec SDD desde template + branch + stub directorios
argument-hint: H<N> "<título corto>"
---

# /new-finding $ARGUMENTS

Arranca un finding nuevo siguiendo SDD.

## Pasos

1. Parsear `$ARGUMENTS` → extraer ID (`H<N>`) y título.
2. Verificar que `docs/specs/H<N>.md` NO existe (evitar sobrescribir).
3. Crear branch: `rtk git checkout -b feat/h<N>`
4. Copiar `docs/specs/_TEMPLATE.md` → `docs/specs/H<N>.md`
5. Reemplazar placeholders:
   - `H<N>` → ID real
   - `<título corto imperativo>` → título recibido
   - `YYYY-MM-DD` → fecha actual
6. Abrir el archivo y pedir al usuario completar: H0, H1, método, umbral, anti-ataques.
7. Recordar: no avanzar a `/publish H<N>` hasta que spec tenga todos los campos.

## Output

- Branch creado
- Spec stub en `docs/specs/H<N>.md`
- Mensaje al usuario: "spec creada, completa H0/H1/método antes de correr pipeline".
