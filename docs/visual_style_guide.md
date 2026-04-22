# Guía visual interna

## Identidad
- Estilo institucional sobrio con énfasis en legibilidad.
- Color principal de marca: rojo institucional (`--c-primary`).
- Fondos claros para contenido y barra lateral oscura para navegación.

## Componentes
- **Navbar:** branding compacto, usuario visible, menú móvil.
- **Sidebar:** iconos Bootstrap por módulo, estado activo con acento rojo, cierre de sesión en botón sensible.
- **Cards:** borde suave + sombra baja para orden visual.
- **Tablas:** encabezado oscuro, filas con hover suave.
- **Formularios:** foco rojo accesible y etiquetas en semibold.
- **Botones:**
  - Principal: `btn-main`.
  - Secundario: `btn-soft`.
  - Sensible: `logout-btn`.

## Recomendaciones
- Reutilizar `page-header`, `page-subtitle`, `btn-main`, `btn-soft`, `app-table`.
- Evitar estilos inline y colores no definidos en variables CSS.
