FROM python:3-slim

LABEL maintainer="tinhhn.uit@gmail.com"

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY app.py ./

CMD gunicorn -w 4 -b 0.0.0.0:9165 app:app
