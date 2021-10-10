FROM python:3.9 as builder

RUN apt-get update && apt-get install -y openssh-server && \
    apt-get install --no-install-recommends -y liblapack-dev gcc gfortran && \
    apt-get install gcc && apt-get clean && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /requirements.txt
RUN pip install -U pip setuptools \
    && pip install --no-cache-dir -r /requirements.txt supervisor

WORKDIR /opt/app

ENV APP_PATH=/opt/app

# Copy the application over into the container.
ADD application /opt/app/application

RUN git clone https://github.com/jvkersch/pyconcorde opt/app/pyconcorde
CMD cd opt/app/pyconcorde
RUN pip install -e opt/app/pyconcorde

CMD cd /opt/app/application
CMD gunicorn -b 0.0.0.0:8000 application.__init__:server
EXPOSE 8000
