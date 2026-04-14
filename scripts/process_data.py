import csv
import json
import os
from datetime import datetime
from scripts.utils import timestamp_ahora

def calcular_promedio_horario(ruta_csv):
    """Lee el CSV crudo y calcula promedios por hora."""
    registros = {}
    if not os.path.exists(ruta_csv):
        return {}
    with open(ruta_csv, 'r') as f:
        reader = csv.DictReader(f)
        for fila in reader:
            hora = fila['timestamp'][:13]
            if hora not in registros:
                registros[hora] = []
            registros[hora].append(float(fila['peso_kg']))
    promedios = {}
    for hora, valores in registros.items():
        promedios[hora] = round(sum(valores) / len(valores), 3)
    return promedios

def generar_dashboard_json(promedios, ruta_salida):
    """Genera el archivo JSON para el dashboard."""
    data = {
        "actualizado": timestamp_ahora(),
        "datos": [{"hora": h, "peso_kg": v} for h, v in promedios.items()]
    }
    with open(ruta_salida, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Dashboard JSON generado en {ruta_salida}")

if __name__ == "__main__":
    promedios = calcular_promedio_horario("data/raw/peso_raw.csv")
    print(f"Promedios calculados: {promedios}")
EOF 
