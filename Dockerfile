FROM python:3-alpine
ADD . /src
WORKDIR /src
RUN pip install -r requirements.txt