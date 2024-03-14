from flask import flash, redirect, render_template, Response, jsonify, request, url_for, send_file
from app_attendward import app
from app_attendward.config.mysqlconnection import connectToMySQL
from datetime import datetime
import cv2
import os
import pandas as pd
from itertools import cycle

# Ruta para almacenar los entrenamientos faciales
entrenamientos_ruta = 'app_attendward/rfacial/entrenamientos'

# Crear directorio si no existe
if not os.path.exists(entrenamientos_ruta):
    os.makedirs(entrenamientos_ruta)

# Listas para almacenar datos
listaDeDetectados = []
listaDeEstudiantes = []

# Función para generar el video del feed de la cámara
def generate():
    modelos_entrenados = []
    nombres_personas = []

    for modelo_file in os.listdir(entrenamientos_ruta):
        for estudiante in listaDeEstudiantes:
            if estudiante['rut'] ==  int(os.path.splitext(os.path.basename(modelo_file))[0]):
                modelo_entrenado = cv2.face_EigenFaceRecognizer.create()
                modelo_entrenado.read(os.path.join(entrenamientos_ruta, modelo_file))
                modelos_entrenados.append(modelo_entrenado)
                nombres_personas.append(os.path.splitext(os.path.basename(modelo_file))[0])

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                rostro = gray[y:y+h, x:x+w]  # Obtener el rostro
                rostro = cv2.resize(rostro, (160, 160), interpolation=cv2.INTER_CUBIC)  # Redimensionar el rostro

                # Realizar la predicción con cada modelo de entrenamiento
                for i, modelo_entrenado in enumerate(modelos_entrenados):
                    resultado = modelo_entrenado.predict(rostro)

                    if resultado[1] < 5500:
                        nombre_persona = nombres_personas[i]
                        # Si la persona no ha sido detectada previamente, agregarla a la lista
                        if nombre_persona not in listaDeDetectados:
                            listaDeDetectados.append(nombre_persona)
                        cv2.putText(frame, nombre_persona, (x, y - 20), 2, 1.1, (0, 255, 0), 1, cv2.LINE_AA)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                        break  # Salir del bucle si se encuentra una persona
                else:
                    cv2.putText(frame, "No encontrado", (x, y - 20), 2, 0.7, (0, 255, 0), 1, cv2.LINE_AA)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            (flag, encoded_image) = cv2.imencode(".jpg", frame)
            if not flag:
                continue
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n')

