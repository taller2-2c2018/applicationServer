#!/bin/sh

pip install -r requirements.txt
cd src/
export DEVELOPMENT=True
export FLASK_ENV=development
export FLASK_APP=appserver/app.py
flask run --host=0.0.0.0