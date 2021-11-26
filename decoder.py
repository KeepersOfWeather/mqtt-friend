import base64

def lhtDecode(payload): 
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
    	tempDS = (bytes[0]<<24>>16 | bytes[1])/100
    	batS = bytes[4]>>6
    else:
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
        ext_sensor = "Temperature Sensor";
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
        mode = "Interrupt Sensor count";
        extCount = bytes[7]<<24 | bytes[8]<<16 | bytes[9]<<8 | bytes[10]
    elif ext==9:
        mode = "DS18B20 & timestamp"
        time = bytes[7]<<24 | bytes[8]<<16 | bytes[9]<<8 | bytes[10] 
    elif ext==15:
        mode = "DS18B20ID";
        ID = str_pad(bytes[2])+str_pad(bytes[3])+str_pad(bytes[4])+str_pad(bytes[5])+str_pad(bytes[7])+str_pad(bytes[8])+str_pad(bytes[9])+str_pad(bytes[10]); 
    
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
        
        return(decoded)
    
    
def pyDecode(payload):
    msg = payload.encode("ascii")
    bytes = base64.b64decode(msg)
    
    light = bytes[1];
    pressure = bytes[0]/2+950;
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
    
  
  
py_payload = 'l70qAw=='
pyDecode(py_payload)

lht_payload = 'zB4IQQHsBQEXf/8='
lhtDecode(lht_payload)