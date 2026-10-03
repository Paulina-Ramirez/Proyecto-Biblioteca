# Proyecto Biblioteca - API REST

Sistema de Gestión de Biblioteca desarrollado con **FastAPI**, **SQLAlchemy** y **SQL Server**, siguiendo una **Arquitectura en Capas (N-Tier)**.

---

## Arquitectura del Proyecto

Este proyecto implementa el patrón **N-Tier** con las siguientes capas:
┌─────────────────────────────────────────┐
│ CAPA DE PRESENTACIÓN (routers/) │ ← Endpoints HTTP
├─────────────────────────────────────────┤
│ CAPA DE LÓGICA (services/) │ ← Reglas de negocio
├─────────────────────────────────────────┤
│ CAPA DE DATOS (repositories/) │ ← Acceso a la BD
├─────────────────────────────────────────┤
│ BASE DE DATOS (models/) │ ← SQL Server
└─────────────────────────────────────────┘

text

### Estructura de carpetas
Proyecto-Biblioteca/
│
├── app/
│ ├── config/ # Configuración (conexión BD)
│ │ └── database.py
│ ├── models/ # Entidades SQLAlchemy
│ │ ├── libro.py
│ │ ├── usuario.py
│ │ ├── prestamo.py
│ │ └── sancion.py
│ ├── repositories/ # Capa de acceso a datos (CRUD)
│ │ ├── libro_repository.py
│ │ ├── usuario_repository.py
│ │ ├── prestamo_repository.py
│ │ └── sancion_repository.py
│ ├── schemas/ # Validación de datos (Pydantic)
│ │ ├── libro_schema.py
│ │ ├── usuario_schema.py
│ │ ├── prestamo_schema.py
│ │ └── sancion_schema.py
│ ├── routers/ # Endpoints HTTP (FastAPI)
│ │ ├── libro_router.py
│ │ ├── usuario_router.py
│ │ ├── prestamo_router.py
│ │ └── sancion_router.py
│ └── main.py # Punto de entrada
│
├── database/
│ └── schema.sql # Script SQL Server
│
├── tests/ # Pruebas unitarias
├── requirements.txt # Dependencias Python
├── .gitignore
└── README.md



---

## Stack Tecnológico

| Tecnología | Versión | Uso |
| :--- | :--- | :--- |
| **Python** | 3.11+ | Lenguaje principal |
| **FastAPI** | 0.115.6 | Framework web |
| **SQLAlchemy** | 2.0.36 | ORM (mapeo objeto-relacional) |
| **Pydantic** | 2.10.4 | Validación de datos |
| **Uvicorn** | 0.34.0 | Servidor ASGI |
| **SQL Server** | 2019+ | Base de datos |
| **pyodbc** | 5.2.0 | Driver de conexión |
| **python-dotenv** | 1.0.1 | Variables de entorno |

---

## Requisitos Previos

Antes de empezar, asegúrate de tener instalado:

1. **Python 3.11 o superior** → [Descargar](https://www.python.org/downloads/)
2. **Git** → [Descargar](https://git-scm.com/download/win)
3. **SQL Server** (Express o Developer) → [Descargar](https://www.microsoft.com/es-mx/sql-server/sql-server-downloads)
4. **SQL Server Management Studio (SSMS)** → [Descargar](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms)
5. **ODBC Driver 17 for SQL Server** → [Descargar](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

---

## 🚀 Guía de Instalación

### Paso 1: Clonar el repositorio

Abre **PowerShell** en la carpeta donde quieras el proyecto y ejecuta:

```bash
git clone https://github.com/Paulina-Ramirez/Proyecto-Biblioteca.git
cd Proyecto-Biblioteca
Paso 2: Cambiar a la rama de trabajo
bash
git checkout develop
Paso 3: Crear y activar el entorno virtual
bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows PowerShell:
venv\Scripts\activate

# En Git Bash:
source venv/Scripts/activate
Sabrás que está activado porque verás (venv) al inicio de tu terminal.

Paso 4: Instalar dependencias
bash
pip install -r requirements.txt
Paso 5: Crear el archivo .env
Crea un archivo llamado .env en la raíz del proyecto (junto a requirements.txt) con el siguiente contenido:

env
DB_SERVER=.\MSSQLSERVER1
DB_NAME=BibliotecaDB
DB_DRIVER=ODBC Driver 17 for SQL Server
Importante: Ajusta MSSQLSERVER1 al nombre de tu instancia de SQL Server.

Si tu servidor se llama MSSQLSERVER (instancia por defecto) → DB_SERVER=localhost

Si es SQLEXPRESS → DB_SERVER=.\SQLEXPRESS

Si es MSSQLSERVER1 → DB_SERVER=.\MSSQLSERVER1

Para saber el nombre de tu instancia, ejecuta en PowerShell:

powershell
Get-Service | Where-Object {$_.Name -like "MSSQL*"}
Este archivo NO se sube a GitHub (está en .gitignore por seguridad).

Paso 6: Crear la base de datos
Abre SQL Server Management Studio (SSMS).

Conéctate con Windows Authentication a tu instancia.

Abre el archivo database/schema.sql.

Presiona F5 para ejecutarlo.

Deberías ver: Base de datos BibliotecaDB creada con datos de prueba.

Verifica que se creó correctamente:

sql
USE BibliotecaDB;
SELECT COUNT(*) FROM Libros;   -- Debe devolver 10
SELECT COUNT(*) FROM Usuarios; -- Debe devolver 3
Paso 7: Ejecutar el servidor
bash
uvicorn app.main:app --reload
Deberías ver:

text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
Paso 8: Abrir la documentación
Abre tu navegador en:

http://127.0.0.1:8000 → Mensaje de bienvenida

http://127.0.0.1:8000/docs → 🎉 Swagger UI (documentación interactiva)

http://127.0.0.1:8000/redoc → Documentación alternativa (ReDoc)
