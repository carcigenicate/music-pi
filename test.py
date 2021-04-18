from ssl import PROTOCOL_TLS

from paho.mqtt.subscribe import callback as subscribe_with_callback
from paho.mqtt.publish import single as publish
from paho.mqtt.client import Client, MQTTv31, MQTTMessage



HOSTNAME = "e944d32c8e874cd4979367462d2cbb88.s1.eu.hivemq.cloud"
TOPIC = "request"

AUTH = {"username": "reverseeng",
        "password": "Password1"}

PORT = 8883


def callback(cl, _, message):
    print("Received", message)

def connect_callback(msg, fl, rc):
    print(msg, fl, rc)

def sub_main():
    client = Client("PahoSubTest")
    client.username_pw_set(AUTH["username"], AUTH["password"])
    client.on_message = lambda c, u, message: print(message.payload)
    client.on_connect = lambda cl, ud, fl, rc: connect_callback("SUB", fl, rc)
    client.tls_set(tls_version=PROTOCOL_TLS)
    try:
        result = client.connect(HOSTNAME, PORT)
        client.loop_start()
        print("Connected...", result == 0)
        client.subscribe(TOPIC, qos=2)
        input()
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

def pub_main():
    client = Client("PahoPubTest")
    client.username_pw_set(AUTH["username"], AUTH["password"])
    client.on_publish = lambda *_: print("Published!")
    client.on_connect = lambda cl, ud, fl, rc: connect_callback("PUB", fl, rc)
    client.tls_set(tls_version=PROTOCOL_TLS)
    result = client.connect(HOSTNAME, PORT)
    client.loop_start()
    print("Connected...", result == 0)
    try:
        while True:
            payload = input("Message: ")
            client.publish(TOPIC, payload, qos=0)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

# def pub_main():
#     publish(TOPIC, "TEST!", hostname=HOSTNAME, port=PORT, auth=AUTH)
#
# def sub_main():
#     subscribe_with_callback(callback, [TOPIC], hostname=HOSTNAME, port=PORT, auth=AUTH)