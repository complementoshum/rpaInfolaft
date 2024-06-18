FROM python:3.10.12-slim-bullseye

# Definir variables de entorno
ENV APP_HOME /var/rpa/rpaInfolaft
ENV RESOURCES_DIR $APP_HOME/includes/resources
# Establecer variables de entorno para Chromedriver
ENV CHROMEDRIVER_DIR /chromedriver
ENV PATH $CHROMEDRIVER_DIR:$PATH

# Configurar directorio de trabajo y copiar archivos del proyecto
WORKDIR $APP_HOME
COPY . $APP_HOME

# Instalar dependencias y herramientas necesarias en una sola capa
RUN set -eux; \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    gnupg \
    curl \
    unzip \
    cron \
    nano \
    && \
    # Configurar Microsoft SQL Server ODBC
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    # Instalar Google Chrome desde el archivo local usando dpkg
    apt-get install -y $RESOURCES_DIR/google-chrome-stable_114.0.5735.198-1_amd64.deb && \
    # Instalar Chromedriver desde el archivo local
    mkdir /chromedriver && \
    unzip $RESOURCES_DIR/chromedriver_linux64.zip -d /chromedriver && \
    # Limpiar cachés y archivos temporales
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    $RESOURCES_DIR/google-chrome-stable_114.0.5735.198-1_amd64.deb \
    $RESOURCES_DIR/chromedriver_linux64.zip

# Configurar cron
COPY root /var/spool/cron/crontabs/root
RUN chmod 600 /var/spool/cron/crontabs/root && \
    chown root:crontab /var/spool/cron/crontabs/root

# Instalar dependencias del proyecto
RUN python -m pip install --no-cache-dir -r requirements.txt

# Comando para correr la aplicación
CMD ["cron", "-f"]