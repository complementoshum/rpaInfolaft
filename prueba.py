import time
import os
import glob
import random
from concurrent.futures import ThreadPoolExecutor

def procesarSolicitud(user):
    # Lógica para procesar la solicitud
    # Agregar la lógica para observar las descargas aquí
    folder = f'/ruta/a/documento{user}'  # Ruta a la carpeta de descargas específica para este usuario
    partial_name = 'parte_del_nombre'  # Parte del nombre del archivo que estás buscando

    while True:
        # Buscar archivos que contengan la parte específica del nombre en la carpeta de descargas
        files = glob.glob(os.path.join(folder, f"*{partial_name}*"))
        if files:
            # Suponiendo que solo estamos interesados en el último archivo encontrado
            latest_file = max(files, key=os.path.getctime)
            print(f"Usuario {user}: Nuevo archivo descargado: {latest_file}")
            # Puedes hacer lo que necesites con el nombre del archivo aquí
        time.sleep(1)  # Espera antes de volver a verificar

# Lista de usuarios
userP = [1, 2, 3]

# Iniciar ThreadPoolExecutor
with ThreadPoolExecutor() as executor:
    randomTimeSleep = random.uniform(0, 5)
    time.sleep(randomTimeSleep)
    # Ejecutar procesarSolicitud para cada usuario
    ejecutado = list(executor.map(procesarSolicitud, userP))
