import paho.mqtt.client as mqtt

from iot.data_manager import collect_data, register_sensor
from iot.pubsubconfig import *


def receive(node, topic, msg):
    # receive msg from sensor
    if topic in [TOPIC_SENSOR_HATCH, TOPIC_SENSOR_HEARTBEAT, TOPIC_SENSOR_FOOD]:
        # read content, save in DB if necessary
        rec_msg_code, rec_msg_target = collect_data(topic, msg)

        # switch rec_msg_code:
        if rec_msg_code == 0:  # nothing to do after saving msg in database
            return
        # eventually, perform actions triggered by messages
        # if rec_msg_code == 1:

        if str(rec_msg_code) == COMMAND_OPEN_HATCH:
            # globalStatus.setStatusValve(1)
            node.client.publish(TOPIC_ACTUATOR_HATCH, rec_msg_target + " open")
        elif str(rec_msg_code) == COMMAND_CLOSE_HATCH:
            # globalStatus.setStatusValve(0)
            node.client.publish(TOPIC_ACTUATOR_HATCH, rec_msg_target + " close")
        elif str(rec_msg_code) == COMMAND_REFILL_START_FOOD:
            # globalStatus.setStatusValve(1)
            node.client.publish(TOPIC_ACTUATOR_FOOD, rec_msg_target + " filling")
        elif str(rec_msg_code) == COMMAND_REFILL_STOP_FOOD:
            # globalStatus.setStatusValve(0)
            node.client.publish(TOPIC_ACTUATOR_FOOD, rec_msg_target + " stop")
    else:
        # this is never happening, since i subscribed only topics i can handle
        print("Received message from unexpected topic")


def negotiate_id(node, id_proposed, node_type):
    result_msg = register_sensor(id_proposed, node_type)
    node.client.publish(TOPIC_ID_CONFIG, result_msg)


class MqttNode:
    """
    Handle basic connection functions server-side. The main purpose is receiving messages from sensor nodes.
    Methods:
        task: a thread is going to be instantiated, looping on this function
        on_connect: subscribe all the node topics
        on_message: callback function called for published messages
    """
    client = None

    def task(self, *args):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        print("mqtt node is connecting "+str(args))
        self.client.connect(args[0], args[1])

        if self.client.is_connected():
            print("mqtt node is connected successfully")
        else:
            print("mqtt node is not able to connect")

        # lock the thread in a loop that is permanent until disconnect is called
        # reconnections and callbacks are handled by the library
        self.client.loop_forever()

    def disconnect(self):
        self.client.disconnect()

    def on_message(self, msg):

        if msg.topic == TOPIC_ID_CONFIG:
            # msg payload is defined as: "node_type node_id action"
            msg_fields = str(msg.payload).split(" ")

            if msg_fields == "awakens":
                # new node has connected, waiting for IP
                negotiate_id(self, id_proposed=msg_fields[1], node_type=msg_fields[0])
            # remote nodes can only publish "awakens" action.
            # this thread (controller) is the only one able to publish other actions
        else:
            # digest message from sensors
            receive(self, msg.topic, msg.payload)

    def on_connect(self):
        self.client.subscribe(TOPIC_SENSOR_HATCH)
        self.client.subscribe(TOPIC_SENSOR_HEARTBEAT)
        self.client.subscribe(TOPIC_SENSOR_FOOD)
        self.client.subscribe(TOPIC_ID_CONFIG)
