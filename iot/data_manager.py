from django.utils import timezone

from Network_Controller.models import *
from iot.handler_HelperClient import createConnection
from iot.pubsubconfig import *
import re


# MSG TEMPLATE:
# { type:[Food, Heartbeat, Trapdoor] config:[false,true] arguments:{a:1 b:2 c:3} }


def clean_string_to_number(raw_string):
    defined = str(raw_string)
    return int(re.sub(r'\D', '', defined))


def decode_message(type_msg, raw_msg):
    """
    Reads a json (obtained from a remote message) and decodes it based on the type;
    the output is ready to be saved in a new database row.

    param type: a string that also is a topic ["food","heartbeat","hatch"]
    param raw_msg: check pubsubconfig.py to see how message are written
    :return: content of the message
    """
    try:
        digested_msg = str(raw_msg).split(";")
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
    value = clean_string_to_number(food_level)
    f = Food(lvl=value, containerID=cid)
    f.save()
    update_last_interaction(cid)


def save_heartbeat(frequency, pid):
    """
    Saves a new tuple in the heartbeat table

    param frequency: latest heartbeat frequency received
    param pid: id of the pet tag
    """
    value = clean_string_to_number(frequency)
    hb = Heartbeat(frequency=value, petID=pid)
    hb.save()
    update_last_interaction(pid)


def save_hatch(direction, wid):
    """
    Saves a new tuple in the hatches table

    param direction: side of the hatch triggered
    param wid: id of the hatch
    """
    value = clean_string_to_number(direction)
    w = Hatch(direction_Trigger=value, hatchId=wid)
    w.save()
    update_last_interaction(wid)


def display_alert(msg_content):
    """
    Displays a graphic notification when a simple error occurs

    param msg_content: a string describing the error
    """
    print(msg_content)


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
    print("food config: " + str(bottom) + " " + str(stop) + " " + str(start) + " " + str(top))

    # check food level against requirements
    try:
        latest = Food.objects.latest("time")
        print(str(latest))
        if latest.lvl > top:
            display_alert("CRITICAL WARNING: food bowl " + str(cid) + " is overfilled")
        if latest.lvl < bottom:
            display_alert("CRITICAL WARNING: food bowl " + str(cid) + " must be checked")

        # if below required level
        if latest.lvl < start:
            # action: refill target bowl
            return COMMAND_REFILL_START_FOOD, cid

        # if above max level
        if latest.lvl > stop:
            # action: refill target is finished
            return COMMAND_REFILL_STOP_FOOD, cid

        # else, no action to do
        return 0, 0

    except Food.DoesNotExist:
        return 0, 0  # no previous record detected, no action to perform
    # default case, should be unreachable / permission denied: no action to do, hatch stay closed
    return 0, 0


def check_hatch(hatch_id):
    """
      Detected pet nearby a hatch; check if it's allowed to open it; notify the hatch which behavior to apply

      param direction: check if pet is leaving or entering
      param hatchId: hatch where pet is detected
      :return:  0 if everything is ok
      """
    # check if hatch is allowed to open in the current direction
    # if allowed
    # return "open_hatch", hatchId
    # else
    open_permission = HatchConfig.defaultAllow
    try:
        config = HatchConfig.objects.get(hatchId=hatch_id)
        open_permission = config.allowOpen
    except HatchConfig.DoesNotExist:
        pass  # not a problem, using default config values

    print("Permission : " + str(open_permission))
    try:
        latest = Hatch.objects.filter(hatchId=hatch_id).latest("time")
        print(str(latest))
        if str(latest.direction_Trigger) == "0":
            print("received trigger 0 from " + str(hatch_id))

            return COMMAND_CLOSE_HATCH, hatch_id
        else:
            print("received positive trigger from " + str(hatch_id))
            if open_permission:
                # open if allowed (else: nothing to do, ignore it)
                return COMMAND_OPEN_HATCH, hatch_id

    except Hatch.DoesNotExist:
        return 0, 0  # no previous record detected, no action to perform
    # default case, no action to do, hatch stay closed
    return 0, 0


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
    print("Heartbeat config: " + str(low) + " " + str(high))
    try:
        latest = Heartbeat.objects.filter(petID=petId).latest("time")

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
    except Heartbeat.DoesNotExist:
        return 0, 0  # no previous record detected, no action to perform


