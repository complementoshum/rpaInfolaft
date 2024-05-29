import os
import time
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import threading
import includes.mstrs.queryMstr as qMstr

# Configuración de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()  # Cargar variables de entorno

now = datetime.now()
dateToday = now.strftime("%Y-%m-%d %H:%M:%S")

timeWaitLoadPage = float(os.getenv("TIEMPOMAXCARGAPAGINA", 10))
maxRetry = int(os.getenv("REINTENTOSCARGAPAGINA", 3))

bloqueoHilos = threading.Lock()


def driverRPA(driverDic):
    driver = None
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--password-store=basic")
    options.add_argument("--enable-automation")
    options.add_argument("--disable-logging")

    options.add_experimental_option(
        "excludeSwitches", ["enable-automation", "enable-logging"]
    )
    options.add_experimental_option("useAutomationExtension", False)
    chrome_prefs = {
        "download.default_directory": os.environ.get("RUTAPROYECTO")
    }  # DOCKER
    options.experimental_options["prefs"] = chrome_prefs
    if not driverDic["loadStgy"]:
        driverDic["loadStgy"] = "normal"
    options.page_load_strategy = driverDic["loadStgy"]
    driver = webdriver.Chrome(service=Service(), options=options)
    time.sleep(2)
    return driver


def listaActiva(listasRiesgo):
    estadoListaCon = qMstr.getEstadoLista(listasRiesgo)[0]["estado"]
    estadoListaActiva = os.getenv("LISTAACTIVA")

    if str(estadoListaCon) == str(estadoListaActiva):
        return True

    logging.info("La lista no está 'ACTIVA', la consulta no será realizada.")
    return False


def esperaCargaPagina(driver, url, campoBuscar, timeWaitLoadPage=10, maxRetry=3):
    for intento in range(maxRetry):
        try:
            driver.get(url)
            WebDriverWait(driver, timeWaitLoadPage).until(
                EC.element_to_be_clickable((By.XPATH, campoBuscar))
            )
            return True
        except TimeoutException:
            logging.warning(
                f"Tiempo de espera excedido al cargar la página. Intento {intento + 1} de {maxRetry}"
            )
        except Exception as e:
            logging.error(f"Error al cargar la página: {repr(e)}")
            return False
    logging.error("Se alcanzó el número máximo de intentos")
    return False


def removeFileIfExist(ruta):
    try:
        if os.path.exists(ruta):
            os.remove(ruta)
            return True
        return False
    except Exception as e:
        logging.error(f"Error al eliminar el archivo: {repr(e)}")
        return False

