import json
import os

DB_FILE = "historial_inspeccions.json"

def guardar_historial_local(historial):
    with open(DB_FILE, "w") as f:
        json.dump(historial, f)

def carregar_historial_local():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []