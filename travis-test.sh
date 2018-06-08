cd src/

export SHARED_SERVER_HOST=default
export SERVER_USER=default
export SERVER_PASSWORD=default
export MONGO_URL=mongodb://127.0.0.1:27017/applicationServerDB
export REDIS_HOST=localhost
export ANDROID_APP_TOKEN=appmock

coverage run -m unittest -v tests/app/allTestsAreHereForNow.py
COVERALLS_REPO_TOKEN=tYDtwIUPZennl1BOFr1lf5JOV2lCM9Go2 coveralls