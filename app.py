import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
# Flask necesita esta clave para mantener las sesiones seguras
app.secret_key = os.getenv('SECRET_KEY')

# --- Configuración de la conexión a la base de datos ---
def obtener_conexion_db():
    """Crea y devuelve una conexión a la base de datos."""
    try:
        # Construir la cadena DSN manualmente
        dsn = (
            f"host='{os.getenv('DB_HOST')}' "
            f"port='{os.getenv('DB_PORT', '5432')}' "
            f"dbname='{os.getenv('DB_NAME')}' "
            f"user='{os.getenv('DB_USER')}' "
            f"password='{os.getenv('DB_PASS')}' "
            f"options='-c client_encoding=utf8'" # Incluir opción aquí
        )
        # print(f"Intentando conectar con DSN: {dsn}") # Descomenta para depurar si sigue fallando
        conexion = psycopg2.connect(dsn)
        return conexion
    except Exception as e:
        # Imprimir el error específico de conexión ayuda a diagnosticar
        print(f"ERROR AL CONECTAR A LA BASE DE DATOS: {e}")
        raise # Vuelve a lanzar el error para que Flask lo muestre
# --- Rutas de la Aplicación ---

@app.route('/')
def inicio():
    # Si ya hay una sesión iniciada, redirige al panel principal
    if 'id_usuario' in session:
        return redirect(url_for('panel_principal'))
    return redirect(url_for('iniciar_sesion'))

