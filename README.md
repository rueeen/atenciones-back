# Sistema de Gestión y Trazabilidad de Solicitudes Estudiantiles

Proyecto fullstack Django para registrar, derivar y dar seguimiento a casos estudiantiles con trazabilidad completa.

## Arquitectura

Apps principales:
- `accounts`: perfil extendido (`UserProfile`) y roles.
- `organization`: estructura institucional (`Area`, `AcademicArea`, `Career`).
- `students`: gestión de estudiantes.
- `cases`: ciclo completo de casos, categorías, derivaciones, comentarios, adjuntos e historial.
- `dashboard`: métricas y panel principal.

## Funcionalidades clave

- Login/logout con vistas de Django.
- Permisos por rol (administrador, supervisor, funcionario, director/coordinador de carrera, solo lectura).
- CRUD de estudiantes y categorías.
- Casos con folio autogenerado, prioridad, estados, trazabilidad y resolución final.
- Derivación entre áreas con comentario obligatorio.
- Timeline de historial por caso.
- Adjuntos con validación de formato.
- Dashboard con métricas operativas.
- Django admin con filtros/búsquedas.

## Instalación y ejecución

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_initial_data
python manage.py runserver
```

Credenciales de ejemplo después de seed:
- `admin / admin1234`
- `supervisor_dae / supervisor1234`

## Base de datos

- Desarrollo: SQLite por defecto.
- Producción: exportar `DB_ENGINE=postgresql` y variables `POSTGRES_*`.

### Troubleshooting rápido

Si al entrar a `/login/` aparece:

`OperationalError: no such table: auth_user`

la base de datos todavía no tiene migraciones aplicadas. Ejecuta:

```bash
python manage.py migrate
python manage.py seed_initial_data
```

Luego reinicia el servidor (`python manage.py runserver`).

## Tests básicos

```bash
python manage.py test
```
