# Importar las librerías necesarias
from flask import render_template, request, redirect, url_for, flash
from app_attendward import app
from app_attendward.config.mysqlconnection import connectToMySQL
import os
import cv2 as cv
import numpy as np
import imutils
from time import time
from shutil import rmtree

# Rutas a utilizar
data_ruta = 'app_attendward/rfacial/DATA'
ruta_entrenamientos = 'app_attendward/rfacial/entrenamientos'

# Función para verificar si existe la ruta y crearla si no existe
def verificar_ruta(ruta):
    if not os.path.exists(ruta):
        os.makedirs(ruta)

# Función para procesar la página de administración
@app.route('/admin', methods=['GET'])
def admin_page():
    resultados = None
    return render_template('administrar.html', resultados=resultados)

# Función para buscar un alumno
@app.route('/buscar_alumno', methods=['POST'])
def buscar_alumno():
    rut = request.form.get('rut')
    if not rut:
        flash('Debes ingresar un rut', 'error')
        return redirect(url_for('admin_page'))
    try:
        rut = int(rut)
    except ValueError:
        flash('El rut ingresado no es válido', 'error')
        return redirect(url_for('admin_page'))

    db = connectToMySQL('attend_bd')
    query = "SELECT * FROM alumnos WHERE rut = %s"
    data = (rut,)
    resultados = db.query_db(query, data)

    train_found = any(rut == int(os.path.splitext(os.path.basename(modelo_file))[0]) for modelo_file in os.listdir(ruta_entrenamientos))
    resultados = {"train_found": train_found, "resultados": resultados}
    return render_template('administrar.html', resultados=resultados)

# Función para crear un alumno
@app.route('/crear_alumno', methods=['POST'])
def crear_alumno():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    rut = request.form.get('rut_nuevo')
    if not nombre or not apellido or not rut:
        flash('Todos los campos son obligatorios', 'error')
        return redirect(url_for('admin_page'))

    db = connectToMySQL('attend_bd')
    query = "SELECT * FROM alumnos WHERE rut = %s"
    data = (rut,)
    resultado = db.query_db(query, data)
    if resultado:
        flash('El rut proporcionado ya está registrado', 'error')
        return redirect(url_for('admin_page'))

    query = "INSERT INTO alumnos (nombre, apellido, rut) VALUES (%s, %s, %s)"
    data = (nombre, apellido, rut)
    db.query_db(query, data)

    flash('Alumno creado exitosamente', 'success')
    return redirect(url_for('admin_page'))

# Función para entrenar el modelo del alumno
@app.route('/entrenar', methods=['POST'])
def entrenar_modelo_alumno():
    rut = request.form.get('rut')
    modelo = rut
    ruta_completa = os.path.join(data_ruta, modelo)
    verificar_ruta(ruta_completa)

    camara = cv.VideoCapture(0)
    print("Cámara lista")
    ruidos = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
    tiempo_inicial = time()

    id = 1
    while True:
        respuesta, captura = camara.read()
        if not respuesta:
            break
        captura = imutils.resize(captura, width=640)

        gris = cv.cvtColor(captura, cv.COLOR_BGR2GRAY)
        idcaptura = captura.copy()

        cara = ruidos.detectMultiScale(gris, 1.3, 5)

        for (x, y, e1, e2) in cara:
            cv.rectangle(captura, (x, y), (x+e1, y+e2), (0, 255, 0), 2)
            rostrocapturado = idcaptura[y:y+e2, x:x+e1]
            rostrocapturado = cv.resize(rostrocapturado, (160, 160), interpolation=cv.INTER_CUBIC)
            cv.imwrite(os.path.join(ruta_completa, f'imagen_{id}.jpg'), rostrocapturado)
            id += 1

        cv.imshow("Resultado", captura)

        if id == 251:
            break
    print("Tiempo de captura: ", round(time() - tiempo_inicial, 1), " segundos")
    camara.release()
    cv.destroyAllWindows()

    lista_data = os.listdir(data_ruta)
    modelos_entrenados = []

    for persona in lista_data:
        ruta_completa = os.path.join(data_ruta, persona)
        print('Leyendo las imágenes de:', persona)
        
        entrenamiento_eigen_face_recognizer = cv.face_EigenFaceRecognizer.create()
        
        ids = []
        rostros_data = []
        id = 0

        for archivo in os.listdir(ruta_completa):
            ids.append(id)
            rostros_data.append(cv.imread(os.path.join(ruta_completa, archivo), 0))
            id += 1

            os.remove(os.path.join(ruta_completa, archivo))

        entrenamiento_eigen_face_recognizer.train(rostros_data, np.array(ids))
        
        modelo_file = f"{persona}.xml"
        entrenamiento_eigen_face_recognizer.save(os.path.join(ruta_entrenamientos, modelo_file))
        
        modelos_entrenados.append(entrenamiento_eigen_face_recognizer)

        if os.path.exists(ruta_completa):
            rmtree(ruta_completa)

    flash('Entrenamiento completado exitosamente', 'success')
    return redirect(url_for('admin_page'))

# Función para eliminar el entrenamiento de un alumno
@app.route('/eliminar_entrenamiento', methods=['POST'])
def eliminar_entrenamiento():
    rut = request.form.get('rut')
    eliminar_entrenamiento_rut(rut)
    flash('Entrenamiento eliminado exitosamente', 'success')
    return redirect(url_for('admin_page'))

# Función para eliminar el entrenamiento basado en el rut
def eliminar_entrenamiento_rut(rut):
    ruta_completa = os.path.join(ruta_entrenamientos, f'{rut}.xml')
    if os.path.exists(ruta_completa):
        os.remove(ruta_completa)