# --- LOGIN (CORREGIDO) ---
@app.route('/login', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'POST':
        email = request.form['email']
        contrasena = request.form['password']

        conn = None  # Inicializar conn a None
        cursor = None # Inicializar cursor a None
        try:
            conn = obtener_conexion_db()
            cursor = conn.cursor()
            # Busca el usuario por email
            cursor.execute('SELECT id_usuario, password, rol FROM Usuarios WHERE email = %s', (email,))
            usuario = cursor.fetchone()

            # Verifica si el usuario existe y la contraseña es correcta
            if usuario and check_password_hash(usuario[1], contrasena):
                # Guarda datos del usuario en la sesión
                session['id_usuario'] = usuario[0]
                session['rol_usuario'] = usuario[2]

                # Busca el nombre del doctor asociado (SI el rol es 'doctor')
                # AHORA SE HACE *ANTES* DE CERRAR EL CURSOR Y LA CONEXIÓN
                if usuario[2] == 'doctor':
                    cursor.execute('SELECT nombre_completo FROM Doctores WHERE id_usuario = %s', (usuario[0],))
                    doctor_info = cursor.fetchone()
                    if doctor_info:
                        # Guarda solo el primer nombre en la sesión
                        session['nombre_doctor'] = doctor_info[0].split()[0]
                    else:
                        # Si no se encuentra un perfil de doctor, guarda un nombre genérico o vacío
                        session['nombre_doctor'] = 'Doctor' # O dejarlo vacío: ''

                # Redirige al panel principal DESPUÉS de guardar todo en la sesión
                return redirect(url_for('panel_principal'))
            else:
                # Si el usuario no existe o la contraseña es incorrecta
                flash('Correo o contraseña incorrectos.')

        except Exception as e:
            # Captura cualquier error durante el proceso y lo muestra
            flash(f'Ocurrió un error: {e}')
        finally:
            # Asegura que el cursor y la conexión se cierren SIEMPRE,
            # incluso si hubo un error
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Si el método es GET (cargar la página) o si el login falló, muestra el formulario
    return render_template('login.html')


# --- PANEL PRINCIPAL (DASHBOARD) ---
@app.route('/panel')
def panel_principal():
    # Proteger ruta: si no hay sesión, no se puede entrar
    if 'id_usuario' not in session:
        flash('Por favor, inicia sesión para acceder.')
        return redirect(url_for('iniciar_sesion'))

    # Diferenciar paneles según el rol
    if session.get('rol_usuario') == 'doctor':
        # Pasamos el nombre del doctor a la plantilla
        nombre = session.get('nombre_doctor', 'Doctor') # Usa 'Doctor' si no se guardó el nombre
        return render_template('dashboard_doctor.html', nombre_doctor=nombre)
    elif session.get('rol_usuario') == 'admin':
        # Lógica para otros roles (ej. admin)
        return "<h1>Bienvenido, Admin!</h1>" # Puedes crear un dashboard_admin.html
    else:
        # Si el rol no es reconocido, cierra sesión por seguridad
        session.clear()
        flash('Rol de usuario no reconocido.')
        return redirect(url_for('iniciar_sesion'))

# --- CREAR ATENCIÓN ---
@app.route('/crear_atencion', methods=['GET', 'POST'])
def crear_atencion():
    if 'id_usuario' not in session or session.get('rol_usuario') != 'doctor':
        flash('Acceso no autorizado.')
        return redirect(url_for('iniciar_sesion'))

    if request.method == 'POST':
        # Obtener datos del formulario
        nombre_paciente = request.form['paciente_nombre']
        rut_paciente = request.form['paciente_rut']
        fecha_atencion = request.form['fecha_atencion']
        nombre_tratamiento = request.form['tratamiento_nombre']
        costo_tratamiento = int(request.form['tratamiento_costo'])

        # Datos del laboratorio (opcionales)
        hubo_laboratorio = 'hubo_laboratorio' in request.form
        nombre_lab = request.form.get('lab_nombre')
        costo_lab = request.form.get('lab_costo')

        conn = None
        cursor = None
        try:
            conn = obtener_conexion_db()
            cursor = conn.cursor()
            conn.autocommit = False # Iniciar transacción

            # --- INICIO DE LA TRANSACCIÓN ---
            # 1. Manejar Paciente (crear si no existe)
            cursor.execute('SELECT id_paciente FROM Pacientes WHERE rut = %s', (rut_paciente,))
            paciente = cursor.fetchone()
            if paciente:
                id_paciente = paciente[0]
            else:
                cursor.execute('INSERT INTO Pacientes (nombre_completo, rut) VALUES (%s, %s) RETURNING id_paciente',
                               (nombre_paciente, rut_paciente))
                id_paciente = cursor.fetchone()[0]

            # 2. Obtener id_doctor a partir del id_usuario de la sesión
            cursor.execute('SELECT id_doctor FROM Doctores WHERE id_usuario = %s', (session['id_usuario'],))
            doctor_result = cursor.fetchone()
            if not doctor_result:
                raise Exception("Perfil de doctor no encontrado para este usuario.")
            id_doctor = doctor_result[0]


            # 3. Insertar Atención
            cursor.execute('INSERT INTO Atenciones (fecha_atencion, id_doctor, id_paciente) VALUES (%s, %s, %s) RETURNING id_atencion',
                           (fecha_atencion, id_doctor, id_paciente))
            id_atencion = cursor.fetchone()[0]

            # 4. Insertar Tratamiento
            cursor.execute('INSERT INTO Tratamientos (nombre_tratamiento, costo_tratamiento, id_atencion) VALUES (%s, %s, %s) RETURNING id_tratamiento',
                           (nombre_tratamiento, costo_tratamiento, id_atencion))
            id_tratamiento = cursor.fetchone()[0]

            # 5. Insertar Laboratorio (si aplica)
            if hubo_laboratorio and nombre_lab and costo_lab:
                cursor.execute('INSERT INTO Laboratorios (nombre_laboratorio, costo_laboratorio, id_tratamiento) VALUES (%s, %s, %s)',
                               (nombre_lab, int(costo_lab), id_tratamiento))

            # --- CONFIRMAR TRANSACCIÓN ---
            conn.commit()
            flash('¡Atención guardada con éxito!', 'success')
            return redirect(url_for('panel_principal'))

        except Exception as error:
            # --- REVERTIR TRANSACCIÓN EN CASO DE ERROR ---
            if conn:
                conn.rollback()
            flash(f'Error al guardar la atención: {error}', 'danger')

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Si es GET, muestra el formulario
    return render_template('formulario_atencion.html')

# --- CERRAR SESIÓN (LOGOUT) ---
@app.route('/logout')
def cerrar_sesion():
    session.clear() # Limpia todos los datos de la sesión
    flash('Has cerrado sesión exitosamente.')
    return redirect(url_for('iniciar_sesion'))

if __name__ == '__main__':
    # El modo debug es solo para desarrollo. Quítalo cuando lances la aplicación.
    app.run(host='0.0.0.0', debug=True) # Añadido host='0.0.0.0' por si lo necesitas localmente