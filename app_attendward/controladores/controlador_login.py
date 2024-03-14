from flask import render_template,session,redirect
from flask_bcrypt import Bcrypt
from app_attendward import app

# Inicializar Bcrypt con la aplicación Flask
bcrypt=Bcrypt(app)

# Función para desplegar la página de inicio de sesión
@app.route('/', methods = ['GET'])
def desplegar_login():
    return render_template('login.html')

# Función para realizar el logout
@app.route('/logout', methods=['POST'])
def haz_logout():
    session.clear()
    return redirect('/')