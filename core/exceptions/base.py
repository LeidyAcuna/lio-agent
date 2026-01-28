class AppError(Exception):
    """Clase base para otros errores de la aplicación"""
    pass

class DatabaseInsertError(AppError):
    """Se lanza cuando falla la inserción en Postgres"""
    def __init__(self, message="No se pudo guardar el gasto en la base de datos"):
        self.message = message
        super().__init__(self.message)

class AIProcessingError(AppError):
    """Se lanza cuando el LLM no puede entender el mensaje"""
    pass