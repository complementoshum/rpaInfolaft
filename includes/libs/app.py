import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime

import requests
import threading

import includes.mstrs.queryMstr as qMstr

load_dotenv()  # Evitar sobrescribir variables

now = datetime.now()
dateToday = now.strftime("%Y-%m-%d %H:%M:%S")

timeWaitLoadPage = float(os.environ.get("TIEMPOMAXCARGAPAGINA"))
maxRetry = int(os.environ.get("REINTENTOSCARGAPAGINA"))

bloqueoHilos = threading.Lock()


def driverRPA(driverDic):
    driver = None
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument('--headless=new')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--start-fullscreen')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--password-store=basic")
    options.add_argument("--enable-automation")  # necesario para automatizar
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
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
    listaActivaCon = None
    estadoListaCon = None
    listaActivaCon = qMstr.getEstadoLista(listasRiesgo)
    estadoListaCon = listaActivaCon[0]["estado"]
    estadoListaActiva = os.environ.get("LISTAACTIVA")
    if str(estadoListaCon) == str(estadoListaActiva):
        return True

    print("La lista no esta 'ACTIVA', la consulta no sera realizada ")
    return False


def esperaCargaPagina(driver, url, campoBuscar, intentos=0):
    urlP = None
    try:
        urlP = url
        driver.get(urlP)
        WebDriverWait(driver, timeWaitLoadPage).until(
            EC.presence_of_element_located((By.XPATH, campoBuscar))
        )
        return True

    except Exception as e:
        print("Error Cargando Pagina, ", repr(e))
        if intentos < maxRetry:
            return esperaCargaPagina(driver, url, campoBuscar, intentos + 1)

        return False


def eliminarArchivosExist(ruta):
    while os.path.exists(ruta):
        os.remove(ruta)
        return True
