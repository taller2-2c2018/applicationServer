# Application Server


[![Build Status](https://travis-ci.org/taller2-2c2018/applicationServer.svg?branch=master)](https://travis-ci.org/taller2-2c2018/applicationServer)
[![codecov](https://codecov.io/gh/taller2-2c2018/applicationServer/branch/master/graph/badge.svg)](https://codecov.io/gh/taller2-2c2018/applicationServer)

## Descripción

Esta es una aplicación flask conectada a una base de datos mongodb.

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

## Data sample
```
curl -X POST -H "Content-Type:application/json" 127.0.0.1:5000/user/ --data '{"user":"newUser", "password":"1234rfghu9"}'
```