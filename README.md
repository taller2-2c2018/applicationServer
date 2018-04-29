# Application Server


[![Build Status](https://travis-ci.org/taller2-2c2018/applicationServer.svg?branch=master)](https://travis-ci.org/taller2-2c2018/applicationServer)
[![codecov](https://codecov.io/gh/taller2-2c2018/applicationServer/branch/master/graph/badge.svg)](https://codecov.io/gh/taller2-2c2018/applicationServer)


## How to run it locally

1. Activate the virtual environment with the following command
```
source ./venv/bin/activate
```

2. Run in a separate console the the following command to run a local mongoDB instance
```
sudo service mongod start
```

3. To startup the application run these commands
```
~ cd src
~ python run.py
```

4. To stop the mongoDB instance
```
sudo service mongod stop
```

5. Data sample
```
curl -X POST -H "Content-Type:application/json" 127.0.0.1:5000/user/ --data '{"user":"newUser", "password":"1234rfghu9"}'
```