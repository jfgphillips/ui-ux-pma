In order to run this application please run the following command

Run locally (Flask Config), for use on just one computer
```
virtualenv .venv
source .venv/bin/activate
pip install requirements.txt

flask run
```
n.b. you can specify an optional port number with `flask run -p 5001` 

Run locally (Python Config), for use across multiple computers
```
nano app.py
# customise the following lines (124) with your ifconfig public hostname
# e.g. `ifconfig | grep "inet"`
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host ="xxx.xxx.xx.xx") # <-- line 124
```


