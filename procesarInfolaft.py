import random
import time
import os
import threading
import concurrent.futures
import asyncio
import importlib

from telegram import Bot
from dotenv import load_dotenv

import includes.libs.app as app
import includes.mstrs.queryMstr as qMstr

load_dotenv()  # Evitar sobrescribir variables


class RPAConfig:
    def __init__(self):
        self.estadoV = os.environ.get("ESTADOVALIDANDO")
        self.estadoF = os.environ.get("ESTADOFINALIZADO")
        self.appRPA = os.environ.get("APPRPA")
        self.modRPA = os.environ.get("MODRPA")
        self.rutaFs = os.environ.get("RUTAFS")
        self.rutaDescargas = os.environ.get("RUTAPROYECTO")
        self.retryTime = int(os.environ.get("TIEMPOREINTENTOS"))
        self.botToken = str(os.environ.get("TELEGRAMBOT"))
        self.chatIds = str(os.environ.get("TELEGRAMID")).split(",")
        self.msgTelegram = (
            "Ocurrió un error general en la ejecución del RPA de infolaft: "
        )
        self.maxSolicitudes = int(os.environ.get("CANTIDADMAXSOL"))
        self.semaphore = threading.Semaphore(self.maxSolicitudes)
        self.lock = threading.Lock()


class RPAMain:
    def __init__(self, config):
        self.config = config

    def maxSolicitudes(self):
        cantidadV = qMstr.getSolicitudesV()
        cantidadF = cantidadV[0]["cantidad"]
        return cantidadF < self.config.maxSolicitudes

    def updEstadoSolicitud(self, idSolicitud, estadoSol, mensajeError):
        estado = None
        updateFunction = None
        updFuncionName = None
        updSolicitud = None
        updEstado = None

        if estadoSol == self.config.estadoF:
            estado = self.config.estadoF
            updFuncionName = "updEstadoSolicitudFinalizada"
        else:
            # Si el estado no es 'F', se valida si se puede continuar.
            if self.maxSolicitudes():
                estado = self.config.estadoV
                updFuncionName = "updEstadoSolicitud"
            else:
                return None

        try:
            updEstado = {
                "estado": estado,
                "idSolicitud": idSolicitud,
                "mensajeError": mensajeError,
            }

            updateFunction = getattr(qMstr, updFuncionName)
            updSolicitud = updateFunction(updEstado)
            return updSolicitud
        except AttributeError:
            print(f"La funcion {updFuncionName} no existe.")
            return None
        except Exception as e:
            print(f"Ocurrio un error al momento de actualizar el estado: {e}")
            return None

    def procesarLista(self, user, listaRiesgo):
        perNit = None
        perIdSolicitud = None
        idConsecutivo = None
        idBd = None
        listId = None
        listNombre = None
        listUrl = None
        listUserLogin = None
        listPwdLogin = None
        bdName = None
        rutaScr = None
        rutaDoc = None
        varImportRpa = None
        infolaft = None
        rpaDatosDic = {
            "nit": None,
            "idSolicitud": None,
            "idLista": None,
            "listNombre": None,
            "urlLista": None,
            "usuarioLogin": None,
            "contraseñaLogin": None,
            "msgNoResultado": None,
            "rutaDocumento": None,
            "reintentosEspera": None,
            "siteCaptchaKey": None,
        }

        resultE = {
            "idSolicitud": None,
            "idLista": None,
            "urlResultado": None,
        }

        try:
            perNit = user["nit"]
            perIdSolicitud = user["id"]
            idConsecutivo = user["idInfolaft"]
            idBd = user["idBd"]
            listId = listaRiesgo["idLista"]
            listNombre = listaRiesgo["nombre"]
            listUrl = listaRiesgo["urlLista"]
            listUserLogin = listaRiesgo["userLogin"]
            listPwdLogin = listaRiesgo["passwordLogin"]

            bdName = qMstr.getConecInfo({"idBd": idBd})
            rutaScr = os.path.join(
                self.config.rutaFs,
                bdName["bd"],
                "infolaft",
                perNit,
                str(perIdSolicitud),
            )
            if not os.path.exists(rutaScr):
                os.makedirs(rutaScr)

            rutaDoc = os.path.join(rutaScr, f"{listId}_{perNit}.pdf")
            varImportRpa = importlib.import_module(f"rpa.{listNombre}")
            rpaDatosDic.update(
                {
                    "nit": perNit,
                    "idSolicitud": perIdSolicitud,
                    "idConsecutivo": idConsecutivo,
                    "idLista": listId,
                    "listNombre": listNombre,
                    "urlLista": listUrl,
                    "usuarioLogin": listUserLogin,
                    "contraseñaLogin": listPwdLogin,
                    "rutaDocumento": rutaDoc,
                    "rutaDescargas": self.config.rutaDescargas,
                    "reintentosEspera": self.config.retryTime,
                }
            )
            resultE.update(
                {
                    "idSolicitud": perIdSolicitud,
                    "idLista": listId,
                    "urlResultado": None,
                }
            )
            infolaft = varImportRpa.WebAutomation(rpaDatosDic)
            return infolaft.rpa(resultE)
        except Exception as e:
            print(f"Error processing document: {e}")
            return None

    def procesarSolicitud(self, user):
        mensajeError = None
        try:
            idSolicitud = user["id"]
            if self.maxSolicitudes():
                with self.config.semaphore:
                    if self.updEstadoSolicitud(
                        idSolicitud, self.config.estadoV, mensajeError
                    ):
                        print(f"Inicia RPA PDF Infolaft #{idSolicitud}")

                        listaRiesgo = qMstr.getListaT()
                        for lista in listaRiesgo:
                            resultado = self.procesarLista(user, lista)
                            if resultado and "urlResultado" in resultado:
                                qMstr.insertResultado(
                                    {
                                        "idSolicitud": user["id"],
                                        "idLista": lista["idLista"],
                                        "urlResultado": resultado["urlResultado"],
                                    }
                                )
                        print(f"Finaliza RPA PDF Infolaft Solicitud {idSolicitud}")
                        self.updEstadoSolicitud(
                            idSolicitud, self.config.estadoF, mensajeError
                        )
        except Exception as e:
            mensajeError = f"{self.config.msgTelegram}{repr(e)}"
            self.enviarMsgTelegram(mensajeError)
            self.updEstadoSolicitud(user["id"], self.config.estadoF, mensajeError)

    async def enviarMensaje(self, token, chatId, mensaje):
        bot = Bot(token)
        await bot.send_message(chatId=chatId, text=mensaje)

    def enviarMsgTelegram(self, mensaje):
        for chatId in self.config.chatIds:
            asyncio.run(self.enviarMensaje(self.config.botToken, chatId, mensaje))


def ejecutarRPA():
    configRPA = RPAConfig()
    procesarRPA = RPAMain(configRPA)

    if procesarRPA.maxSolicitudes():
        solicitudP = {"estado": os.environ.get("ESTADOPENDIENTE")}
        userP = qMstr.getSolicitud(solicitudP)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            time.sleep(random.uniform(0, 5))
            executor.map(procesarRPA.procesarSolicitud, userP)


if __name__ == "__main__":
    ejecutarRPA()
