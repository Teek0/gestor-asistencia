from app_attendward.config.mysqlconnection import connectToMySQL

class Alumno:
    def __init__(self, data):
        self.id_alumno = data['id_alumno']
        self.nombre = data['nombre']
        self.apellido = data['apellido']
        self.rut = data['rut']
        self.creado=data['creado']
        self.editado=data['editado']