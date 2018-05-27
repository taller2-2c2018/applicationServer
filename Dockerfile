FROM python:3-alpine
ADD . /src
WORKDIR /src

# Change TimeZone
RUN apk add --update tzdata
ENV TZ=America/Argentina/Buenos_Aires
# Clean APK cache
RUN rm -rf /var/cache/apk/*

RUN pip install -r requirements.txt
RUN pip install requests
RUN pip install gunicorn

ENV FLASK_APP=run.py

EXPOSE 5000