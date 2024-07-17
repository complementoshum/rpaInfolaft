import os
import time
import logging

import pyodbc as py
from dotenv import load_dotenv

load_dotenv()  # Evitar sobrescribir variables

# Configura el logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M'
)

logger = logging.getLogger(__name__)

driver = os.environ.get("DRIVER")
server = os.environ.get("SERVER")
userDb = os.environ.get("USERDB")
passwordDb = os.environ.get("PASSWORDDB")
databaseApp = os.environ.get("DATABASEAPP")


def conSqlAppWeb():
    try:
        connStr = f'DRIVER={driver};SERVER={server};DATABASE={databaseApp};UID={userDb};PWD={passwordDb};TrustServerCertificate=yes'
        connection = py.connect(connStr)
        return connection

    except Exception as e:
        logger.warning(f"Error en la conexión: {repr(e)}")
        time.sleep(30)
        return conSqlAppWeb()