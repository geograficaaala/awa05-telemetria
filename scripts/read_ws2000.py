import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask, request
from scripts.utils import timestamp_ahora, guardar_csv

app = Flask(__name__)

RUTA_CLIMA = "data/raw/clima_raw.csv"

@app.route("/data", methods=["POST", "GET"])
def recibir_datos():
    datos = request.args if request.method == "GET" else request.form
    if not datos:
        return "Sin datos", 400

    fila = {
        "timestamp":        timestamp_ahora(),
        "temp_exterior":    datos.get("tempf",    "N/A"),
        "humedad":          datos.get("humidity", "N/A"),
        "punto_rocio":      datos.get("dewptf",   "N/A"),
        "presion":          datos.get("baromin",  "N/A"),
        "viento_vel":       datos.get("windspeedmph", "N/A"),
        "viento_dir":       datos.get("winddir",  "N/A"),
        "lluvia_hora":      datos.get("rainin",   "N/A"),
        "radiacion_solar":  datos.get("solarradiation", "N/A"),
        "uv":               datos.get("UV",       "N/A"),
    }

    guardar_csv(RUTA_CLIMA, fila)
    print(f"[WS2000] Datos recibidos: temp={fila['temp_exterior']} humedad={fila['humedad']}")
    return "OK", 200

@app.route("/", methods=["GET"])
def estado():
    return "Servidor AWA05 activo", 200

def iniciar_servidor():
    app.run(host="0.0.0.0", port=7777, debug=False)

if __name__ == "__main__":
    iniciar_servidor()
