from Network_Controller.models import *
import time

from iot.network_manager import activateRefiller
# MSG TEMPLATE:
# { type:[Food, Heartbeat, Trapdoor] config:[false,true] arguments:{a:1 b:2 c:3} }
from iot.pubsubconfig import *
from coapthon.resources.resource import Resource
from coapthon.messages.request import Request
from coapthon.messages.response import Response


def timestamp():
    """
    #return current timestamp
    """
    return time.time()


def decode_message(type_msg, raw_msg):
    """
    Reads a json (obtained from a remote message) and decodes it based on the type;
    the output is ready to be saved in a new database row.

    param type: a string that also is a topic ["food","heartbeat","trapdoor"]
    param raw_msg: check pubsubconfig.py to see how message are written
    :return: content of the message
    """
    try:
        digested_msg = raw_msg.split(";")
        node_id = (digested_msg[0].split(":"))[1]
        value = (digested_msg[1].split(":"))[1]
        if type_msg in [TOPIC_SENSOR_HATCH, TOPIC_SENSOR_HEARTBEAT, TOPIC_SENSOR_FOOD]:
            return value, node_id
        # this is never happening, since i collect only sensor data
        else:
            return "error", "error"
    except IndexError:
        return "message not respecting format", type_msg


def save_food(food_level, cid):
    """
    Saves a new tuple in the food table

    param food_level: content of the bowl received
    param cid: id of the food bowl
    """
    now = timestamp()
    f = Food(lvl=food_level, time=now, containerID=cid)
    f.save()
    try:
        node = LiveClients.objects.get(nodeId=cid, nodeType="food")
        node.lastInteraction = now
    except LiveClients.DoesNotExist:
        print("Received Food message from unregistered client " + str(cid))


def save_heartbeat(frequency, pid):
    """
    Saves a new tuple in the heartbeat table

    param frequency: latest heartbeat frequency received
    param pid: id of the pet tag
    """
    now = timestamp()
    hb = Heartbeat(frequency=frequency, time=now, petID=pid)
    hb.save()
    try:
        node = LiveClients.objects.get(nodeId=pid, nodeType="heartbeat")
        node.lastInteraction = now
    except LiveClients.DoesNotExist:
        print("Received Heartbeat message from unregistered client " + str(pid))


def save_hatch(direction, wid):
    """
    Saves a new tuple in the hatches table

    param direction: side of the hatch triggered
    param wid: id of the hatch
    """

    now = timestamp()
    w = Hatch(direction_Trigger=direction, time=now, hatchId=wid)
    w.save()
    try:
        node = LiveClients.objects.get(nodeId=wid, nodeType="heartbeat")
        node.lastInteraction = now
    except LiveClients.DoesNotExist:
        print("Received Heartbeat message from unregistered client " + str(wid))


def display_alert(msg_content):
    """
    Displays a graphic notification when a simple error occurs

    param msg_content: a string describing the error
    """
    # TODO: notifica grafica che sta succedendo un errore
    pass


def check_food_level(cid):
    """
     Check food level left in each container, according to the most recent message received

     param cid: id of the food container to be checked
     :return: 0 if everything is ok; id of target bowl if refilling is necessary
     """
    top, start, stop, bottom = FoodConfig.defaultMax, FoodConfig.defaultThresholdStart, FoodConfig.defaultThresholdStop, FoodConfig.defaultMin
    try:
        config = FoodConfig.objects.get(containerID=cid)
        top = config.lvlMax
        stop = config.lvlThresholdStop
        start = config.lvlThresholdStart
        bottom = config.lvlMin
    except FoodConfig.DoesNotExist:
        pass  # not a problem, using default config values

    # check food level against requirements
    try:
        latest = Food.objects.order_by("time")[:1].get()

        if latest.lvl > top:
            display_alert("CRITICAL WARNING: food bowl " + str(cid) + " is overfilled")
        if latest.lvl < bottom:
            display_alert("CRITICAL WARNING: food bowl " + str(cid) + " must be checked")

        # if below required level
        if latest.lvl < start:
            pairObject = Pair.objects.filter(nodeIdMQTT=cid).first()
            if pairObject is not None:
                pairActuator = pairObject.nodeIdCOAP
                pairActuatorAddress = get_COAP_Address_from_ID(pairActuator)
                success = activateRefiller(pairActuatorAddress)
            # action: refill target bowl
            return COMMAND_REFILL_START_FOOD, cid

        # if above max level
        if latest.lvl > stop:
            return COMMAND_REFILL_STOP_FOOD, cid

        # else, no action to do
        return 0, 0

    except Food.DoesNotExist:
        return 0, 0  # no previous record detected, no action to perform


