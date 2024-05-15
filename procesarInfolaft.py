import importlib
import os
import threading
import concurrent.futures
import asyncio

from telegram import Bot
from twocaptcha import TwoCaptcha
from dotenv import load_dotenv

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import tempfile
import random
import time

import includes.libs.app as app
import includes.mstrs.queryMstr as qMstr


load_dotenv()  # Evitar sobrescribir variables
envApiCaptcha = TwoCaptcha(os.environ.get("CAPTCHAKEY"))
envEstadoV = os.environ.get("ESTADOVALIDANDO")
envEstadoF = os.environ.get("ESTADOFINALIZADO")
envAppRPA = os.environ.get("APPRPA")
envModRPA = os.environ.get("MODRPA")
envRutaFS = os.environ.get("RUTAFS")
envRutaDescargas = os.environ.get("RUTAPROYECTO")
envRetryTime = int(os.environ.get("TIEMPOREINTENTOS"))
botToken = str(os.environ.get("TELEGRAMBOT"))
chatIdComp = str(os.environ.get("TELEGRAMID"))
chatIds = chatIdComp.split(",")
msgTelegram = "Ocurrió un error general en la ejecución del RPA de infolaft: "

glbRutaS = {"rutaDescargas": envRutaDescargas, "rutaDoc": None}

sem = threading.Semaphore(int(os.environ.get("CANTIDADMAXSOL")))
bloqueoHilos = threading.Lock()



def maxDocumentos():
    cantidadF = None
    cantidadSol = None
    cantidadV = None
    cantidadSol = int(os.environ.get("CANTIDADMAXSOL"))
    cantidadV = qMstr.getSolicitudesV()
    cantidadF = cantidadV[0]["cantidad"]
    if cantidadF < cantidadSol:
        return True

    else:
        return False



def updEstadoDocumento(idSolicitudP, usrRegistraP, estadoVal, audApp, audMod):
    usrRegistra = None
    estadoV = None
    auditoria = None
    updDocumento = None
    updDisponible = None
    idSolicitud = None
    updEstadoV = {
        "estado": None,
        "idSolicitud": None,
        "mensajeError": None,
    }
    auditoria = {
        "accion": None,
        "usr": None,
        "app": None,
        "modName": None,
    }
    updDisponible = maxDocumentos()

    if updDisponible:
        try:
            usrRegistra = usrRegistraP
            idSolicitud = idSolicitudP
            estadoV = estadoVal
            appRPA = audApp
            modRPA = audMod
            updEstadoV.update(
                {
                    "estado": estadoV,
                    "idSolicitud": idSolicitud,
                    "mensajeError": None,
                }
            )
            updDocumento = qMstr.updEstadoDocs(updEstadoV)
            auditoria.update(
                {
                    "accion": f"UPD - Estado Solicitud {idSolicitud} - {estadoV}",
                    "usr": usrRegistra,
                    "app": appRPA,
                    "modName": modRPA,
                }
            )
            return updDocumento

        except:
            return updDocumento

    return updDocumento


