import urllib.request
import json
def get_truckinfo():
    with urllib.request.urlopen("http://localhost:25555/api/ets2/telemetry") as url:
        data = json.loads(url.read().decode())
        return data['truck']['speed'],data['truck']['gameThrottle'],data['truck']['gameBrake'],data['truck']['gameSteer']

def get_accel():
    with urllib.request.urlopen("http://localhost:25555/api/ets2/telemetry") as url:
        data = json.loads(url.read().decode())
        return data['truck']['speed']
    

def get_info():
    with urllib.request.urlopen("http://localhost:25555/api/ets2/telemetry") as url:
        data = json.loads(url.read().decode())
        return data
