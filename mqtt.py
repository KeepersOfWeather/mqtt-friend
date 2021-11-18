import paho.mqtt.client as mqttClient
import mariadb
import json
import os
from threading import Event

# The Things Network MQQT broker credentials
broker_endpoint = os.getenv("BROKER_ADDRESS")
port = os.getenv("BROKER_PORT")
user = os.getenv("BROKER_USER")
password = os.getenv("BROKER_PASSWORD")

# Database environment variables
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_endpoint = os.getenv("DB_ENDPOINT") #
db_port = os.getenv("DB_PORT")
db_db = os.getenv("DB_DB")
db_json_table = os.getenv("DB_JSON_TABLE") # 

# Check if we have all needed environment keys
if not any([broker_endpoint, port, user, password, db_user, db_password, db_endpoint, db_port, db_db, db_json_table]):
    print("Missing environment variables, check your docker compose file.")
    os._exit(1)

try:
    conn = mariadb.connect(
        user=db_user,
        password=db_password,
        host=db_endpoint,
        port=int(db_port),
        database=db_db
    )

except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    os._exit(1)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        # Connection succesfull
        print("Connected to broker!")

        # Subscribe to all events
        print("Subscribing to main topic...")
        client.subscribe("#")
        print("Subcribed!")

    else:
        print(f"Connection failed (rc: {rc})")

def on_message(client, userdata, message):
    try:
        payload_json = json.loads(message.payload)
        # print(payload_json)
    except ValueError as e:
        print(f"Error parsing message from {client}")
        return

    # Convert json object to string to use in database
    payload_json_str = str(json.dumps(payload_json, indent=4, sort_keys=False))

    try:
        # Get cursor and write to table
        cursor = conn.cursor()

        cursor.execute(
            f"INSERT INTO {db_json_table} (id, json) VALUES (?, ?)", (0, payload_json_str)
            )

        # Commit to database
        conn.commit()    

        print("Added new data to database!")

    except mariadb.Error as e:
        print(f"MariaDB error: {e}")

    # dev_name = weatherInfo["dev_id"]
    # dev_serial = weatherInfo['metadata']['gateways'][0]['gtw_id']
    # dev_dt = weatherInfo['metadata']['gateways'][0]['time']
    # raw_id = (dev_serial, dev_dt)

client = mqttClient.Client()  # create new instance

# Use HTTPS with 8883
client.tls_set()

# Authenticate to TTN and setup callback functions
client.username_pw_set(user, password=password)  # set username and password
client.on_connect = on_connect  # attach function to callback
client.on_message = on_message  # attach function to callback

# Connect and start event loop
client.connect(broker_endpoint, int(port), 60)  # connect to broker
client.loop_start()  # start the loop

while True:
    Event().wait()