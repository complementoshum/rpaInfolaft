import os
from dotenv import load_dotenv
import includes.libs.connection as con
import logging

load_dotenv()  # Cargar variables de entorno


# Configura el logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M'
)

logger = logging.getLogger(__name__)


def executeQuery(query, cnx=None, params=()):
    results = []

    if not cnx:
        cnx = con.conSqlAppWeb()
    try:
        with cnx:
            with cnx.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().lower().startswith("select"):
                    columns = [column[0] for column in cursor.description]
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))

                    return results

                else:
                    cnx.commit()

                    return cursor.rowcount

    except Exception as e:
        logger.critical(f"Error ejecutando query: {repr(e)}")
        return None

    finally:
        if cnx:
            cnx.close()


def getListaT():
    query = f"""
                SELECT [idLista],[nombre],[urlLista],[descripcion],[fechaHora],[estado],[usrRegistra],[fechaUltUpd],
                [esListaRiesgo],[userLogin],[passwordLogin],[msgNoResultado],[msgNoCaptcha],[siteCaptchaKey]
                FROM T_RPA_ListasRiesgo WITH(NOLOCK) WHERE esListaRiesgo = ?
            """
    params = (os.environ.get("LISTAINFOLAFT"),)
    return executeQuery(query, params=params)


def getEstadoLista(row):
    query = f"""SELECT estado FROM T_RPA_ListasRiesgo WITH(NOLOCK) WHERE idLista = ? """
    params = (row["idLista"],)
    return executeQuery(query, params=params)


def getSolicitud(row):
    query = f"""
                SELECT {os.environ.get('TOPSOL')} [id], [idBd],[idProceso],[idInfolaft],[nit],[usrRegistra],
                [fechaHora],[rutaArchivo], [fechaFinalizacion], [estado]
                FROM T_GH_solicitudInfolaft WITH(NOLOCK) WHERE estado = ? AND rutaArchivo IS NULL ORDER BY id ASC
            """
    params = (row["estado"])
    return executeQuery(query, params = params)


def getSolicitudesV():
    query = f"""
                SELECT COUNT(idInfolaft) AS cantidad
                FROM T_GH_solicitudInfolaft WITH(NOLOCK) WHERE estado = ?
            """
    params = (os.environ.get("ESTADOVALIDANDO"),)
    return executeQuery(query, params = params)


def insertResultado(row):
    query = f"""UPDATE T_GH_solicitudInfolaft SET rutaArchivo = ? WHERE id = ? """
    params = (row["urlResultado"], row["idSolicitud"])
    rowResult = executeQuery(query, params = params)

    return f""" {rowResult} row(s) affected. Se ha insertado el resultado de la lista {row['idLista']} Solicitud {row['idSolicitud']}.
            """



def updEstadoSolicitud(row):
    query = f"""UPDATE T_GH_solicitudInfolaft SET estado = ? WHERE id = ?"""
    params = (row["estado"], row["idSolicitud"])
    rowResult = executeQuery(query, params = params)
    return f"""
        {rowResult} row(s) affected. Se actualizó el estado del documento {row['idSolicitud']}.
    """



def updEstadoSolicitudFinalizada(row):
    query = f"""UPDATE T_GH_solicitudInfolaft SET estado = ?, fechaFinalizacion = GETDATE() WHERE id = ?"""
    params = (row["estado"], row["idSolicitud"])
    rowResult = executeQuery(query, params = params)
    return f"""{rowResult} row(s) affected. Se actualizó el estado del documento {row['idSolicitud']}.
            """


def getConecInfo(params):
    query = (
        f"""SELECT idBd, bd, srv FROM T_G_appDatabases WITH(NOLOCK) WHERE idBd = ?"""
    )
    params = (params["idBd"])
    result = executeQuery(query, params = params)
    return result[0] if result else None
