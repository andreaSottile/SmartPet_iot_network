import threading

from iot.data_manager import collect_data

import json
from datetime import datetime
from time import time
from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri
from mqttNetwork.mqqt_collector_bath_float import MqttClientBathFloat
from mqttNetwork.mqtt_collector_values import MqttClientData
from database.dataBase import Database
from globalStatus import globalStatus


mqtt_client = 0
coap_client = 0
mqtt_thread = 0
coap_thread = 0


def boot():
    print("network starting up")
    mqtt_client_thread = MqttClientData()
    thread = threading.Thread(target=mqtt_client_thread.mqtt_client)
    thread.start()
    client1 = MqttClientBathFloat()
    thread1 = threading.Thread(target=client1.mqtt_client, args=(), kwargs={})
    thread1.start()

    server = CoAPServer(ip, port)
    thread2 = threading.Thread(target=server.listen, args=(), kwargs={})
    thread2.start()


def receive(msg):
    # receive msg

    # read content, save in DB if necessary
    rec_msg_code, rec_msg_target = collect_data(msg)

    # azioni da eseguire dopo
    # switch rec_msg_code:
    if rec_msg_code == 0:  # nothing to do after saving msg in database
        return




