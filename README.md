In order to run this application please run the following command

Run locally (Flask Config), for use on just one computer
1. create and activate virtualenvironment
```bash
virtualenv .venv
source .venv/bin/activate
```

2. install requirements
```bash
pip install requirements.txt
```

3. run Flask app
```bash
flask run
```
n.b. you can specify an optional port number with `flask run -p 5001` 

Run locally (Python Config), for use across multiple computers

```bash
nano app.py
```

```python
# customise the following lines (124) with your ifconfig public hostname
# e.g. `ifconfig | grep "inet"`
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host ="xxx.xxx.xx.xx") # <-- line 124
```