def procesarDocumento(
    rutaFS,
    listaRiesgo,
    user,
    retryTime,
    dicRuta,
):
    perIdSolicitud = None
    perNit = None
    listId = None
    listNombre = None
    listUrl = None
    listUserLogin = None
    listPwdLogin = None
    rutaScr = None
    idConsecutivoP = None
    retryTime = None
    varImportRPA = None
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
        "apiCaptcha": None,
        "reintentosEspera": None,
        "siteCaptchaKey": None,
        "msgNoCaptcha": None,
    }

    resultE = {
        "idSolicitud": None,
        "idLista": None,
        "urlResultado": None,
    }

    estudioS = resultE
    try:
        with bloqueoHilos:
            perNit = user["nit"]
            perIdSolicitud = user["id"]
            idConsecutivoP = user['idInfolaft']
            listId = listaRiesgo["idLista"]
            listNombre = listaRiesgo["nombre"]
            listUrl = listaRiesgo["urlLista"]
            listUserLogin = listaRiesgo["userLogin"]
            listPwdLogin = listaRiesgo["passwordLogin"]
            rutaScr = f"{rutaFS}/{perNit}/infolaft/{perIdSolicitud}/"
            retryTime = envRetryTime
            if not os.path.exists(rutaScr):
                os.makedirs(rutaScr)

            dicRuta.update({"rutaDoc": rutaScr + str(listId) + "_" + perNit + ".pdf"})
            varImportRPA = importlib.import_module(f"rpa.{listNombre}")
            print(f"{listNombre} - Solicitud {perIdSolicitud}")

            rpaDatosDic.update(
                {
                    "nit": perNit,
                    "idSolicitud": perIdSolicitud,
                    "idConsecutivo": idConsecutivoP,
                    "idLista": listId,
                    "listNombre": listNombre,
                    "urlLista": listUrl,
                    "usuarioLogin": listUserLogin,
                    "contraseñaLogin": listPwdLogin,
                    "rutaDocumento": dicRuta["rutaDoc"],
                    "rutaDescargas": dicRuta["rutaDescargas"],
                    "reintentosEspera": retryTime,
                }
            )
        resultE.update({"idSolicitud": perIdSolicitud, "idLista": listId})
        estudioS = varImportRPA.rpa(
            resultE, rpaDatosDic
        )
        return estudioS

    except Exception as e:
        return estudioS


def procesarSolicitud(user):
    mensajeError = None
    idSolicitud = None
    nit = None
    result = None
    usrRegistra = None
    updSolicitud = None
    documentoDispo = None

    idSolicitud = user["id"]
    usrRegistra = user["usrRegistra"]



    documentoDispo = maxDocumentos()
    if documentoDispo:
        with sem:
            with bloqueoHilos:
                updSolicitud = updEstadoDocumento(
                    idSolicitud, usrRegistra, envEstadoV, envAppRPA, envModRPA
                )

    if updSolicitud:
        try:

            print(
                f"---------------Inicia RPA PDF Infolaft #{idSolicitud}--------------"
            )

            result = qMstr.getListaT()
            for listaRiesgo in result:
                idLista = None
                procesPDF = {
                    "idSolicitud": None,
                    "idLista": None,
                    "urlResultado": None,
                }
                nombreLista = None

                idLista = listaRiesgo["idLista"]
                nombreLista = listaRiesgo["nombre"]
                with os.scandir(os.environ.get("RUTAPROYECTO") + "rpa") as files:
                    for file in files:
                        if str(nombreLista + ".py") == (file.name):
                            auditoriaUPD = None
                            # EJECUTA EL ARCHIVO PARA GENERAR EL PDF
                            procesPDF = procesarDocumento(
                                envRutaFS,
                                listaRiesgo,
                                user,
                                envRetryTime,
                                glbRutaS,
                            )

                            print(procesPDF)
                            infoLaftDocumento = procesPDF["urlResultado"]

                            if infoLaftDocumento:
                                qMstr.insertResultado(procesPDF)
        except Exception as e:
            mensajeError = msgTelegram + repr(e)
            for idChat in chatIds:

                async def enviar_mensaje(token, chat_id, mensaje):
                    bot = Bot(token)
                    await bot.send_message(chat_id=chat_id, text=mensaje)

                async def main():
                    token = botToken
                    chat_id = idChat
                    await enviar_mensaje(token, chat_id, mensajeError)

                asyncio.run(main())
    updEstadoFE = None
    updEstadoFE = {
        "estado": envEstadoF,
        "idSolicitud": idSolicitud,
        "mensajeError": mensajeError,
    }
    qMstr.updEstadoSolicitudFinalizada(updEstadoFE)

def ejecutarRPA():
    randomTimeSleep = None
    userP = None
    selectDocumentoP = None
    DocumentoDispo = None
    DocumentoDispo = maxDocumentos()
    if DocumentoDispo:
        selectDocumentoP = {"estado": os.environ.get("ESTADOPENDIENTE")}
        userP = qMstr.getSolicitud(selectDocumentoP)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            randomTimeSleep = random.uniform(0, 5)
            time.sleep(randomTimeSleep)
            ejecutado = list(executor.map(procesarSolicitud, userP))


rpaInfolaft = ejecutarRPA()
