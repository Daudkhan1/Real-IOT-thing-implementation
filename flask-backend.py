from flask import Flask, jsonify, render_template, request
import paho.mqtt.client as mqtt
import psycopg2
import ssl
import json

app = Flask(__name__)

# Database Connection
DB_HOST = "database-1.ch2cu2qaa4oh.ap-south-1.rds.amazonaws.com"
DB_NAME = "iot_db"
DB_USER = "daud"
DB_PASSWORD = "daud3738"

try:
    conn = psycopg2.connect(
        database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port="5432"
    )
    cursor = conn.cursor()
    print("[INFO] Database connection established successfully")
except Exception as e:
    print(f"[ERROR] Database connection failed: {e}")
    conn, cursor = None, None

# AWS IoT Core Details
BROKER_ENDPOINT = "alf679etvm4fm-ats.iot.ap-south-1.amazonaws.com"

CERTS_PATH = "/home/ubuntu/certs"
CA_CERT = f"{CERTS_PATH}/AmazonRootCA1.pem"

# Function to configure MQTT client dynamically
def configure_mqtt_client(thing_name):
    client = mqtt.Client(client_id=f"{thing_name}-client-pub", protocol=mqtt.MQTTv311)
    thing_cert = f"{CERTS_PATH}/{thing_name}.pem.crt"
    thing_key = f"{CERTS_PATH}/{thing_name}.pem.key"

    client.tls_set(ca_certs=CA_CERT, certfile=thing_cert, keyfile=thing_key, tls_version=ssl.PROTOCOL_TLS)
    
    def on_connect(client, userdata, flags, rc):
        print(f"[INFO] Connected to AWS IoT Core with result code {rc}")
        client.subscribe(f"{thing_name}/incoming")

    def on_message(client, userdata, msg):
        message = msg.payload.decode()
        print(f"[DEBUG] Received: {message} from topic {msg.topic}")
        try:
            parsed_message = json.loads(message)
            status = parsed_message.get("action", "unknown")
            
            if conn and cursor:
                print(f"[DEBUG] Inserting received status into {thing_name}: {status}")
                cursor.execute(f"INSERT INTO {thing_name} (status) VALUES (%s);", (status,))
                conn.commit()
                print("[DEBUG] ✅ Status inserted successfully")
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse MQTT message: {e}")
        except Exception as e:
            print(f"[ERROR] Database insert failed: {e}")

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ENDPOINT, 8883, 60)
    client.loop_start()

    return client

# Creating clients for both things
thing1_client = configure_mqtt_client("thing1")
thing2_client = configure_mqtt_client("thing2")

@app.route("/")
def home():
    return render_template("dummy-user-app.html")

@app.route("/unlock/<thing_name>", methods=["POST"])
def unlock_thing(thing_name):
    if thing_name not in ["thing1", "thing2"]:
        return jsonify({"error": "Invalid thing name"}), 400
    
    payload = json.dumps({"action": "unlock", "thing": thing_name})
    topic = f"{thing_name}/incoming"

    if thing_name == "thing1":
        thing1_client.publish(topic, payload, qos=1)
    else:
        thing2_client.publish(topic, payload, qos=1)

    print(f"[DEBUG] Published: {payload} to topic {topic}")
    return jsonify({"message": f"Unlock request sent to {thing_name}"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
