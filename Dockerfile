FROM python:3-alpine
ADD . /src
WORKDIR /src
RUN pip install -r requirements.txt
RUN pip install gunicorn

ENV FLASK_APP=run.py

EXPOSE 5000