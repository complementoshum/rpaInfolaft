import os

from dotenv import load_dotenv

import includes.libs.connection as con

load_dotenv()  # Evitar sobrescribir variables


def getListaT():
    query = (
        f"select [idLista],[nombre],[urlLista],[descripcion],[fechaHora],[estado],[usrRegistra],[fechaUltUpd],"
        f"[esListaRiesgo],[userLogin],[passwordLogin],[msgNoResultado],[msgNoCaptcha],[siteCaptchaKey] "
        f"from T_RPA_ListasRiesgo with(nolock) where esListaRiesgo = '{os.environ.get('LISTAINFOLAFT')}'"
    )
    conec = con.conSqlAppWeb()
    cursor = conec.cursor().execute(query)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return results


def getEstadoLista(row):
    query = f"select estado from T_RPA_ListasRiesgo with(nolock) where idLista = {row['idLista']}"
    conec = con.conSqlAppWeb()
    cursor = conec.cursor().execute(query)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return results



def getSolicitud(row):
    estado = row["estado"]
    query = (
        f"SELECT {os.environ.get('TOPSOL')} [id], [idBd],[idProceso],[idInfolaft],[nit],[usrRegistra],"
        f"[fechaHora],[rutaArchivo], [fechaFinalizacion], [estado] "
        f"FROM T_GH_solicitudInfolaft WITH(NOLOCK) where estado = '{estado}' and rutaArchivo IS NULL order by id asc"
    )
    conec = con.conSqlAppWeb()
    cursor = conec.cursor().execute(query)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return results


def getSolicitudesV():
    query = f"select count(idInfolaft) cantidad from T_GH_solicitudInfolaft WITH(NOLOCK) WHERE estado = '{os.environ.get('ESTADOVALIDANDO')}'"
    conec = con.conSqlAppWeb()
    cursor = conec.cursor().execute(query)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return results


def insertResultado(row):
    params = (row["urlResultado"], row["idSolicitud"])
    query = "UPDATE T_GH_solicitudInfolaft SET rutaArchivo = ? WHERE id = ?"
    conec = con.conSqlAppWeb()
    cursor = conec.cursor().execute(query, params)
    conec.commit()
    return (
        cursor.rowcount,
        f"row(s) affected. Se ha insertado el resultado de la lista {row['idLista']} Solicitud {row['idSolicitud']}.",
    )


def updEstadoDocs(row):
    params = (row["estado"], row["idSolicitud"])
    query = "UPDATE T_GH_solicitudInfolaft SET estado = ? where id = ?"
    conec = con.conSqlAppWeb()
    cursor = conec.cursor().execute(query, params)
    conec.commit()
    return (
        cursor.rowcount,
        f"row(s) affected. Se actualizo el estado del documento {row['idSolicitud']}.",
    )


def updEstadoSolicitudFinalizada(row):
    params = (row["estado"], row["idSolicitud"])
    query = "UPDATE T_GH_solicitudInfolaft SET estado = ?, fechaFinalizacion = GETDATE() where id = ?"
    conec = con.conSqlAppWeb()
    cursor = conec.cursor().execute(query, params)
    conec.commit()
    return (
        cursor.rowcount,
        f"row(s) affected, se actualizo el estado del documento {row['idSolicitud']}.",
    )

def getConecInfo(params):
    params = params['idBd']
    query = "SELECT idBd, bd, srv FROM T_G_appDatabases WITH(NOLOCK) WHERE idBd = ?"
    conec = con.conSqlAppWeb()
    cursor = conec.cursor().execute(query, params)
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return results[0]