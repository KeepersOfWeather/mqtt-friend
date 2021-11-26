import paho.mqtt.client as mqttClient
import mariadb
import decoder
import json
import os
import datetime
from threading import Event

# The Things Network MQQT broker credentials
broker_endpoint = os.getenv("BROKER_ADDRESS")
port = os.getenv("BROKER_PORT")
user = os.getenv("BROKER_USER")
password = os.getenv("BROKER_PASSWORD")

# Database environment variables
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_endpoint = os.getenv("DB_ENDPOINT")
db_port = os.getenv("DB_PORT")
db_db = os.getenv("DB_DB")

# Database tables
db_json_table = os.getenv("DB_JSON_TABLE", "raw_json")
db_metadata_table = os.getenv("DB_METADATA_TABLE", "metadata")
db_positional_table = os.getenv("DB_POSITIONAL_TABLE", "positional")
db_sensor_data_table = os.getenv("DB_SENSOR_DATA_TABLE", "sensor_data")
db_transmissional_data_table = os.getenv("DB_TRANSMISSIONAL_DATA_TABLE", "transmissional_data")

# Check if we have all needed environment keys
if not any([broker_endpoint, port, user, password, db_user, db_password, db_endpoint, db_port, db_db, db_json_table]):
    print("Missing environment variables, check your docker compose file.")
    os._exit(1)

try:
    # Try connecting to the database
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
        
    except ValueError as e:
        print(f"Error parsing message from {client}")
        return

    failed = False

    # Convert json object to string to dump into our database
    payload_json_str = str(json.dumps(payload_json, indent=4, sort_keys=False))

    try:
        # Get cursor and write to table
        cursor = conn.cursor()

        # Insert raw JSON into raw_json table
        cursor.execute(
            f"INSERT INTO {db_json_table} (id, json) VALUES (?, ?)", (0, payload_json_str)
        )

        # Commit to database
        conn.commit()

    except mariadb.Error as e:
        failed = True
        print(f"MariaDB error: {e}")

    # timestamp	timestamp [0000-00-00 00:00:00]	
    timestamp = payload_json["received_at"].split(".")[0].replace("T", " ")

    payload = payload_json["uplink_message"]["frm_payload"]

    # device_id	tinytext	
    device_id = payload_json["end_device_ids"]["device_id"]

    # TODO: Decode weather data based on device or payload type?
    decoded_payload = decoder.decode(device_id, payload)

    # The payload doesn't match the device or the device is unknown
    if not any(decoded_payload):
        print("Not storing to database!")
        return

    try:

        # Get cursor and write to table
        cursor = conn.cursor()

        # This is our decoded data from the payload
        decoded = decoded_payload[1]

        if decoded_payload[0] == "lht":
            cursor.execute(
                f"INSERT INTO {db_sensor_data_table} (timestamp, light_log_scale, light_lux, temperature, humidity, pressure, battery_status, battery_voltage, work_mode) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                (timestamp, None, decoded["light"], decoded["temp"], decoded["humidity"], None, decoded["battery_status"], decoded["battery_voltage"], decoded["mode"])
            )

        elif decoded_payload[0] == "py":
            cursor.execute(
                f"INSERT INTO {db_sensor_data_table} (timestamp, light_log_scale, light_lux, temperature, humidity, pressure, battery_status, battery_voltage, work_mode) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                (timestamp, decoded["light"], None, decoded["temp"], None, decoded["pressure"], None, None, None)
            )

        conn.commit()

    except mariadb.Error as e:
        failed = True
        print(f"MariaDB error: {e}")

    # We push these values to the metadata table:

    # application_id	tinytext	
    application_id = payload_json["end_device_ids"]["application_ids"]["application_id"]

    # gateway_id	tinytext
    gateway_id = payload_json["uplink_message"]["rx_metadata"][0]["gateway_ids"]["gateway_id"]

    try:
        # Get cursor and write to table
        cursor = conn.cursor()

        cursor.execute(
            f"INSERT INTO {db_metadata_table} (timestamp, device_id, application_id, gateway_id) VALUES (?, ?, ?, ?)", 
            (timestamp, device_id, application_id, gateway_id)
        )

        conn.commit()

    except mariadb.Error as e:
        failed = True
        print(f"MariaDB error inserting metadata: {e}")

    # latitude	float	
    latitude = payload_json["uplink_message"]["rx_metadata"][0]["location"]["latitude"]

    # longitude	float	
    longitude = payload_json["uplink_message"]["rx_metadata"][0]["location"]["longitude"]

    # altitude	float	
    altitude = payload_json["uplink_message"]["rx_metadata"][0]["location"]["altitude"]

    try:
        # Get cursor and write to table
        cursor = conn.cursor()

        cursor.execute(
            f"INSERT INTO {db_positional_table} (timestamp, latitude, longitude, altitude) VALUES (?, ?, ?, ?)", 
            (timestamp, latitude, longitude, altitude)
        )

        conn.commit()

    except mariadb.Error as e:
        failed = True
        print(f"MariaDB error inserting positional data: {e}")

    # rssi
    rssi = payload_json["uplink_message"]["rx_metadata"][0]["rssi"]

    # snr
    snr = payload_json["uplink_message"]["rx_metadata"][0]["snr"]

    # spreading_factor
    spreading_factor = payload_json["uplink_message"]["settings"]["data_rate"]["lora"]["spreading_factor"]

    # consumed_airtime
    consumed_airtime = payload_json["uplink_message"]["consumed_airtime"].replace("s", "")

    # bandwidth
    bandwidth = payload_json["uplink_message"]["settings"]["data_rate"]["lora"]["bandwidth"]

    # frequency
    frequency = payload_json["uplink_message"]["settings"]["frequency"]

    try:
        # Get cursor and write to table
        cursor = conn.cursor()

        cursor.execute(
            f"INSERT INTO {db_transmissional_data_table} (timestamp, rssi, snr, spreading_factor, consumed_airtime, bandwidth, frequency) VALUES (?, ?, ?, ?, ?, ?, ?)", 
            (timestamp, int(rssi), float(snr), int(spreading_factor), float(consumed_airtime), int(bandwidth), int(frequency))
        )

        conn.commit()

    except mariadb.Error as e:
        failed = True
        print(f"MariaDB error inserting transmissional data: {e}")

    if not failed:
        print("{} Added new data to database!".format(datetime.datetime.now().strftime("%H:%M:%S %d-%b-%Y")))


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