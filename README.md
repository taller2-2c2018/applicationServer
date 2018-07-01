# Application Server


[![Build Status](https://travis-ci.org/taller2-2c2018/applicationServer.svg?branch=master)](https://travis-ci.org/taller2-2c2018/applicationServer)
[![Coverage Status](https://img.shields.io/coveralls/github/taller2-2c2018/applicationServer/master.svg)](https://coveralls.io/github/taller2-2c2018/applicationServer?branch=master)
## Descripción

Esta es una aplicación desarrollada en python flask v1, conectada a una base de datos mongodb, y una base redis.

A su vez esta aplicación se encuentra conectada a una instancia del backend de [shared server](https://github.com/taller2-2c2018/ApiNodeBackend).

Paralelamente, se utilizan algunos servicios externos:
- Facebook para autenticación de usuarios
- Firebase para envío de notificaciones push

## Configuración local

Para correr la app local, debe existir un archivo en el directorio `/src/config/.env` con las siguientes variables:

```
SHARED_SERVER_HOST=<SHARED_SERVER_HEROKU_URL>
SERVER_USER=<SHARED_SERVER_ADMIN_USER>
SERVER_PASSWORD=<SHARED_SERVER_ADMIN_PASSWORD>
MONGO_URL=<MONGO_DB_CONNECTION_URL>
REDIS_HOST=<REDIS_HOST>
REDIS_PORT=<REDIS_PORT>
ANDROID_APP_TOKEN=<FACEBOOK_ANDROID_SDK_TOKEN>
FIREBASE_SERVER_KEY=<FIREBASE_SERVER_KEY>
LOGGING_LEVEL=<DEBUG|OTHER>
```

## Correr con docker:

### Requerimientos:
- Docker
- Docker-compose

En el directorio raíz del proyecto ejecutar el siguiente comando:  
```
$~ docker-compose up
```
Esto levanta una instancias del aplication server, conectado con un container que contiene la base de datos MongoDB.

### Conexión a docker

Para ejecutar comandos como pip install \<paquete>, se puede conectar al docker container de la siguiente manera: 

```
$~ docker exec -it <nombre_del_container> sh
```
