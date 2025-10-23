import os
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

# --- Pide los datos para el nuevo doctor ---
nombre_doctor = input("Introduce el nombre completo del doctor: ")
rut_doctor = input("Introduce el RUT del doctor: ")
email_doctor = input("Introduce el email para el login: ")
contrasena_doctor = input("Introduce la contraseña para el login: ")

# Encriptar la contraseña (¡muy importante!)
contrasena_hasheada = generate_password_hash(contrasena_doctor)

conn = None # Inicializar para el bloque finally
cursor = None # Inicializar para el bloque finally
try:
    # --- Se conecta a la base de datos ---
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        port=os.getenv('DB_PORT', '5432'), # Usar puerto del .env o 5432 por defecto
        options="-c client_encoding=utf8"   # Forzar codificación UTF-8
    )
    cursor = conn.cursor()

    # --- Inserta en la tabla Usuarios ---
    cursor.execute(
        "INSERT INTO Usuarios (email, password, rol) VALUES (%s, %s, 'doctor') RETURNING id_usuario",
        (email_doctor, contrasena_hasheada)
    )
    # Obtenemos el ID del usuario recién creado
    id_nuevo_usuario = cursor.fetchone()[0]

    # --- Inserta en la tabla Doctores, vinculando con el usuario ---
    cursor.execute(
        "INSERT INTO Doctores (nombre_completo, rut, id_usuario) VALUES (%s, %s, %s)",
        (nombre_doctor, rut_doctor, id_nuevo_usuario)
    )

    # --- Confirma todos los cambios ---
    conn.commit()

    print("\n✅ ¡Doctor creado exitosamente!")
    print(f"   Email: {email_doctor}")
    print(f"   Ahora puedes usar estas credenciales para iniciar sesión.")

except Exception as error:
    if conn:
        conn.rollback() # Revertir si hubo error
    print(f"\n❌ Ocurrió un error: {error}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()