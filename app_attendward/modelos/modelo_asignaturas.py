from app_attendward.config.mysqlconnection import connectToMySQL

class Asignatura:
    def __init__(self, data):
        self.id_asignatura = data['id_asignatura']
        self.nombre = data['nombre']
        self.codigo = data['codigo']
        self.creado=data['creado']
        self.editado=data['editado']