import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.utils import timestamp_ahora, guardar_csv
from scripts.read_distance import leer_nivel

RUTA_RAW = "data/raw/nivel_raw.csv"

def tomar_lectura():
    distancia, volumen = leer_nivel()
    if distancia is None:
        print("[SKIP] Lectura descartada, sin respuesta del sensor.")
        return
    fila = {
        "timestamp": timestamp_ahora(),
        "distancia_cm": distancia,
        "volumen_litros": volumen
    }
    guardar_csv(RUTA_RAW, fila)
    print(f"[{fila['timestamp']}] Nivel: {distancia} cm | Volumen: {volumen} L")

if __name__ == "__main__":
    print("Sistema AWA05 iniciado.")
    tomar_lectura()
