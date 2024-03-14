from flask import Flask
import re

app = Flask(__name__)
app.secret_key = "3sdXj904DG5j3kklFSHg8hY7d"

BASE_DATOS = "attend_bd"

NOMBRE_REGEX = re.compile(r'^[a-zA-Z ]+$')