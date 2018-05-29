#!/bin/sh

pip install -r requirements.txt
cd src/
export DEVELOPMENT=True
flask run