from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import tempfile
import time
import glob
import os
import shutil

import includes.libs.app as app

temp_profile_dir = tempfile.mkdtemp()

inputdId = '//*[@id="input_20"]'
inputUser = '//*[@id="input_2"]'
inputdPWd = '//*[@id="input_3"]'
btnIngresar = '/html/body/div[2]/div[2]/section/div/div/div[2]/div[1]/div/ng-include/div/div/div[1]/div/div[2]/a'
btnReportes = '//*[@id="nav"]/li[3]/ul/li[1]/a/span'
btnVerReporte = '//*[@id="content"]/section/standard-view/section/div/div/section/div[2]/ng-transclude/div/div[1]/div/form/div/div[1]/div/div[3]/div/button[1]'
btnAdministrar = '//*[@id="content"]/section/standard-view/section/div/div/section/div[2]/ng-transclude/div/div[2]/div/md-table-container/table/tbody/tr/td[10]/md-menu/button/md-icon'
btnAdminEntrar = "/html/body/div[5]/md-menu-content"
btnBusquedaAdmin = "/html/body/div[2]/div/section/standard-view/section/div/div/section/div[2]/ng-transclude/div/div[3]/div[2]/md-table-container/table/tbody/tr/td[5]/md-menu/button"
btnBusquedaDescPDF = "/html/body/div[5]/md-menu-content/md-menu-item[2]/button"


def rpa(
    resultE,
    paramsCons,
    contNoti=0,
):
    nit = None
    rutaDescargas = None
    idSolicitud = None
    waitInputId = None
    waitInputPwd = None
    waitInputUser = None
    waitBtnAdminEntrar = None
    waitBtnAdministrar = None
    waitBtnBusquedaAdmin = None
    waitBtnIngresar = None
    waitBtnReportes = None
    waitBtnVerReporte = None
    driver = None
    urlF = None
    download = None
    usuarioLog = None
    retryTime = None
    passwordLog = None
    idConsecutivo = None
    rutaF = None
    idLista = None
    driverDic = {"loadStgy": "", "rutaDescargas": ""}
    dicListaRiesgo = {"idLista": None}
    rutaDescargas = paramsCons["rutaDescargas"]
    idSolicitud = paramsCons["idSolicitud"]
    idLista = paramsCons["idLista"]
    dicListaRiesgo.update({"idLista": idLista})
    driverDic.update({"rutaDescargas": rutaDescargas})
    if app.listaActiva(dicListaRiesgo):
        try:
            nit = paramsCons["nit"]
            rutaF = paramsCons["rutaDocumento"]
            usuarioLog = paramsCons["usuarioLogin"]
            passwordLog = paramsCons["contraseñaLogin"]
            idConsecutivo = paramsCons["idConsecutivo"]
            retryTime = paramsCons["reintentosEspera"]
            driver = app.driverRPA(driverDic)
            driver.set_window_size(1600, 1080)
            urlF = paramsCons["urlLista"]

            paginaDisponible = app.esperaCargaPagina(driver, urlF, inputUser)
            if not paginaDisponible:
                print(f"Reintentando en Solicitud {idSolicitud} ")
                driver.quit()
                time.sleep(retryTime)
                return rpa(
                    resultE,
                    paramsCons,
                    contNoti + 1,
                )

            app.eliminarArchivosExist(rutaF)

            try:
                waitInputUser = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, inputUser))
                )
                waitInputUser.send_keys(usuarioLog)
                driver.save_screenshot(rutaF)
                waitInputPwd = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, inputdPWd))
                )
                waitInputPwd.send_keys(passwordLog)
                waitBtnIngresar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, btnIngresar))
                )
                waitBtnIngresar.click()
                print("login")
                waitBtnReportes = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, btnReportes))
                )
                waitBtnReportes.click()
                print("reportes")
                waitInputId = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, inputdId))
                )
                waitInputId.send_keys(idConsecutivo)
                print("consecutivo")

                waitBtnVerReporte = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, btnVerReporte))
                )
                waitBtnVerReporte.click()
                print("ver reporte")

                waitBtnAdministrar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, btnAdministrar))
                )
                waitBtnAdministrar.click()
                print("administrar")

                waitBtnAdminEntrar = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, btnAdminEntrar))
                )
                waitBtnAdminEntrar.click()
                print("admin entrar")

                waitBtnBusquedaAdmin = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, btnBusquedaAdmin))
                )
                waitBtnBusquedaAdmin.click()
                print("busqueda admin")

            except Exception as e:
                print(e)
                driver.quit()
                time.sleep(retryTime)
                return rpa(
                    resultE,
                    paramsCons,
                    contNoti + 1,
                )

            waitBtnBusquedaDescPDF = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, btnBusquedaDescPDF))
            )
            waitBtnBusquedaDescPDF.click()

            while True:
                # Buscar archivos que contengan la parte específica del nit en la carpeta
                files = glob.glob(os.path.join(rutaDescargas, f"*{nit}*"))
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    new_path = rutaF  # Ruta de destino para mover el archivo
                    os.rename(latest_file, os.path.join(new_path))
                    break

                time.sleep(1)  # Espera antes de volver a verificar

            resultE.update(
                {
                    "urlResultado": rutaF,
                }
            )

            try:
                driver.quit()
            except:
                pass

            return resultE

        except Exception as e:
            print(repr(e))
