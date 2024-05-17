# Imagen
FROM python:3.10.12-slim-bullseye

# Limpiamos y eliminamos el cache
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Instalamos requerimientos
RUN apt-get update -y && \ 
    apt-get install -y gnupg wget xvfb curl unzip cron vim nano --no-install-recommends

# Proyecto
WORKDIR /var/rpa/rpaInfolaft
COPY . /var/rpa/rpaInfolaft
COPY root /var/spool/cron/root
RUN chmod 777 /var/spool/cron/root
RUN /usr/bin/crontab /var/spool/cron/root

# Ejecutamos los requerimientos
RUN python -m pip install -r requirements.txt

# SQL
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update -y && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Configurar el PPA de Chrome
RUN apt-get install -y wget
RUN wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.198-1_amd64.deb

# Actualice la lista de paquetes e instale Chrome
RUN apt-get update -y && \
    apt-get install -y ./google-chrome-stable_114.0.5735.198-1_amd64.deb

# Configurar las variables de entorno de Chromedriver
ENV CHROMEDRIVER_DIR /chromedriver
RUN mkdir $CHROMEDRIVER_DIR

RUN wget -q --continue -P $CHROMEDRIVER_DIR http://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR

# Poner Chromedriver en la RUTA
ENV PATH $CHROMEDRIVER_DIR:$PATH

RUN rm google-chrome-stable_114.0.5735.198-1_amd64.deb

# Comandos para correr aplicacion
CMD ["cron", "-f"]