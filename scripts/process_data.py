import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import csv
import json
import os
from scripts.utils import timestamp_ahora

RUTA_NIVEL = "data/raw/nivel_raw.csv"
RUTA_CLIMA = "data/raw/clima_raw.csv"
RUTA_JSON  = "data/processed/dashboard_data.json"

def leer_csv(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r") as f:
        return list(csv.DictReader(f))

def ultima_lectura(filas, campos):
    if not filas:
        return {c: None for c in campos}
    ultima = filas[-1]
    return {c: ultima.get(c, None) for c in campos}

def serie_temporal(filas, campo, limite=24):
    datos = []
    for fila in filas[-limite:]:
        try:
            datos.append({"timestamp": fila["timestamp"], "valor": float(fila[campo])})
        except (ValueError, KeyError):
            pass
    return datos

def generar_dashboard_json():
    os.makedirs("data/processed", exist_ok=True)
    nivel = leer_csv(RUTA_NIVEL)
    clima = leer_csv(RUTA_CLIMA)
    ultimo_nivel = ultima_lectura(nivel, ["distancia_cm", "volumen_litros"])
    ultimo_clima = ultima_lectura(clima, ["temp_exterior", "humedad", "punto_rocio", "presion", "viento_vel", "viento_dir", "lluvia_hora", "radiacion_solar", "uv"])
    data = {
        "actualizado": timestamp_ahora(),
        "nivel": {
            "ultima": ultimo_nivel,
            "serie": serie_temporal(nivel, "volumen_litros")
        },
        "clima": {
            "ultima": ultimo_clima,
            "series": {
                "temperatura": serie_temporal(clima, "temp_exterior"),
                "humedad": serie_temporal(clima, "humedad"),
                "presion": serie_temporal(clima, "presion"),
                "viento_vel": serie_temporal(clima, "viento_vel"),
                "lluvia": serie_temporal(clima, "lluvia_hora"),
                "radiacion_solar": serie_temporal(clima, "radiacion_solar"),
                "uv": serie_temporal(clima, "uv")
            }
        }
    }
    with open(RUTA_JSON, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[OK] dashboard_data.json generado en {RUTA_JSON}")
    return data

if __name__ == "__main__":
    data = generar_dashboard_json()
    print(f"Nivel actual: {data['nivel']['ultima']}")
    print(f"Clima actual: {data['clima']['ultima']}")
