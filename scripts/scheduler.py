import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import schedule
import time
import threading
from scripts.main import tomar_lectura
from scripts.upload_github import subir_archivos, subir_dashboard
from scripts.process_data import generar_dashboard_json
from scripts.read_ws2000 import iniciar_servidor

TEMP_CRITICA = 75.0

def watchdog_termico():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp = int(f.read()) / 1000.0
        print(f"[WATCHDOG] Temperatura CPU: {temp}°C")
        if temp >= TEMP_CRITICA:
            print(f"[WATCHDOG] TEMPERATURA CRITICA {temp}°C - Generando reporte y apagando...")
            generar_dashboard_json()
            subir_dashboard()
            time.sleep(10)
            os.system("sudo shutdown -h now")
    except Exception as e:
        print(f"[WATCHDOG] Error leyendo temperatura: {e}")

def job_lectura():
    print("[SCHEDULER] Tomando lectura del sensor...")
    tomar_lectura()
    print("[SCHEDULER] Generando y subiendo datos...")
    generar_dashboard_json()
    subir_archivos()

def job_sistema():
    print("[SCHEDULER] Actualizando KPIs del sistema Pi...")
    generar_dashboard_json()
    subir_dashboard()

def iniciar_scheduler():
    print("[SCHEDULER] Esperando 10 min para que la red levante...")
    time.sleep(600)
    print("[SCHEDULER] Lectura inicial al arrancar...")
    job_lectura()
    schedule.every(60).minutes.do(job_lectura)
    schedule.every(15).minutes.do(job_sistema)
    schedule.every(5).minutes.do(watchdog_termico)
    print("[SCHEDULER] Activo - lecturas cada 60 min, KPIs Pi cada 15 min, watchdog cada 5 min")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    hilo_flask = threading.Thread(target=iniciar_servidor, daemon=True)
    hilo_flask.start()
    print("[SERVIDOR] Flask iniciado en puerto 7777")
    iniciar_scheduler()
