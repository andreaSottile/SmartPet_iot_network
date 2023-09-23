import threading
from iot.COAP_server import CoAPServer
from iot.data_manager import negotiate_id, flush_outdated_data, get_pair_object_from_sensor, update_last_interaction, \
    collect_data, unbind
from iot.handler_HelperClient import getConnectionHelperClient
from iot.mqttnode import MqttNode
from iot.pubsubconfig import *

target_host_mqtt = "127.0.0.1"
target_port_mqtt = 1883
mqtt_listener = None
mqtt_thread = None
coap_listener = 0  # CoapNode()
coap_thread = None
COAP_Server_ip = "::"
COAP_Server_port = 5683


def boot(req):
    global mqtt_listener
    global mqtt_thread
    print("cleaning database")
    flush_outdated_data()

    print("Grafana starting up")
    # create_grafana_data_source(target_host_mqtt, req)
    # create_grafana_dashboard(req)

    print("network starting up")
    mqtt_listener = MqttNode(negotiate_function=negotiate_id, receive_function=receive, disconnect_function=unbind)

    mqtt_thread = threading.Thread(target=mqtt_listener.task, args=(target_host_mqtt, target_port_mqtt), kwargs={})
    mqtt_thread.start()

    coap_server = CoAPServer(COAP_Server_ip, COAP_Server_port)
    coap_server_thread = threading.Thread(target=coap_server.start_server, args=(), kwargs={})
    coap_server_thread.start()


def get_mqtt_transceiver():
    global mqtt_listener
    return mqtt_listener


def receive(topic, msg):
    print("received msg: " + str(msg))
    # receive msg from sensor
    if topic in [TOPIC_SENSOR_HATCH, TOPIC_SENSOR_HEARTBEAT, TOPIC_SENSOR_FOOD]:
        # read content, save in DB if necessary
        rec_msg_code, rec_msg_target = collect_data(topic, msg)

        # switch rec_msg_code:
        if rec_msg_code == 0:  # nothing to do after saving msg in database
            return
            # eventually, perform actions triggered by messages
            # if rec_msg_code == 1:
        command_sender(rec_msg_code, rec_msg_target)
    else:
        # this is never happening, since i subscribed only topics i can handle
        print("Received message from unexpected topic")


def activate_refiller(actuator_Id):
    clientCOAP = getConnectionHelperClient(actuator_Id)
    # Send a POST request to actuator (THIS HAS NO EFFECT BESIDE THE OUTPUT LOG)
    # sending ID is not necessary, since the communication is 1:1
    response = clientCOAP.post("food", "command=open")
    if response.code == 67:
        return 1
    else:
        return 0


def close_refiller(actuator_Id):
    clientCOAP = getConnectionHelperClient(actuator_Id)
    # Send a POST request to actuator (THIS HAS NO EFFECT BESIDE THE OUTPUT LOG)
    # sending ID is not necessary, since the communication is 1:1
    response = clientCOAP.post("food", "command=close")
    if response.code == 67:
        return 1
    else:
        return 0


def close_hatch(actuator_Id):
    clientCOAP = getConnectionHelperClient(actuator_Id)
    # Send a POST request to actuator
    # sending ID is not necessary, since the communication is 1:1
    response = clientCOAP.post("hatch", "command=close")
    if response.code == 67:
        return 1
    else:
        return 0


def open_hatch(actuator_Id):
    clientCOAP = getConnectionHelperClient(actuator_Id)
    # Send a POST request to actuator
    # sending ID is not necessary, since the communication is 1:1
    response = clientCOAP.post("hatch", "command=open")
    if response.code == 67:
        return 1
    else:
        return 0


def command_sender(rec_msg_code, rec_msg_target):
    node = get_mqtt_transceiver()
    if node is None:
        print("Node" + str * rec_msg_target + "not paired")
        return

        # Action: open hatch
    if str(rec_msg_code) == COMMAND_OPEN_HATCH:
        print("sending open hatch command to " + str(rec_msg_target))
        paired, pair_target = get_pair_object_from_sensor(rec_msg_target)
        if not paired:
            print("actuator has no partner")
            return
        done = open_hatch(pair_target)
        if done:
            update_last_interaction(pair_target)

        node.client.publish(TOPIC_ACTUATOR_HATCH, str(rec_msg_target) + " open")

        # Action: close hatch
    elif str(rec_msg_code) == COMMAND_CLOSE_HATCH:
        print("sending close hatch command to " + str(rec_msg_target))
        paired, pair_target = get_pair_object_from_sensor(rec_msg_target)
        if not paired:
            print("actuator has no partner")
            return
        done = close_hatch(pair_target)
        if done:
            update_last_interaction(pair_target)
        node.client.publish(TOPIC_ACTUATOR_HATCH, str(rec_msg_target) + " close")

        # Action: refill food
    elif str(rec_msg_code) == COMMAND_REFILL_START_FOOD:
        print("sending fill food command to " + str(rec_msg_target))
        paired, pair_target = get_pair_object_from_sensor(rec_msg_target)
        if not paired:
            print("actuator has no partner")
            return
        done = activate_refiller(pair_target)
        if done:
            update_last_interaction(pair_target)
        node.client.publish(TOPIC_ACTUATOR_FOOD, str(rec_msg_target) + " filling")

        # Action: stop food refill
    elif str(rec_msg_code) == COMMAND_REFILL_STOP_FOOD:
        print("sending stop refilling food command to " + str(rec_msg_target))
        paired, pair_target = get_pair_object_from_sensor(rec_msg_target)
        if not paired:
            print("actuator has no partner")
            return
        done = close_refiller(pair_target)
        if done:
            update_last_interaction(pair_target)
        node.client.publish(TOPIC_ACTUATOR_FOOD, str(rec_msg_target) + " stop")
