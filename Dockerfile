FROM python:3.9 as builder

RUN apt-get update && apt-get install -y openssh-server && \
    apt-get install --no-install-recommends -y liblapack-dev gcc gfortran && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /requirements.txt
RUN pip install -U pip setuptools \
    && pip install --no-cache-dir -r /requirements.txt supervisor
#    && pip install --no-cache-dir --prefix=/pip_prefix -r /requirements.txt supervisor

WORKDIR /opt/app

ENV APP_PATH=/opt/app
ENV AVU_ENV=dev
ENV GUNICORN_HOST=0.0.0.0
ENV GUNICORN_PORT=8000
ENV GUNICORN_MODULE=app
ENV GUNICORN_CALLABLE=app
ENV GUNICORN_USER=app

EXPOSE 8000

# Copy the application over into the container.
#ADD application /opt/app/application
#ADD manage.py /opt/app/
