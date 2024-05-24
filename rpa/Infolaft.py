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
    "input_id": '//*[@id="input_20"]',
    "input_user": '//*[@id="input_2"]',
    "input_pwd": '//*[@id="input_3"]',
    "btn_ingresar": "/html/body/div[2]/div[2]/section/div/div/div[2]/div[1]/div/ng-include/div/div/div[1]/div/div[2]/a",
    "btn_reportes": '//*[@id="nav"]/li[3]/ul/li[1]/a/span',
    "btn_ver_reporte": '//*[@id="content"]/section/standard-view/section/div/div/section/div[2]/ng-transclude/div/div[1]/div/form/div/div[1]/div/div[3]/div/button[1]',
    "btn_administrar": '//*[@id="content"]/section/standard-view/section/div/div/section/div[2]/ng-transclude/div/div[2]/div/md-table-container/table/tbody/tr/td[10]/md-menu/button/md-icon',
    "btn_admin_entrar": "/html/body/div[5]/md-menu-content",
    "btn_busqueda_admin": "/html/body/div[2]/div/section/standard-view/section/div/div/section/div[2]/ng-transclude/div/div[3]/div[2]/md-table-container/table/tbody/tr/td[5]/md-menu/button",
    "btn_busqueda_desc_pdf": "/html/body/div[5]/md-menu-content/md-menu-item[2]/button",
}

class WebAutomation:
    def __init__(self, params_cons):
        self.params_cons = params_cons
        self.driver = None
        self.temp_profile_dir = tempfile.mkdtemp()
        self.setup_driver()

    def setup_driver(self):
        driver_dic = {"loadStgy": "", "rutaDescargas": self.params_cons["rutaDescargas"]}
        self.driver = app.driverRPA(driver_dic)
        self.driver.set_window_size(1600, 1080)

    def login(self, usuario, contraseña, intentos=0):
        try:
            wait_input_user = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, XPATHS["input_user"]))
            )
            wait_input_user.clear()
            wait_input_user.send_keys(usuario)

            wait_input_pwd = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, XPATHS["input_pwd"]))
            )
            wait_input_pwd.clear()
            wait_input_pwd.send_keys(contraseña)

            wait_btn_ingresar = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["btn_ingresar"]))
            )
            wait_btn_ingresar.click()
            return True

        except Exception as e:
            print(f"Error login, intento: {intentos} | {repr(e)}")
            time.sleep(10)
            if intentos < 6:
                return self.login(usuario, contraseña, intentos + 1)
            return False

    def navigate_to_report(self, id_consecutivo):
        wait_btn_reportes = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, XPATHS["btn_reportes"]))
        )
        wait_btn_reportes.click()

        wait_input_id = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATHS["input_id"]))
        )
        wait_input_id.clear()
        wait_input_id.send_keys(id_consecutivo)

        wait_btn_ver_reporte = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, XPATHS["btn_ver_reporte"]))
        )
        wait_btn_ver_reporte.click()

        wait_btn_administrar = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, XPATHS["btn_administrar"]))
        )
        wait_btn_administrar.click()

        wait_btn_admin_entrar = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATHS["btn_admin_entrar"]))
        )
        wait_btn_admin_entrar.click()

        wait_btn_busqueda_admin = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATHS["btn_busqueda_admin"]))
        )
        wait_btn_busqueda_admin.click()

        wait_btn_busqueda_desc_pdf = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, XPATHS["btn_busqueda_desc_pdf"]))
        )
        wait_btn_busqueda_desc_pdf.click()

    def move_downloaded_file(self, ruta_descargas, ruta_f, nit, intentos_pdf):
        while intentos_pdf < 10:
            files = glob.glob(os.path.join(ruta_descargas, f"*{nit}*"))
            if files:
                latest_file = max(files, key=os.path.getctime)
                shutil.move(latest_file, os.path.join(ruta_f))
                return True
            intentos_pdf += 1
            time.sleep(5)
        return False

    def handle_exceptions(self, e, resultE, cont_noti, retry_time):
        print(f"Reintentando solicitud {self.params_cons['idSolicitud']} intento {cont_noti + 1} Error: {repr(e)}")
        try:
            self.driver.quit()
        except Exception:
            pass
        time.sleep(retry_time)
        return self.run_rpa(resultE, cont_noti + 1)

    def run_rpa(self, resultE, cont_noti=0):
        intentos_pdf = 0
        if app.listaActiva({"idLista": self.params_cons["idLista"]}):
            try:
                pagina_disponible = app.esperaCargaPagina(self.driver, self.params_cons["urlLista"], XPATHS["btn_ingresar"])

                if not pagina_disponible:
                    return self.handle_exceptions(Exception("Página no disponible"), resultE, cont_noti, self.params_cons["reintentosEspera"])

                app.eliminarArchivosExist(self.params_cons["rutaDocumento"])

                if not self.login(self.params_cons["usuarioLogin"], self.params_cons["contraseñaLogin"]):
                    return self.handle_exceptions(Exception("Login fallido"), resultE, cont_noti, self.params_cons["reintentosEspera"])

                self.navigate_to_report(self.params_cons["idConsecutivo"])

                if self.move_downloaded_file(self.params_cons["rutaDescargas"], self.params_cons["rutaDocumento"], self.params_cons["nit"], intentos_pdf):
                    resultE.update({"urlResultado": self.params_cons["rutaDocumento"]})
                else:
                    return self.handle_exceptions(Exception("Descarga de PDF fallida"), resultE, cont_noti, self.params_cons["reintentosEspera"])

                self.driver.quit()
            except Exception as e:
                return self.handle_exceptions(e, resultE, cont_noti, self.params_cons["reintentosEspera"])
        return resultE

