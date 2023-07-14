import threading

from iot.data_manager import collect_data, flush_outdated_data

# from coapthon.server.coap import CoAP
# from mqttNetwork.mqqt_collector_bath_float import MqttClientBathFloat

from iot.mqttnode import MqttNode


target_host_mqtt = "127.0.0.1"
target_port_mqtt = 1883
mqtt_listener = MqttNode()
mqtt_thread = None
coap_listener = 0 # CoapNode()
coap_thread = None


def boot():
    global mqtt_listener
    global mqtt_thread
    global coap_listener
    global coap_thread
    print("cleaning database")
    flush_outdated_data()

    print("network starting up")

    mqtt_thread = threading.Thread(target=mqtt_listener.task, args=(target_host_mqtt, target_port_mqtt), kwargs={})
    mqtt_thread.start()

    coap_thread = threading.Thread(target=coap_listener.task, args=(), kwargs={})
    coap_thread.start()


