import csv
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.utils import timestamp_ahora

RUTA_NIVEL = "data/raw/nivel_raw.csv"
RUTA_CLIMA = "data/raw/clima_raw.csv"
RUTA_JSON  = "data/processed/dashboard_data.json"

def f_a_c(f):
    try: return round((float(f) - 32) * 5 / 9, 1)
    except: return None

def mph_a_kmh(v):
    try: return round(float(v) * 1.60934, 1)
    except: return None

def leer_csv(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r") as f:
        return list(csv.DictReader(f))

def generar_dashboard_json():
    os.makedirs("data/processed", exist_ok=True)
    nivel = leer_csv(RUTA_NIVEL)
    clima = leer_csv(RUTA_CLIMA)
    limite = 24
    nivel_r = nivel[-limite:]
    clima_r = clima[-limite:]
    labels = [f["timestamp"][11:16] for f in clima_r] if clima_r else [f["timestamp"][11:16] for f in nivel_r]
    nivel_l = [round(float(f["volumen_litros"]), 2) for f in nivel_r if f.get("volumen_litros")]
    while len(nivel_l) < len(labels):
        nivel_l.insert(0, None)
    humedad  = [round(float(f["humedad"]), 1) for f in clima_r if f.get("humedad") and f["humedad"] != "N/A"]
    temp_c   = [f_a_c(f["temp_exterior"]) for f in clima_r if f.get("temp_exterior") and f["temp_exterior"] != "N/A"]
    rocio_c  = [f_a_c(f["punto_rocio"]) for f in clima_r if f.get("punto_rocio") and f["punto_rocio"] != "N/A"]
    presion  = [round(float(f["presion"]), 3) for f in clima_r if f.get("presion") and f["presion"] != "N/A"]
    viento   = [mph_a_kmh(f["viento_vel"]) for f in clima_r if f.get("viento_vel") and f["viento_vel"] != "N/A"]
    dir_v    = [round(float(f["viento_dir"]), 0) for f in clima_r if f.get("viento_dir") and f["viento_dir"] != "N/A"]
    lluvia   = [round(float(f["lluvia_hora"]), 2) for f in clima_r if f.get("lluvia_hora") and f["lluvia_hora"] != "N/A"]
    solar    = [round(float(f["radiacion_solar"]), 1) for f in clima_r if f.get("radiacion_solar") and f["radiacion_solar"] != "N/A"]
    uv       = [round(float(f["uv"]), 1) for f in clima_r if f.get("uv") and f["uv"] != "N/A"]
    ultima_nivel  = nivel[-1] if nivel else {}
    ultima_clima  = clima[-1] if clima else {}
    kpis = {
        "nivel_l":            round(float(ultima_nivel.get("volumen_litros", 0)), 2) if ultima_nivel else None,
        "humedad_pct":        round(float(ultima_clima.get("humedad", 0)), 1) if ultima_clima else None,
        "temp_c":             f_a_c(ultima_clima.get("temp_exterior")) if ultima_clima else None,
        "punto_rocio_c":      f_a_c(ultima_clima.get("punto_rocio")) if ultima_clima else None,
        "presion_inhg":       round(float(ultima_clima.get("presion", 0)), 3) if ultima_clima else None,
        "viento_kmh":         mph_a_kmh(ultima_clima.get("viento_vel")) if ultima_clima else None,
        "viento_dir_deg":     round(float(ultima_clima.get("viento_dir", 0)), 0) if ultima_clima else None,
        "lluvia_hora_mm":     round(float(ultima_clima.get("lluvia_hora", 0)), 2) if ultima_clima else None,
        "radiacion_solar_wm2":round(float(ultima_clima.get("radiacion_solar", 0)), 1) if ultima_clima else None,
        "uv":                 round(float(ultima_clima.get("uv", 0)), 1) if ultima_clima else None
    }
    data = {
        "actualizado": timestamp_ahora(),
        "kpis": kpis,
        "series": {
            "labels":              labels,
            "nivel_l":             nivel_l,
            "humedad_pct":         humedad,
            "temp_c":              temp_c,
            "punto_rocio_c":       rocio_c,
            "presion_inhg":        presion,
            "viento_kmh":          viento,
            "viento_dir_deg":      dir_v,
            "lluvia_hora_mm":      lluvia,
            "radiacion_solar_wm2": solar,
            "uv":                  uv
        }
    }
    with open(RUTA_JSON, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[OK] dashboard_data.json generado: {timestamp_ahora()}")
    return data

if __name__ == "__main__":
    data = generar_dashboard_json()
    print(f"KPIs: {data['kpis']}")
