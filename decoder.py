# Made by: Max Thielen

import base64
import requests
import json

def lht_decode(payload): 
    msg = payload.encode("ascii")
    bytes = list(base64.b64decode(msg))

    data = {
        "bytes" : bytes
    }

    request = requests.get("https://lhtdecoderofnptx7a-test.functions.fnc.fr-par.scw.cloud/", data = json.dumps(data))

    try:
        output = request.json()
    except json.decoder.JSONDecodeError:
        print(f"Cloud function could not decode payload: {payload}")
        return {}

    decoded = {
        "mode": output['decoded']["Work_mode"],
        "light": output['decoded']["ILL_lx"],
        "temp": output['decoded']["TempC_SHT"],
        "humidity": output['decoded']["Hum_SHT"],
        "battery_status": output['decoded']["Bat_status"],
        "battery_voltage": output['decoded']["BatV"]
    }

    return decoded

def py_decode(payload):
    msg = payload.encode("ascii")
    bytes = base64.b64decode(msg)
    
    light = bytes[1]
    pressure = bytes[0]/2+950
    temp = ((bytes[2]-20)*10+bytes[3])/10
    
    decoded = {
        "light": light,
        "temp": temp,
        "pressure": pressure,
    }
    
    return decoded
    
def lopy_decode(payload):
    msg = payload.encode("ascii")
    bytes = base64.b64decode(msg)
    
    pressure = bytes[0]+950
    light = bytes[1]
    temp = float(f"{bytes[2]}.{bytes[3]}")
    
    decoded = {
        "light": light,
        "temp": temp,
        "pressure": pressure,
    }

    return decoded
    

def decode(device_id: str, payload: str):

    if len(payload) > 8 and device_id.startswith("lht"):
        # This is an LHT device for sure (long payload and starts with lht)
        decoded = lht_decode(payload)

        if decoded == {}:
            return ()

        return ("lht", decoded)
    
    elif device_id.startswith("py") and len(payload) == 8 and 'wierden' in device_id or 'saxion' in device_id:
        # This is definitly a pyCom from either wierden of saxion
        return ("py", py_decode(payload))

    elif not device_id.startswith("lht") and len(payload) == 8 and "py" in device_id:
        # This is definetly a pyCom of our own
        return ("lopy", lopy_decode(payload))

    else:
        print(f"Payload doesn't match device: {device_id} with payload: {payload}")
        return (None, None)

  
# py_payload = 'l70qAw=='
# pyDecode(py_payload)

# lht_payload = 'zB4IQQHsBQEXf/8='
# lhtDecode(lht_payload)

if __name__ == "__main__":
    print(decode("py-adriaan", "igAdBQ=="))