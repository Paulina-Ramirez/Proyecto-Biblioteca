# Cozy Biblioteca — Frontend

Interfaz web del sistema de gestión bibliotecaria. La identidad visual utiliza la paleta **Lavender Latte**, con Quicksand para los títulos y Nunito Sans para los textos funcionales.

## Páginas
- `index.html`: inicio de sesión y registro.
- `dashboard.html`: panel principal.
- `libros.html`: catálogo y filtros.
- `usuarios.html`: listado de usuarios para bibliotecario.
- `prestamos.html`: consulta de préstamos.
- `sanciones.html`: consulta de sanciones.

## Recursos compartidos
- `css/styles.css`: estilos globales y diseño responsive.
- `fonts/`: archivos locales WOFF2 de Quicksand y Nunito Sans, junto con sus licencias SIL Open Font License.
- `js/common.js`: conexión a la API, sesión, navegación y elementos comunes.
- `js/`: scripts específicos de cada página.

## Cómo ejecutar
1. Inicia el backend desde la raíz del proyecto: `python -m uvicorn app.main:app --reload`.
2. Abre la carpeta `frontend` en VS Code y ejecuta `index.html` con Live Server.
3. La API se espera en `http://127.0.0.1:8000`.

Las tipografías se cargan desde `fonts/`, por lo que no requieren conexión a internet. La conexión con la API sí requiere que el backend esté en ejecución.

Nota: se conservaron las rutas de API que utiliza el prototipo original. Algunas operaciones del backend pueden variar; valida cada flujo contra los endpoints del equipo.

## Categorías disponibles
El formulario usa una lista fija de categorías: Programación, Novela, Romance, Fantasía, Infantil e Historia. El filtro usa la misma lista, por lo que Romance aparece aunque todavía no haya libros de ese género.
