from app_attendward.config.mysqlconnection import connectToMySQL

class Seccion:
    def __init__(self, data):
        self.id_seccion = data['id_seccion']
        self.id_asignatura = data['id_asignatura']
        self.n_seccion = data['seccion']
        self.horario = data['horario']
        self.creado=data['creado']
        self.editado=data['editado']