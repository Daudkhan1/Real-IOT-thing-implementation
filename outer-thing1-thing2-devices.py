import paho.mqtt.client as mqtt
import ssl

BROKER_ENDPOINT = "alf679etvm4fm-ats.iot.ap-south-1.amazonaws.com"
CERTS_PATH = "/home/ubuntu/certs"
CA_CERT = f"{CERTS_PATH}/AmazonRootCA1.pem"

def configure_mqtt_subscriber(thing_name):
    client = mqtt.Client(client_id=f"{thing_name}-client-sub", protocol=mqtt.MQTTv311)
    thing_cert = f"{CERTS_PATH}/{thing_name}.pem.crt"
    thing_key = f"{CERTS_PATH}/{thing_name}.pem.key"

    client.tls_set(ca_certs=CA_CERT, certfile=thing_cert, keyfile=thing_key, tls_version=ssl.PROTOCOL_TLS)
    
    def on_connect(client, userdata, flags, rc):
        print(f"[INFO] Connected to AWS IoT Core with result code {rc}")
        client.subscribe(f"{thing_name}/incoming")

    def on_message(client, userdata, msg):
        print(f"[DEBUG] Received: {msg.payload.decode()} from topic {msg.topic}")

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ENDPOINT, 8883, 60)
    client.loop_start()

    return client

# Creating subscribers for both things
thing1_client = configure_mqtt_subscriber("thing1")
thing2_client = configure_mqtt_subscriber("thing2")

# Keep the script running
while True:
    pass
