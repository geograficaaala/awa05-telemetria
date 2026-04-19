import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from github import Github, Auth
from scripts.utils import timestamp_ahora

def cargar_token():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    with open(env_path) as f:
        for linea in f:
            if linea.startswith('GITHUB_TOKEN'):
                return linea.strip().split('=')[1]
    raise ValueError('Token no encontrado en .env')

REPO_NAME = "geograficaaala/awa05-telemetria"
RAMA      = "main"

ARCHIVOS = [
    "data/raw/nivel_raw.csv",
    "data/raw/clima_raw.csv",
]

def subir_archivos():
    token = cargar_token()
    g     = Github(auth=Auth.Token(token))
    repo  = g.get_repo(REPO_NAME)
    for ruta_local in ARCHIVOS:
        if not os.path.exists(ruta_local):
            print(f"[SKIP] No existe: {ruta_local}")
            continue
        with open(ruta_local, "r") as f:
            contenido = f.read()
        ruta_github = ruta_local
        try:
            archivo = repo.get_contents(ruta_github, ref=RAMA)
            repo.update_file(
                path    = ruta_github,
                message = f"Actualizacion automatica {timestamp_ahora()}",
                content = contenido,
                sha     = archivo.sha,
                branch  = RAMA
            )
            print(f"[OK] Actualizado: {ruta_github}")
        except Exception:
            repo.create_file(
                path    = ruta_github,
                message = f"Creacion automatica {timestamp_ahora()}",
                content = contenido,
                branch  = RAMA
            )
            print(f"[OK] Creado: {ruta_github}")

if __name__ == "__main__":
    subir_archivos()

def subir_dashboard():
    token = cargar_token()
    g     = Github(auth=Auth.Token(token))
    repo  = g.get_repo(REPO_NAME)
    ruta_local = "data/processed/dashboard_data.json"
    if not os.path.exists(ruta_local):
        print("[SKIP] No existe dashboard_data.json")
        return
    with open(ruta_local, "r") as f:
        contenido = f.read()
    try:
        archivo = repo.get_contents(ruta_local, ref=RAMA)
        repo.update_file(
            path    = ruta_local,
            message = f"[sistema] KPIs Pi {timestamp_ahora()}",
            content = contenido,
            sha     = archivo.sha,
            branch  = RAMA
        )
        print(f"[OK] dashboard_data.json actualizado")
    except Exception:
        repo.create_file(
            path    = ruta_local,
            message = f"[sistema] KPIs Pi {timestamp_ahora()}",
            content = contenido,
            branch  = RAMA
        )
        print(f"[OK] dashboard_data.json creado")
