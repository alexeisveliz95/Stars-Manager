import logging
import os
from logging.handlers import RotatingFileHandler

def setup_stellar_logger(name="StarsManager"):
    """
    Configura un logger profesional con salida a consola y archivo rotativo.
    """
    # 1. Crear carpeta de logs si no existe
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 2. Definir el formato del log (Tiempo - Nombre - Nivel - Mensaje)
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 3. Handler para la Consola (Output visual rápido)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)

    # 4. Handler para Archivo (Rotativo: 5MB por archivo, máximo 3 archivos)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "stellar_activity.log"),
        maxBytes=5 * 1024 * 1024, 
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.DEBUG)

    # 5. Configuración final del Logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Evitar duplicados si se llama la función varias veces
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

# Instancia global para ser importada
logger = setup_stellar_logger()