# Welcome to this 11 + Tutoring Flask App


In order to run this application please run the following command

## 1. Setup
1.1. create and activate virtualenvironment
```bash
virtualenv .venv
source .venv/bin/activate
```

1.2. install requirements
```bash
pip install requirements.txt
```



## 2 Run locally (one computer)

a. Run locally (default arguments)
```bash
flask run
```

b. Run locally (customise port)
```bash
flask run -p xxxx
```

c. run locally (publish to local network)
c.1 get your public ip address
```bash
ifconfig | grep -wn "inet"
```
c.2 run flask app with -h parameter
```bash
flask run -h xxx.xxx.xx.xx
```

