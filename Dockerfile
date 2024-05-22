FROM python:3.10.12-slim-bullseye

# Instalar dependencias y limpiar en una sola capa
RUN apt-get update -y && \
    apt-get install -y gnupg wget curl unzip cron vim nano --no-install-recommends && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update -y && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.198-1_amd64.deb && \
    apt-get install -y ./google-chrome-stable_114.0.5735.198-1_amd64.deb && \
    mkdir /chromedriver && \
    wget -q --continue -P /chromedriver http://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip /chromedriver/chromedriver* -d /chromedriver && \
    rm google-chrome-stable_114.0.5735.198-1_amd64.deb && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Establecer variables de entorno para Chromedriver
ENV CHROMEDRIVER_DIR=/chromedriver
ENV PATH=$CHROMEDRIVER_DIR:$PATH

# Configurar directorio de trabajo y copiar archivos
WORKDIR /var/rpa/rpaInfolaft
COPY . /var/rpa/rpaInfolaft

# Configurar cron
COPY root /var/spool/cron/crontabs/root
RUN chmod 600 /var/spool/cron/crontabs/root

# Instalar dependencias del proyecto
RUN python -m pip install --no-cache-dir -r requirements.txt

# Comando para correr la aplicación
CMD ["cron", "-f"]
