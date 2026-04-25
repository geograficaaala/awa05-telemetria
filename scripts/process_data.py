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


def estado_sistema():
    import subprocess, re
    try:
        temp = float(re.search(r"temp=([\d.]+)", subprocess.check_output(["vcgencmd","measure_temp"]).decode()).group(1))
    except: temp = None
    try:
        volt = float(re.search(r"volt=([\d.]+)", subprocess.check_output(["vcgencmd","measure_volts"]).decode()).group(1))
    except: volt = None
    try:
        mem = open("/proc/meminfo").read()
        total = int(re.search(r"MemTotal:\s+(\d+)", mem).group(1))
        available = int(re.search(r"MemAvailable:\s+(\d+)", mem).group(1))
        ram_pct = round((total - available) / total * 100, 1)
    except: ram_pct = None
    try:
        st = os.statvfs("/")
        disco_pct = round((1 - st.f_bavail / st.f_blocks) * 100, 1)
    except: disco_pct = None
    try:
        uptime_s = float(open("/proc/uptime").read().split()[0])
        h, m = divmod(int(uptime_s // 60), 60)
        uptime = f"{h}h {m}m"
    except: uptime = None
    return {"cpu_temp_c": temp, "voltaje_v": volt, "ram_uso_pct": ram_pct, "disco_uso_pct": disco_pct, "uptime": uptime}

def generar_dashboard_json():
    os.makedirs("data/processed", exist_ok=True)
    nivel = leer_csv(RUTA_NIVEL)
    clima = leer_csv(RUTA_CLIMA)
    limite = 9999
    nivel_r = nivel[-limite:]
    clima_r = clima[-limite:]

    # Filtro outliers: no puede bajar menos de 5L (salvo vaciado) ni subir mas de 6L
    nivel_filtrado = []
    for i, row in enumerate(nivel_r):
        try:
            vol = float(row["volumen_litros"])
        except:
            nivel_filtrado.append(row)
            continue
        if i == 0:
            nivel_filtrado.append(row)
            continue
        prev_vol = float(nivel_filtrado[-1]["volumen_litros"])
        diff = vol - prev_vol
        if diff > 6:          # pico exagerado hacia arriba
            row = dict(row)
            row["volumen_litros"] = str(prev_vol)
        elif diff < 0 and diff > -5:  # baja poco = outlier por viento
            row = dict(row)
            row["volumen_litros"] = str(prev_vol)
        nivel_filtrado.append(row)
    nivel_r = nivel_filtrado
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
        "sistema": estado_sistema(),
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
