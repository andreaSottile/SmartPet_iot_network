import paho.mqtt.client as mqtt

from iot.data_manager import collect_data


def on_message(userdata, msg):
    if msg.topic == "food":
        receive("food", msg.payload)
    if msg.topic == "heartbeat":
        receive("heartbeat", msg.payload)
    if msg.topic == "trapdoor":
        receive("trapdoor", msg.payload)


def receive(topic, msg):
    # receive msg

    # read content, save in DB if necessary
    rec_msg_code, rec_msg_target = collect_data(topic, msg)

    # switch rec_msg_code:
    if rec_msg_code == 0:  # nothing to do after saving msg in database
        return
    # eventually, perform actions triggered by messages
    # if rec_msg_code == 1:


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
        self.client.on_message = on_message

        print("mqtt node is connecting")
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

    def on_connect(self):
        self.client.subscribe("food")
        self.client.subscribe("heartbeat")
        self.client.subscribe("trapdoor")
