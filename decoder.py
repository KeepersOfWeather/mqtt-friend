import base64

def lht_decode(payload): 
    msg = payload.encode("ascii")
    bytes = base64.b64decode(msg)
    
    ext = bytes[6]&0x0F
    statusMsg = (bytes[6]&0x40)>>6
    connect = (bytes[6]&0x80)>>7
    
    mode = {}
    light = {}
    tempSHT = {}
    hum = {}
    batS = {}
    batV = {}
    
    if ext==0x09:
        # External temperature
    	tempDS = (bytes[0]<<24>>16 | bytes[1])/100
    	batS = bytes[4]>>6
    else:
        # Battery stuff
        batV = ((bytes[0]<<8 | bytes[1]) & 0x3FFF)/1000
        batS = bytes[0]>>6
        
    if ext!=0x0f:
        tempSHT = (bytes[2]<<24>>16 | bytes[3])/100
        hum = ((bytes[4]<<8 | bytes[5])&0xFFF)/10

    if connect=='1':
        No_connect = "Sensor no connection"

    if ext==0:
        ext_sensor ="No external sensor"
    elif ext==1:
        ext_sensor = "Temperature Sensor"
        tempDS = (bytes[7]<<24>>16 | bytes[8])/100
    elif ext==4:
        mode = "Interrupt Sensor send"
        if bytes[7]:
            val = "High"
        else:
            val = "Low"
        extPin = val
        if bytes[8]:
            val = "True"
        else:
            val = "False"
        extStatus = val
    elif ext==5:
        mode = "Illumination Sensor"
        light = bytes[7]<<8 | bytes[8]
    elif ext==6:
        mode = "ADC Sensor"
        adcV = (bytes[7]<<8 | bytes[8])/1000
    elif ext==7:
        mode = "Interrupt Sensor count"
        extCount = bytes[7]<<8 | bytes[8]
    elif ext==8:
        mode = "Interrupt Sensor count"
        extCount = bytes[7]<<24 | bytes[8]<<16 | bytes[9]<<8 | bytes[10]
    elif ext==9:
        mode = "DS18B20 & timestamp"
        time = bytes[7]<<24 | bytes[8]<<16 | bytes[9]<<8 | bytes[10] 
    elif ext==15:
        mode = "DS18B20ID"
        ID = bytes(bytes[2])+bytes(bytes[3])+bytes(bytes[4])+bytes(bytes[5])+bytes(bytes[7])+bytes(bytes[8])+bytes(bytes[9])+bytes(bytes[10]) 
    
    if(statusMsg==0): #and bytes.length == 11):
        decoded = {
             "mode": mode,
             "light": light,
             "temp": tempSHT,
             "humidity": hum,
             "battery_status": batS,
             "battery_voltage": batV
        }
        print(decoded)
        print()
        print(decoded["battery_voltage"])
        print(decoded["battery_status"])
        print(decoded["humidity"])
        print(decoded["light"])
        print(decoded["temp"])
        print(decoded["mode"])
        
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
    
    print(decoded)
    print()
    print(decoded["light"])
    print(decoded["pressure"])
    print(decoded["temp"])
    
    return decoded
    
def decode(device_id: str, payload: str):

    if len(payload) > 8 and device_id.startswith("lht"):
        # This is an LHT device for sure (long payload and starts with lht)
        return ("lht", lht_decode(payload))
    
    elif device_id.startswith("py") and len(payload) == 8:
        # This is definitly a pyCom
        return ("py", py_decode(payload))

    else:
        print(f"Payload doesn't match device: {device_id} with payload: {payload}")
        return (None, None)

  
# py_payload = 'l70qAw=='
# pyDecode(py_payload)

# lht_payload = 'zB4IQQHsBQEXf/8='
# lhtDecode(lht_payload)

if __name__ == "__main__":
    print(decode("lht-wierden", "zB4IQQHsBQEXf/8="))