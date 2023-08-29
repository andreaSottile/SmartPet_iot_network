from Network_Controller.models import *
from iot.handler_HelperClient import createConnection
from iot.network_manager import mqtt_listener
from iot.pubsubconfig import *
from django.utils import timezone




def command_sender(rec_msg_code, rec_msg_target):
    if str(rec_msg_code) == COMMAND_OPEN_HATCH:
        # globalStatus.setStatusValve(1)
        mqtt_listener.client.publish(TOPIC_ACTUATOR_HATCH, rec_msg_target + " open")
    elif str(rec_msg_code) == COMMAND_CLOSE_HATCH:
        # globalStatus.setStatusValve(0)
        mqtt_listener.client.publish(TOPIC_ACTUATOR_HATCH, rec_msg_target + " close")
    elif str(rec_msg_code) == COMMAND_REFILL_START_FOOD:
        # globalStatus.setStatusValve(1)
        mqtt_listener.client.publish(TOPIC_ACTUATOR_FOOD, rec_msg_target + " filling")
    elif str(rec_msg_code) == COMMAND_REFILL_STOP_FOOD:
        # globalStatus.setStatusValve(0)
        mqtt_listener.client.publish(TOPIC_ACTUATOR_FOOD, rec_msg_target + " stop")


def lookForPartner(node_type, target):
    if target == 'Sensor':
        targetID = LiveClient.objects.filter(nodeType=node_type, isActuator=False, isFree=True).first()
    elif target == 'Actuator':
        targetID = LiveClient.objects.filter(nodeType=node_type, isActuator=True, isFree=True).first()
    else:
        return 0
    if targetID is not None:
        return targetID
    else:
        return 0
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
        # not a duplicate: register new node
        now = timezone.now()
        # Looking for an unpaired Actuator Node of the same type of the sensor
        partnerID = lookForPartner(node_type, target="Sensor")
        if partnerID > 0:
            # Found unpaired actuator
            pair = Pair(nodeIdMQTT=candidate_id, nodeIdCOAP=partnerID)
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
