import threading

from iot.data_manager import collect_data, flush_outdated_data

# from coapthon.server.coap import CoAP
# from mqttNetwork.mqqt_collector_bath_float import MqttClientBathFloat

from iot.mqttnode import MqttNode
from coapthon.client.helperclient import HelperClient
from COAP_server import *

target_host_mqtt = "127.0.0.1"
target_port_mqtt = 1883
mqtt_listener = MqttNode()
mqtt_thread = None
coap_listener = 0  # CoapNode()
coap_thread = None
COAP_Server_ip = "0.0.0.0"
COAP_Server_port = 5683


def boot():
    global mqtt_listener
    global mqtt_thread
    print("cleaning database")
    flush_outdated_data()

    print("network starting up")

    mqtt_thread = threading.Thread(target=mqtt_listener.task, args=(target_host_mqtt, target_port_mqtt), kwargs={})
    mqtt_thread.start()

    coap_server = CoAPServer(COAP_Server_ip, COAP_Server_port)
    coap_server_thread = threading.Thread(target=coap_server.listen, args=(), kwargs={})
    coap_server_thread.start()


def activateRefiller(actuatorId):
    clientCOAP = coapConnectionHandler.getConnectionHelperClient(actuatorId)
    # Send a POST request to actuator (THIS HAS NO EFFECT BESIDE THE OUTPUT LOG)
    response = clientCOAP.post("food", "open" + actuatorId)
    if response.code == 67:
        return 1
    else:
        return 0


def closeRefiller(actuatorId):
    clientCOAP = coapConnectionHandler.getConnectionHelperClient(actuatorId)
    # Send a POST request to actuator (THIS HAS NO EFFECT BESIDE THE OUTPUT LOG)
    response = clientCOAP.post("food", "close" + actuatorId)
    if response.code == 67:
        return 1
    else:
        return 0


def closeHatch(actuatorId):
    clientCOAP = coapConnectionHandler.getConnectionHelperClient(actuatorId)
    # Send a POST request to actuator (THIS HAS NO EFFECT BESIDE THE OUTPUT LOG)
    response = clientCOAP.post("hatch", "close" + actuatorId)
    if response.code == 67:
        return 1
    else:
        return 0


def openHatch(actuatorId):
    clientCOAP = coapConnectionHandler.getConnectionHelperClient(actuatorId)
    # Send a POST request to actuator (THIS HAS NO EFFECT BESIDE THE OUTPUT LOG)
    response = clientCOAP.post("hatch", "open" + actuatorId)
    if response.code == 67:
        return 1
    else:
        return 0
