import os
import time

import pyodbc as py
from dotenv import load_dotenv

load_dotenv()  # Evitar sobrescribir variables

driver = os.environ.get("DRIVER")
server = os.environ.get("SERVER")
userDb = os.environ.get("USERDB")
passwordDb = os.environ.get("PASSWORDDB")
databaseApp = os.environ.get("DATABASEAPP")


def conSqlAppWeb():
    try:
        conn_str = f'DRIVER={driver};SERVER={server};DATABASE={databaseApp};UID={userDb};PWD={passwordDb};TrustServerCertificate=yes'
        connection = py.connect(conn_str)
        return connection

    except Exception as e:
        print(repr(e))
        time.sleep(30)
        return conSqlAppWeb()