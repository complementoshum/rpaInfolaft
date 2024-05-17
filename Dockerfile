FROM python:3.10.12-slim-bullseye

# Configurar el PPA de Chrome y SQL y realizar una actualización inicial
RUN apt-get update -y && \
    apt-get install -y gnupg wget curl unzip cron vim nano --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update -y && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Instalar Chrome y Chromedriver en una sola capa y limpiar después
RUN wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.198-1_amd64.deb && \
    apt-get update -y && \
    apt-get install -y ./google-chrome-stable_114.0.5735.198-1_amd64.deb && \
    mkdir /chromedriver && \
    wget -q --continue -P /chromedriver http://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip /chromedriver/chromedriver* -d /chromedriver && \
    rm google-chrome-stable_114.0.5735.198-1_amd64.deb && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Establecer variables de entorno para Chromedriver
ENV CHROMEDRIVER_DIR /chromedriver
ENV PATH $CHROMEDRIVER_DIR:$PATH

# Proyecto
WORKDIR /var/rpa/rpaInfolaft
COPY . /var/rpa/rpaInfolaft
COPY root /var/spool/cron/root
RUN chmod 777 /var/spool/cron/root && \
    /usr/bin/crontab /var/spool/cron/root

# Ejecutamos los requerimientos
RUN python -m pip install --no-cache-dir -r requirements.txt

# Comando para correr la aplicación
CMD ["cron", "-f"]
