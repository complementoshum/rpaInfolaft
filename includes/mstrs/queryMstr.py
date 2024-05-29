import os
from dotenv import load_dotenv
import includes.libs.connection as con
import logging

load_dotenv()  # Cargar variables de entorno


def executeQuery(query, params=None):
    conec = con.conSqlAppWeb()
    cursor = conec.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results
    except Exception as e:
        logging.error(f"Error ejecutando la consulta: {e}")
        return None
    finally:
        cursor.close()
        conec.close()


def getListaT():
    query = f"""
        SELECT [idLista],[nombre],[urlLista],[descripcion],[fechaHora],[estado],[usrRegistra],[fechaUltUpd],
        [esListaRiesgo],[userLogin],[passwordLogin],[msgNoResultado],[msgNoCaptcha],[siteCaptchaKey]
        FROM T_RPA_ListasRiesgo WITH(NOLOCK) WHERE esListaRiesgo = ?
        """
    params = (os.environ.get("LISTAINFOLAFT"),)
    return executeQuery(query, params)


def getEstadoLista(row):
    query = f"""SELECT estado FROM T_RPA_ListasRiesgo WITH(NOLOCK) WHERE idLista = ? """
    params = (row["idLista"],)
    return executeQuery(query, params)


def getSolicitud(row):
    query = f"""
        SELECT {os.environ.get('TOPSOL')} [id], [idBd],[idProceso],[idInfolaft],[nit],[usrRegistra],
        [fechaHora],[rutaArchivo], [fechaFinalizacion], [estado]
        FROM T_GH_solicitudInfolaft WITH(NOLOCK) WHERE estado = ? AND rutaArchivo IS NULL ORDER BY id ASC
        """
    params = (row["estado"],)
    return executeQuery(query, params)


def getSolicitudesV():
    query = f"""
        SELECT COUNT(idInfolaft) AS cantidad
        FROM T_GH_solicitudInfolaft WITH(NOLOCK) WHERE estado = ?
    """
    params = (os.environ.get("ESTADOVALIDANDO"),)
    return executeQuery(query, params)


def insertResultado(row):
    query = f"""UPDATE T_GH_solicitudInfolaft SET rutaArchivo = ? WHERE id = ? """
    params = (row["urlResultado"], row["idSolicitud"])
    conec = con.conSqlAppWeb()
    cursor = conec.cursor()
    try:
        cursor.execute(query, params)
        conec.commit()
        return (
            cursor.rowcount,
            f"row(s) affected. Se ha insertado el resultado de la lista {row['idLista']} Solicitud {row['idSolicitud']}.",
        )
    except Exception as e:
        logging.error(f"Error insertando resultado: {e}")
        return None
    finally:
        cursor.close()
        conec.close()


def updEstadoSolicitud(row):
    query = f"""UPDATE T_GH_solicitudInfolaft SET estado = ? WHERE id = ?"""
    params = (row["estado"], row["idSolicitud"])
    conec = con.conSqlAppWeb()
    cursor = conec.cursor()
    try:
        cursor.execute(query, params)
        conec.commit()
        return (
            cursor.rowcount,
            f"row(s) affected. Se actualizó el estado del documento {row['idSolicitud']}.",
        )
    except Exception as e:
        logging.error(f"Error actualizando estado: {e}")
        return None
    finally:
        cursor.close()
        conec.close()


def updEstadoSolicitudFinalizada(row):
    query = f"""UPDATE T_GH_solicitudInfolaft SET estado = ?, fechaFinalizacion = GETDATE() WHERE id = ?"""
    params = (row["estado"], row["idSolicitud"])
    conec = con.conSqlAppWeb()
    cursor = conec.cursor()
    try:
        cursor.execute(query, params)
        conec.commit()
        return (
            cursor.rowcount,
            f"row(s) affected. Se actualizó el estado del documento {row['idSolicitud']}.",
        )
    except Exception as e:
        logging.error(f"Error actualizando estado finalizado: {e}")
        return None
    finally:
        cursor.close()
        conec.close()


def getConecInfo(params):
    query = (
        f"""SELECT idBd, bd, srv FROM T_G_appDatabases WITH(NOLOCK) WHERE idBd = ?"""
    )
    params = (params["idBd"],)
    result = executeQuery(query, params)
    return result[0] if result else None