def check_hatch(hatch_id):
    """
      Detected pet nearby a trapdoor; check if it's allowed to open it; notify the trapdoor which behavior to apply

      param direction: check if pet is leaving or entering
      param trapdoorId: trapdoor where pet is detected
      :return:  0 if everything is ok
      """
    # check if trapdoor is allowed to open in the current direction
    # if allowed
    # return "open_trapdoor", trapdoorId
    # else
    open_permission = HatchConfig.defaultAllow
    try:
        config = HatchConfig.objects.get(hatchId=hatch_id)
        open_permission = config.allowOpen
    except HatchConfig.DoesNotExist:
        pass  # not a problem, using default config values

    try:
        latest = Hatch.objects.filter(hatchId=hatch_id).order_by("time")[:1].get()

        if latest.direction_Trigger == Hatch.nothing:
            return COMMAND_CLOSE_HATCH, hatch_id
        else:
            if open_permission:
                # else, no action to do
                return COMMAND_OPEN_HATCH, hatch_id

    except Hatch.DoesNotExist:
        return 0, 0  # no previous record detected, no action to perform


def check_heartbeat(petId):
    """
      Check heartbeat level; send alert to client_application if value is outside the safe range

      :return: 0 if everything is ok
      """
    # if value out of safe range
    # show alert on client app

    high, low = HeartBeatConfig.defaultHigh, HeartBeatConfig.defaultLow
    try:
        config = HeartBeatConfig.objects.get(petID=petId)
        high, low = config.high_Threshold, config.low_Threshold
    except HeartBeatConfig.DoesNotExist:
        pass  # not a problem, using default config values

    try:
        latest = Heartbeat.objects.filter(petID=petId).order_by("time")[:1].get()

        if latest.frequency > HeartBeatConfig.max:
            display_alert("CRITICAL WARNING: frequency for " + str(petId) + " is above max possible value")
        if latest.frequency < HeartBeatConfig.min:
            display_alert("CRITICAL WARNING: frequency for " + str(petId) + " is below min possible value")

        if latest.frequency < low:
            display_alert("WARNING: pet " + str(petId) + "\'s frequency is lower than safe range")
        if latest.frequency > high:
            display_alert("WARNING: pet " + str(petId) + "\'s frequency is higher than safe range")

            # else, value is safe

        # no actuators for heartbeat
        return 0, 0
    except Hatch.DoesNotExist:
        return 0, 0  # no previous record detected, no action to perform


def collect_data(msg_topic, msg_raw):
    """
    Called when a new message is received;
    it reads the message, saves it if necessary, and eventually perform control actions

    param topic: a string that also is a topic ["food","heartbeat","trapdoor"]
    param raw_msg: a msg received in mqtt
    :return: (code,target)
    code 0: no further actions are necessary
    other codes: more actions to be performed (topic to publish on)
    target: content of the message to be published
    """
    arg, target_id = decode_message(msg_topic, msg_raw)
    if target_id == "error":
        # message cannot be interpreted
        display_alert("Received MQTT message with no type")
        return 0, 0
    if target_id == msg_topic:
        # unexpected result from decode
        display_alert(arg)
        return 0, 0

    if msg_topic == TOPIC_SENSOR_FOOD:
        save_food(arg, target_id)
        return check_food_level(target_id)
    if msg_topic == TOPIC_SENSOR_HEARTBEAT:
        save_heartbeat(arg, target_id)
        return check_heartbeat(target_id)
    if msg_topic == TOPIC_SENSOR_HATCH:
        save_hatch(arg, target_id)
        return check_hatch(target_id)

