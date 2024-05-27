import os
import shutil
import tempfile
import time
import glob
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import includes.libs.app as app


# Constants
XPATHS = {
    "inputId": '//*[@id="input_20"]',
    "inputUser": '//*[@id="input_2"]',
    "inputPwd": '//*[@id="input_3"]',
    "btnIngresar": "/html/body/div[2]/div[2]/section/div/div/div[2]/div[1]/div/ng-include/div/div/div[1]/div/div[2]/a",
    "btnReportes": '//*[@id="nav"]/li[3]/ul/li[1]/a/span',
    "btnVerReporte": '//*[@id="content"]/section/standard-view/section/div/div/section/div[2]/ng-transclude/div/div[1]/div/form/div/div[1]/div/div[3]/div/button[1]',
    "btnAdministrar": '//*[@id="content"]/section/standard-view/section/div/div/section/div[2]/ng-transclude/div/div[2]/div/md-table-container/table/tbody/tr/td[10]/md-menu/button/md-icon',
    "btnAdminEntrar": "/html/body/div[5]/md-menu-content",
    "btnBusquedaAdmin": "/html/body/div[2]/div/section/standard-view/section/div/div/section/div[2]/ng-transclude/div/div[3]/div[2]/md-table-container/table/tbody/tr/td[5]/md-menu/button",
    "btnBusquedaDescPDF": "/html/body/div[5]/md-menu-content/md-menu-item[2]/button",
}


class WebAutomation:
    def __init__(self, paramsCons):
        self.paramsCons = paramsCons
        self.driver = None
        self.temp_profile_dir = tempfile.mkdtemp()
        self.setupDriver()

    def setupDriver(self):
        driverDic = {"loadStgy": "", "rutaDescargas": self.paramsCons["rutaDescargas"]}
        self.driver = app.driverRPA(driverDic)
        self.driver.set_window_size(1600, 1080)

    def login(self, usuario, contraseña, intentos=0):
        try:
            waitInputUser = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, XPATHS["inputUser"]))
            )
            waitInputUser.clear()
            waitInputUser.send_keys(usuario)

            waitInputPwd = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, XPATHS["inputPwd"]))
            )
            waitInputPwd.clear()
            waitInputPwd.send_keys(contraseña)

            waitBtnIngresar = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["btnIngresar"]))
            )
            waitBtnIngresar.click()
            return True

        except Exception as e:
            print(f"Error login, intento: {intentos} | {repr(e)}")
            time.sleep(10)
            if intentos < 6:
                return self.login(usuario, contraseña, intentos + 1)
            return False

    def menuReport(self, idConsecutivo):
        waitBtnReportes = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, XPATHS["btnReportes"]))
        )
        waitBtnReportes.click()

        waitInputId = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATHS["inputId"]))
        )
        waitInputId.clear()
        waitInputId.send_keys(idConsecutivo)

        waitBtnVerReporte = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, XPATHS["btnVerReporte"]))
        )
        waitBtnVerReporte.click()

        waitBtnAdministrar = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, XPATHS["btnAdministrar"]))
        )
        waitBtnAdministrar.click()

        waitBtnAdminEntrar = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATHS["btnAdminEntrar"]))
        )
        waitBtnAdminEntrar.click()

        waitBtnBusquedaAdmin = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATHS["btnBusquedaAdmin"]))
        )
        waitBtnBusquedaAdmin.click()

        waitBtnBusquedaDescPDF = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATHS["btnBusquedaDescPDF"]))
        )
        waitBtnBusquedaDescPDF.click()

    def moveFile(self, rutaDescargas, rutaF, nit, intentosPDF):
        while intentosPDF < 10:
            files = glob.glob(os.path.join(rutaDescargas, f"*{nit}*"))
            if files:
                latestFile = max(files, key=os.path.getctime)
                shutil.move(latestFile, os.path.join(rutaF))
                return True
            intentosPDF += 1
            time.sleep(5)
        return False

    def reiniciarRPA(self, e, resultE, contNoti, retryTime):
        print(
            f"Reintentando solicitud {self.paramsCons['idSolicitud']} intento {contNoti + 1} Error: {repr(e)}"
        )
        try:
            self.driver.quit()
        except Exception:
            pass
        time.sleep(retryTime)
        self.setupDriver()  # Reiniciar el driver
        return self.rpa(resultE, contNoti + 1)

    def rpa(self, resultE, contNoti=0):
        intentosPDF = 0
        if app.listaActiva({"idLista": self.paramsCons["idLista"]}):
            try:
                paginaDisponible = app.esperaCargaPagina(
                    self.driver, self.paramsCons["urlLista"], XPATHS["btnIngresar"]
                )

                if not paginaDisponible:
                    return self.reiniciarRPA(
                        Exception("Página no disponible"),
                        resultE,
                        contNoti,
                        self.paramsCons["reintentosEspera"],
                    )

                app.removeFileIfExist(self.paramsCons["rutaDocumento"])

                if not self.login(
                    self.paramsCons["usuarioLogin"], self.paramsCons["contraseñaLogin"]
                ):
                    return self.reiniciarRPA(
                        Exception("Login fallido"),
                        resultE,
                        contNoti,
                        self.paramsCons["reintentosEspera"],
                    )

                self.menuReport(self.paramsCons["idConsecutivo"])

                if self.moveFile(
                    self.paramsCons["rutaDescargas"],
                    self.paramsCons["rutaDocumento"],
                    self.paramsCons["nit"],
                    intentosPDF,
                ):
                    resultE.update({"urlResultado": self.paramsCons["rutaDocumento"]})
                else:
                    return self.reiniciarRPA(
                        Exception("Descarga de PDF fallida"),
                        resultE,
                        contNoti,
                        self.paramsCons["reintentosEspera"],
                    )

                self.driver.quit()
            except Exception as e:
                return self.reiniciarRPA(
                    e, resultE, contNoti, self.paramsCons["reintentosEspera"]
                )
        return resultE