# Función para calcular el dígito verificador de un RUT
def calcular_digito_verificador(rut):
    reversed_digits = map(int, reversed(str(rut)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    return (-s) % 11 if s % 11 > 1 else 'K'

# Función para agregar el dígito verificador a un RUT
def agregar_digito_verificador(rut):
    return f"{rut}-{calcular_digito_verificador(rut)}"

# Función para verificar si un RUT ha sido detectado
def detectado(rut):
    return rut in listaDeDetectados

# Ruta para obtener todos los cursos
@app.route('/cursos', methods=['GET'])
def get_all_cursos():
    mysql = connectToMySQL('attend_bd')
    data = mysql.query_db("SELECT secciones.*, asignaturas.nombre AS nombre_asignatura FROM secciones JOIN asignaturas ON asignaturas.id_asignatura = secciones.id_asignatura;")
    mysql.close_connection()
    return render_template('listado_cursos.html', cursos=data)

# Ruta para obtener los alumnos de una sección y agregar la fecha actual
@app.route('/alumnos/<int:section_id>', methods=['GET'])
def get_alumnos_by_section_on_date(section_id):
    mysql = connectToMySQL('attend_bd')
    section_query = "SELECT secciones.*, asignaturas.nombre AS nombre_asignatura FROM secciones JOIN asignaturas ON asignaturas.id_asignatura = secciones.id_asignatura WHERE secciones.id_seccion = %s;"
    section_data = mysql.query_db(section_query, (section_id,))
    alumnos_query = "SELECT alumnos.* FROM alumnos JOIN inscritos ON inscritos.id_alumno = alumnos.id_alumno WHERE inscritos.id_seccion = %s;"
    alumnos_data = mysql.query_db(alumnos_query, (section_id,))
    aux_list = []
    for alumno in alumnos_data:
        aux_list.append(alumno)
    global listaDeEstudiantes
    global listaDeDetectados
    listaDeDetectados = []
    listaDeEstudiantes = aux_list

    mysql.close_connection()

    fecha_actual = datetime.now()
    meses = {
        1: 'enero',
        2: 'febrero',
        3: 'marzo',
        4: 'abril',
        5: 'mayo',
        6: 'junio',
        7: 'julio',
        8: 'agosto',
        9: 'septiembre',
        10: 'octubre',
        11: 'noviembre',
        12: 'diciembre'
    }
    
    return render_template('control_asistencia.html', seccion=section_data[0], alumnos=alumnos_data, fecha_actual=fecha_actual, meses=meses)

# Ruta para obtener la lista de alumnos detectados
@app.route('/listaDetectados', methods=['GET'])
def return_list():
    return jsonify(arreglo=listaDeDetectados)

# Ruta para agregar manualmente un alumno
@app.route('/agregar_manualmente', methods=['POST'])
def agregar_manualmente():

    data = request.json
    rut = data.get('rut')

    mysql = connectToMySQL('attend_bd')
    inscrito_query = "SELECT * FROM alumnos WHERE rut = %s;"
    inscrito_data = mysql.query_db(inscrito_query, (rut,))

    mysql.close_connection()

    if inscrito_data:
        listaDeDetectados.append(rut)
        return 'Valor agregado correctamente', 200
    else:
        return 'El RUT no se encuentra inscrito', 400

# Ruta para generar el feed de video
@app.route('/video_feed', methods=['GET'])
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Ruta para obtener los alumnos de una sección
@app.route('/listado_seccion/<int:section_id>', methods=['GET'])
def get_alumnos_by_section(section_id):
    mysql = connectToMySQL('attend_bd')
    section_query = "SELECT secciones.*, asignaturas.nombre AS nombre_asignatura FROM secciones JOIN asignaturas ON asignaturas.id_asignatura = secciones.id_asignatura WHERE secciones.id_seccion = %s;"
    section_data = mysql.query_db(section_query, (section_id,))
    alumnos_query = "SELECT alumnos.* FROM alumnos JOIN inscritos ON inscritos.id_alumno = alumnos.id_alumno WHERE inscritos.id_seccion = %s;"
    alumnos_data = mysql.query_db(alumnos_query, (section_id,))
    mysql.close_connection()

    return render_template('agregar_a_seccion.html', seccion=section_data[0], alumnos=alumnos_data, section_id=section_id)

# Ruta para agregar un alumno a una sección
@app.route('/agregar_alumno_seccion/<int:section_id>', methods=['POST'])
def agregar_alumno_seccion(section_id):

    rut = request.form.get('rut_alumno')

    db = connectToMySQL('attend_bd')
    query = "SELECT * FROM alumnos WHERE rut = %s"
    data = (rut,)
    resultado = db.query_db(query, data)

    if not resultado:
        flash('El rut proporcionado no está registrado', 'error')
        return redirect(url_for('get_alumnos_by_section', section_id=section_id))

    query = "SELECT id_alumno FROM alumnos WHERE rut = %s"
    data = (rut,)
    resultado = db.query_db(query, data)
    id_alumno = resultado[0]['id_alumno']
    query = "SELECT * FROM inscritos WHERE id_seccion = %s AND id_alumno = %s"
    data = (section_id, id_alumno)
    resultado = db.query_db(query, data)
    if resultado:
        flash('El alumno ya está inscrito en la sección', 'error')
        return redirect(url_for('get_alumnos_by_section', section_id=section_id))
    query = "INSERT INTO inscritos (id_seccion, id_alumno) VALUES (%s, %s)"
    data = (section_id, id_alumno)
    db.query_db(query, data)
    flash('Alumno agregado a la sección', 'success')
    db.close_connection()
    return redirect(url_for('get_alumnos_by_section', section_id=section_id))

# Ruta para agregar asistencia manualmente
@app.route('/agregar_asistencia_manual/<int:section_id>', methods=['POST'])
def agregar_asistencia_manual(section_id):
    rut = request.form.get('rut_alumno')
    query_alumno_id = "SELECT id_alumno FROM alumnos WHERE rut = %s"
    data = (rut,)
    db = connectToMySQL('attend_bd')
    alumno_resultado = db.query_db(query_alumno_id, data)

    if not alumno_resultado:
        return jsonify({'message': 'El Rut proporcionado no está registrado'}), 400

    flash('Asistencia agregada exitosamente', 'success')
    
    return redirect(url_for('get_alumnos_by_section_on_date', section_id=section_id))

# Ruta para generar un documento Excel con los alumnos detectados
@app.route('/generar_documento_excel', methods=['POST'])
def generar_documento_excel():
    df_ruts = pd.DataFrame(listaDeDetectados, columns=['RUT'])
    df_ruts['RUT'] = df_ruts['RUT'].apply(agregar_digito_verificador)
    mysql = connectToMySQL('attend_bd')
    nombres_apellidos = []
    for rut in listaDeDetectados:
        query = "SELECT nombre, apellido FROM alumnos WHERE rut = %s;"
        data = (rut,)
        resultado = mysql.query_db(query, data)
        if resultado:
            nombres_apellidos.append(resultado[0])
        else:
            nombres_apellidos.append({'nombre': 'Desconocido', 'apellido': 'Desconocido'})
    df_nombres_apellidos = pd.DataFrame(nombres_apellidos)
    df = pd.concat([df_ruts, df_nombres_apellidos], axis=1)
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    titulo_fecha = f'Fecha: {fecha_actual}'
    excel_filename = 'alumnos_detectados.xlsx'
    directorio_trabajo = os.getcwd()
    excel_filepath = os.path.join(directorio_trabajo, excel_filename)
    writer = pd.ExcelWriter(excel_filepath, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    worksheet = writer.sheets['Sheet1']
    worksheet.write('D1', titulo_fecha)
    writer.close()
    mysql.close_connection()
    return send_file(excel_filepath, as_attachment=True)

# Ruta para quitar un alumno de una sección
@app.route('/quitar_alumno_seccion', methods=['POST'])
def quitar_alumno_seccion():
    section_id = request.form.get('section_id')
    alumno_id = request.form.get('alumno_id')
    db = connectToMySQL('attend_bd')

    try:
        query = "DELETE FROM inscritos WHERE id_seccion = %s AND id_alumno = %s"
        data = (section_id, alumno_id)
        db.query_db(query, data)
        flash('Alumno quitado de la sección exitosamente', 'success')
    except Exception as e:
        flash('Error al quitar alumno de la sección', 'error')
        print(e)

    return redirect(url_for('get_alumnos_by_section', section_id=section_id))

# Ruta para quitar la asistencia de un alumno
@app.route('/quitar_asistencia', methods=['POST'])
def quitar_asistencia():
    data = request.json
    rut_estudiante = data.get('rut_estudiante')
    global listaDeDetectados
    for estudiante in listaDeDetectados:
        if estudiante == rut_estudiante:
            listaDeDetectados.remove(rut_estudiante)
            return 'Asistencia removida', 200
    return 'No se removió asistencia', 400