def get_COAP_Address_from_ID(nodeID):
    nodeCOAP= LiveClients.objects.filter(nodeId=nodeID).first()
    if nodeCOAP is not None:
        return nodeCOAP.nodeCoapAddress
    else:
        return 0



def lookForPartner(node_type, target):
    if target == 'Sensor':
        targetID = LiveClients.object.filter(node_type=node_type, isActuator=False, isFree= True).first()
    elif target == 'Actuator':
        targetID = LiveClients.object.filter(node_type=node_type, isActuator=True, isFree= True).first()
    else:
        return 0
    if targetID is not None:
        return targetID
    else:
        return 0

def register_sensor(candidate_id, node_type):
    '''
    Called when a sensor try to register to Controller.
    There is a check if the Client already exists.
    :param candidate_id: ID proposed from the Sensor.
    :param node_type: type of the sensor node.
    :return: confirmation/reject message to sensor for that ID.
    '''
    duplicate = LiveClients.objects.filter(nodeId=candidate_id).exists()
    if duplicate:
        # rejected candidate_id
        return str(node_type) + " " + str(candidate_id) + " denied"
    else:
        # not a duplicate: register new node
        now = timestamp()
        if(node_type == 'heartbeat'):
            # Heartbeat Node doesn't have to be paired with actuators
            live = LiveClients(nodeId=candidate_id, node_type=node_type,isFree=False, isActuator=False, lastInteraction=now)
            live.save()
        else:
            # Food/Hatch cases
            # Looking for an unpaired Actuator Node of the same type of the sensor
            partnerID = lookForPartner(node_type, target="Actuator")
            if partnerID > 0:
                # Found unpaired actuator
                pair = Pair(nodeIdMQTT=candidate_id, nodeIdCOAP=partnerID)
                live = LiveClients(nodeId=candidate_id, node_type=node_type,isFree=False, isActuator=False, lastInteraction=now)
                live.save()
                pair.save()
            else:
                #  No compatible unpaired actuator
                live = LiveClients(nodeId=candidate_id, node_type=node_type, isActuator=False, isFree=True, lastInteraction=now)
                live.save()
        return str(node_type) + " " + str(candidate_id) + " approved"

def register_actuator(candidate_id, node_type, node_address):
    '''
    Called when an actuator try to register to Controller.
    There is a check if the Client already exists.
    :param candidate_id: ID proposed from the Actuator.
    :param node_type: type of the sensor node.
    :return: confirmation/reject message to actuator for that ID.
    '''
    duplicate = LiveClients.objects.filter(nodeId=candidate_id).exists()
    if duplicate:
        # rejected candidate_id
        return str(node_type) + " " + str(candidate_id) + " denied"
    else:
        # not a duplicate: register new node
        now = timestamp()
        # Looking for an unpaired Actuator Node of the same type of the sensor
        partnerID = lookForPartner(node_type, target="Sensor")
        if partnerID > 0:
            # Found unpaired actuator
            pair = Pair(nodeIdMQTT = candidate_id, nodeIdCOAP = partnerID)
            live = LiveClients(nodeId=candidate_id, node_type=node_type, isFree=False, isActuator=True, nodeCoapAddress = node_address, lastInteraction=now)
            live.save()
            pair.save()
        else:
            #  No compatible unpaired actuator
            live = LiveClients(nodeId=candidate_id, node_type=node_type, isActuator=True, isFree=True, nodeCoapAddress = node_address, lastInteraction=now)
            live.save()
        return str(node_type) + " " + str(candidate_id) + " approved"

def flush_outdated_data():
    LiveClients.objects.all().delete()
    HatchConfig.objects.all().delete()
    FoodConfig.objects.all().delete()
    HeartBeatConfig.objects.all().delete()
