from app_attendward.config.mysqlconnection import connectToMySQL

class Inscrito:
    def __init__(self, data):
        self.id_alumno = data['id_alumno']
        self.id_seccion = data['id_seccion']