import json
import csv
import logging
import os
from datetime import datetime

def cargar_config(ruta):
    with open(ruta, 'r') as f:
        return json.load(f)

def timestamp_ahora():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def guardar_csv(ruta, fila, encabezados=None):
    archivo_nuevo = not os.path.exists(ruta)
    with open(ruta, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=encabezados or fila.keys())
        if archivo_nuevo:
            writer.writeheader()
        writer.writerow(fila)

def configurar_log(nombre, ruta_log):
    logger = logging.getLogger(nombre)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(ruta_log)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
