# Intranet Monfer - Clínica Odontológica

Este proyecto es una intranet desarrollada con Flask y PostgreSQL para gestionar atenciones en una clínica odontológica.

## Requisitos Previos

Asegúrate de tener instalado:
- Python (versión 3.11 o superior recomendada)
- Git
- PostgreSQL (instalado y corriendo localmente)

## Configuración Local

Sigue estos pasos para ejecutar el proyecto en tu computadora:

1.  **Clonar el Repositorio:**
    Si aún no tienes el proyecto, clónalo desde GitHub:
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_CARPETA_PROYECTO>
    ```

2.  **Crear y Activar el Entorno Virtual:**
    Necesitamos un entorno aislado para las librerías de Python.
    ```powershell
    # 1. Crea el entorno (solo la primera vez)
    python -m venv .venv

    # 2. Permite la ejecución de scripts (si PowerShell da error)
    #    Ejecuta esto SOLO si el siguiente comando falla
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

    # 3. Activa el entorno (haz esto CADA VEZ que abras una nueva terminal)
    .\.venv\Scripts\Activate.ps1
    ```
    *(Verás `(.venv)` al inicio de la línea si se activó correctamente)*.

3.  **Instalar Dependencias:**
    Instala todas las librerías necesarias listadas en `requirements.txt`.
    ```powershell
    pip install -r requirements.txt
    ```
    *(Asegúrate de que el archivo se llame `requirements.txt` y no `requerimientos.txt`)*.

4.  **Configurar la Base de Datos Local:**
    * Abre tu herramienta de PostgreSQL (pgAdmin o la extensión de VS Code).
    * Asegúrate de tener un usuario (ej: `postgres`) con una contraseña **sin acentos**.
    * Crea una base de datos nueva para este proyecto (ej: `monfer_db`).
    * Ejecuta el script `schema.sql` (que te debe pasar tu compañero) dentro de esta nueva base de datos para crear todas las tablas.

5.  **Configurar Variables de Entorno:**
    * Crea un archivo llamado `.env` en la raíz del proyecto (al lado de `app.py`).
    * Copia y pega el siguiente contenido, **reemplazando los valores** con los de **TU** base de datos local y genera una `SECRET_KEY` segura:
        ```env
        # .env - Variables locales (NO SUBIR A GITHUB)

        # Genera una clave con: python -c "import secrets; print(secrets.token_hex(32))"
        SECRET_KEY='TU_CLAVE_SECRETA_LARGA_Y_ALEATORIA'

        # --- Tus Datos de PostgreSQL Local ---
        DB_HOST=localhost
        DB_PORT=5432       # O el puerto que uses localmente
        DB_NAME=monfer_db  # El nombre de la BD que creaste
        DB_USER=postgres   # Tu usuario local
        DB_PASS=TU_CONTRASEÑA_LOCAL_SIMPLE # Tu contraseña local sin acentos
        ```

6.  **Crear un Usuario (si es necesario):**
    Si necesitas crear un usuario para iniciar sesión, usa el script proporcionado:
    ```powershell
    python crear_usuario.py
    ```

## Ejecutar la Aplicación

Con el entorno virtual activado (`(.venv)` visible), ejecuta:
```powershell
python app.py