def collect_data(msg_topic, msg_raw):
    """
    Called when a new message is received;
    it reads the message, saves it if necessary, and eventually perform control actions

    param msg_topic: a string that also is a topic ["food","heartbeat","hatch"]
    param msg_raw: a msg received in mqtt
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
        # unexpected result from decode (for the handling of an Exception in decode function)
        display_alert(arg)
        return 0, 0

    update_last_interaction(target_id)

    if msg_topic == TOPIC_SENSOR_FOOD:
        save_food(arg, target_id)
        return check_food_level(target_id)
    if msg_topic == TOPIC_SENSOR_HEARTBEAT:
        save_heartbeat(arg, target_id)
        return check_heartbeat(target_id)
    if msg_topic == TOPIC_SENSOR_HATCH:
        save_hatch(arg, target_id)
        return check_hatch(target_id)


def get_COAP_address_from_id(nodeID):
    nodeCOAP = LiveClient.objects.filter(nodeId=nodeID).first()
    if nodeCOAP is not None:
        return nodeCOAP.nodeCoapAddress
    else:
        return 0


def update_last_interaction(nodeId):
    client = None
    try:
        client = LiveClient.objects.get(nodeId=nodeId)
    except LiveClient.DoesNotExist:
        print("Trying to update an unknown node: " + str(nodeId))
        client = None
    if client is not None:
        client.lastInteraction = timezone.now()
        client.save()


def register_sensor(candidate_id, node_type):
    '''
    Called when a sensor try to register to Controller.
    There is a check if the Client already exists.
    :param candidate_id: ID proposed from the Sensor.
    :param node_type: type of the sensor node.
    :return: confirmation/reject message to sensor for that ID.
    '''
    duplicate = None
    try:
        duplicate = LiveClient.objects.get(nodeId=candidate_id)
        # rejected candidate_id

    except LiveClient.DoesNotExist:
        duplicate = None
        # this is the case we want, there is no other duplicate
    if duplicate is not None:
        return str(node_type) + " " + str(candidate_id) + " denied"
    else:
        # not a duplicate: register new node
        if node_type == 'heartbeat':
            # Heartbeat Node doesn't have to be paired with actuators
            live = LiveClient(nodeId=candidate_id, nodeType=node_type, isFree=False, isActuator=False)
            live.save()
        else:
            # Food/Hatch cases
            # Looking for an unpaired Actuator Node of the same type of the sensor
            partnerID = look_for_partner(node_type, target="Actuator")
            if partnerID > 0:
                # Found unpaired actuator
                pair = Pair(nodeIdMQTT=candidate_id, nodeIdCOAP=partnerID)
                live = LiveClient(nodeId=candidate_id, nodeType=node_type, isFree=False, isActuator=False)
                live.save()
                pair.save()
            else:
                #  No compatible unpaired actuator
                live = LiveClient(nodeId=candidate_id, nodeType=node_type, isActuator=False, isFree=True)
                live.save()
        return str(node_type) + " " + str(candidate_id) + " approved"


def register_actuator(candidate_id, node_type, node_address):
    '''
    Called when an actuator try to register to Controller.
    There is a check if the Client already exists.
    :param candidate_id: ID proposed from the Actuator.
    :param node_type: type of the sensor node.
    :param node_address: string with the network address
    :return: confirmation/reject message to actuator for that ID.
    '''

    duplicate = LiveClient.objects.filter(nodeId=candidate_id).exists()
    if duplicate:
        # rejected candidate_id
        return str(node_type) + " " + str(candidate_id) + " denied"
    else:
        print("Registering new actuator: " + str(node_type))
        # not a duplicate: register new node
        now = timezone.now()
        # Looking for an unpaired Actuator Node of the same type of the sensor
        partnerID = look_for_partner(node_type, target="Sensor")
        if partnerID != 0:
            # Found unpaired actuator
            pair = Pair(nodeIdMQTT=partnerID, nodeIdCOAP=candidate_id)
            live = LiveClient(nodeId=candidate_id, nodeType=node_type, isFree=False, isActuator=True,
                              nodeCoapAddress=node_address, lastInteraction=now)
            live.save()
            pair.save()
        else:
            #  No compatible unpaired actuator
            live = LiveClient(nodeId=candidate_id, nodeType=node_type, isActuator=True, isFree=True,
                              nodeCoapAddress=node_address, lastInteraction=now)
            live.save()
        createConnection(candidate_id, node_address)
        return str(node_type) + " " + str(candidate_id) + " approved"


def flush_outdated_data():
    if HatchConfig.objects.first() is not None:
        HatchConfig.objects.all().delete()
    if FoodConfig.objects.first() is not None:
        FoodConfig.objects.all().delete()
    if HeartBeatConfig.objects.first() is not None:
        HeartBeatConfig.objects.all().delete()
    if LiveClient.objects.first() is not None:
        LiveClient.objects.all().delete()
    if Pair.objects.first() is not None:
        Pair.objects.all().delete()


def look_for_partner(node_type, target):
    if target == 'Sensor':
        live_client = LiveClient.objects.filter(nodeType=node_type, isActuator=False, isFree=True).first()
    elif target == 'Actuator':
        live_client = LiveClient.objects.filter(nodeType=node_type, isActuator=True, isFree=True).first()
    else:
        return 0
    if live_client is not None:
        live_client.isFree = False
        live_client.save()
        return live_client.nodeId
    else:
        return 0


def negotiate_id(node, id_proposed, node_type):
    result_msg = register_sensor(id_proposed, node_type)
    node.client.publish(TOPIC_ID_CONFIG, result_msg)


def get_pair_object_from_sensor(mqtt_node):
    pair_object = Pair.objects.filter(nodeIdMQTT=mqtt_node).first()

    if pair_object is not None:
        return True, pair_object.nodeIdCOAP
    else:
        return False, None


def get_pair_object_from_actuator(coap_node):
    pair_object = Pair.objects.filter(nodeIdCOAP=coap_node).first()

    if pair_object is not None:
        return True, pair_object.nodeIdMQTT
    else:
        return False, None
