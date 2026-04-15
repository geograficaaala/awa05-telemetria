import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import schedule
import time
import threading
from scripts.main import tomar_lectura
from scripts.upload_github import subir_archivos
from scripts.read_ws2000 import iniciar_servidor

def job_lectura():
    print("[SCHEDULER] Tomando lectura del sensor...")
    tomar_lectura()

def job_subida():
    print("[SCHEDULER] Subiendo datos a GitHub...")
    subir_archivos()

def iniciar_scheduler():
    print("[SCHEDULER] Lectura inicial al arrancar...")
    job_lectura()

    schedule.every(60).minutes.do(job_lectura)
    schedule.every().day.at("12:00").do(job_subida)
    schedule.every().day.at("00:00").do(job_subida)

    print("[SCHEDULER] Activo - lectura cada 60 min, subida a las 12:00 y 00:00")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    hilo_flask = threading.Thread(target=iniciar_servidor, daemon=True)
    hilo_flask.start()
    print("[SERVIDOR] Flask iniciado en puerto 7777")
    iniciar_scheduler()
