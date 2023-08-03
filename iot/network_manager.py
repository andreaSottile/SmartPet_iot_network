import threading
from grafana.grafana_init import *
from iot.COAP_server import CoAPServer
from iot.data_manager import flush_outdated_data
from iot.handler_HelperClient import getConnectionHelperClient
from iot.mqttnode import MqttNode

target_host_mqtt = "127.0.0.1"
target_port_mqtt = 1883
mqtt_listener = MqttNode()
mqtt_thread = None
coap_listener = 0  # CoapNode()
coap_thread = None
COAP_Server_ip = "0.0.0.0"
COAP_Server_port = 5683


def boot(req):
    global mqtt_listener
    global mqtt_thread
    print("cleaning database")
    flush_outdated_data()

    print("Grafana starting up")
    create_grafana_data_source(target_host_mqtt, req)
    create_grafana_dashboard(req)

    print("network starting up")
    mqtt_thread = threading.Thread(target=mqtt_listener.task, args=(target_host_mqtt, target_port_mqtt), kwargs={})
    mqtt_thread.start()

    coap_server = CoAPServer(COAP_Server_ip, COAP_Server_port)
    coap_server_thread = threading.Thread(target=coap_server.listen, args=(), kwargs={})
    coap_server_thread.start()


def activateRefiller(actuatorId):
    clientCOAP = getConnectionHelperClient()
    # Send a POST request to actuator (THIS HAS NO EFFECT BESIDE THE OUTPUT LOG)
    response = clientCOAP.post("food", "open" + actuatorId)
    if response.code == 67:
        return 1
    else:
        return 0


def closeRefiller(actuatorId):
    clientCOAP = getConnectionHelperClient()
    # Send a POST request to actuator (THIS HAS NO EFFECT BESIDE THE OUTPUT LOG)
    response = clientCOAP.post("food", "close" + actuatorId)
    if response.code == 67:
        return 1
    else:
        return 0


def closeHatch(actuatorId):
    clientCOAP = getConnectionHelperClient()
    # Send a POST request to actuator (THIS HAS NO EFFECT BESIDE THE OUTPUT LOG)
    response = clientCOAP.post("hatch", "close" + actuatorId)
    if response.code == 67:
        return 1
    else:
        return 0


def openHatch(actuatorId):
    clientCOAP = getConnectionHelperClient()
    # Send a POST request to actuator (THIS HAS NO EFFECT BESIDE THE OUTPUT LOG)
    response = clientCOAP.post("hatch", "open" + actuatorId)
    if response.code == 67:
        return 1
    else:
        return 0
