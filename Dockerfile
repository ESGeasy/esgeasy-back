FROM python:3.9.7-bullseye

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=server

EXPOSE 5000