import paho.mqtt.client as mqtt

from iot.pubsubconfig import *


class MqttNode:
    """
    Handle basic connection functions server-side. The main purpose is receiving messages from sensor nodes.
    Methods:
        task: a thread is going to be instantiated, looping on this function
        on_connect: subscribe all the node topics
        on_message: callback function called for published messages
    """
    client = None
    broker = None
    receiver = None

    def __init__(self, negotiate_function, receive_function, disconnect_function):
        self.broker = negotiate_function
        self.receiver = receive_function
        self.killer = disconnect_function

    def task(self, *args):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        print("mqtt node is connecting " + str(args))
        broker_ip = args[0]
        broker_port = args[1]
        print("Connecting to " + str(broker_ip) + ":" + str(broker_port))
        # Set up the client to connect to the broker
        self.client.connect(broker_ip, broker_port)

        # lock the thread in a loop that is permanent until disconnect is called
        # reconnections and callbacks are handled by the library
        self.client.loop_forever()

    def disconnect(self):
        self.client.disconnect()

    def on_message(self, client, userdata, msg):

        if msg.topic == TOPIC_ID_CONFIG:
            # msg payload is defined as: "node_type node_id action"
            payload = str(msg.payload).replace("'", "")
            msg_fields = payload.split(" ")

            if msg_fields[2] == "timeout":
                # new node has connected, waiting for IP
                self.killer(self, id_proposed=msg_fields[1], node_type=msg_fields[0][1:])
            if msg_fields[2] == "awakens":
                # new node has connected, waiting for IP
                self.broker(self, id_proposed=msg_fields[1], node_type=msg_fields[0][1:])
            # remote nodes can only publish "awakens" action.
            # this thread (controller) is the only one able to publish other actions
        else:
            # digest message from sensors
            self.receiver(msg.topic, msg.payload)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            self.client.subscribe(TOPIC_SENSOR_HATCH)
            self.client.subscribe(TOPIC_SENSOR_HEARTBEAT)
            self.client.subscribe(TOPIC_SENSOR_FOOD)
            self.client.subscribe(TOPIC_ID_CONFIG)
        else:
            print("Failed to connect to MQTT broker")
