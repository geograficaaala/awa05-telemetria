import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils import cargar_config, timestamp_ahora

def leer_peso_simulado():
    """Retorna un peso simulado para pruebas sin hardware."""
    import random
    return round(random.uniform(0.5, 5.0), 3)

def leer_peso():
    try:
        from hx711 import HX711
        pass
    except Exception as e:
        print(f"Hardware no disponible: {e}")
        return leer_peso_simulado()

if __name__ == "__main__":
    peso = leer_peso_simulado()
    print(f"[{timestamp_ahora()}] Peso simulado: {peso} kg")
