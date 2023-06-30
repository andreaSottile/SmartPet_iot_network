from Network_Controller.models import Food, Heartbeat, Trapdoor


# MSG TEMPLATE:
# { type:[Food, Heartbeat, Trapdoor] config:[false,true] arguments:{a:1 b:2 c:3} }


def decode_message(type, raw_msg):
    """
    Reads a json (obtained from a remote message) and decodes it based on the type;
    the output is ready to be saved in a new database row.

    param type: a string that also is a topic ["food","heartbeat","trapdoor"]
    param raw_msg: a json element like { lvl:a , time:b, id:c }
    :return: content of the message
    """

    if type == "food":
        msg = raw_msg["lvl"], raw_msg["time"], raw_msg["cid"]
        return msg
    if type == "heartbeat":
        msg = raw_msg["freq"], raw_msg["time"], raw_msg["pid"]
        return msg
    if type == "trapdoor":
        msg = raw_msg["dir"], raw_msg["time"], raw_msg["wid"]
        return msg
    return "error"

    #   if t == "food":
    #       msg = raw_msg.arguments.lvlmax, raw_msg.arguments.lvlmin, raw_msg.arguments.lvlth, raw_msg.arguments.cid
    #       return "config_food", msg
    #   if t == "heartbeat":
    #       msg = raw_msg.arguments.freqhigh, raw_msg.arguments.freqlow, raw_msg.arguments.pid
    #       return "config_heartbeat", msg
    #   if t == "trapdoor":
    #       msg = raw_msg.arguments.unlocked, raw_msg.arguments.wid
    #       return "config_trapdoor", msg


def save_food(msg_content):
    """
    Saves a new tuple in the food table

    param msg_content: a tuple containing food_level,timestamp,containerId
    """
    containerId, food_level, time = decode_message(msg_content)
    f = Food(lvl=food_level, time=time, containerID=containerId)
    f.save()


def save_heartbeat(msg_content):
    """
    Saves a new tuple in the heartbeat table

    param msg_content: a tuple containing frequency,timestamp,petId
    """
    frequency, time, petId = decode_message(msg_content)
    hb = Heartbeat(frequency=frequency, time=time, petID=petId)
    hb.save()


def save_trapdoor(msg_content):
    """
    Saves a new tuple in the trapdoors table

    param msg_content: a tuple containing direction,timestamp,trapdoorId
    """
    direction, time, trapdoorId = decode_message(msg_content)
    w = Trapdoor(direction_Trigger=direction, time=time, trapdoorId=trapdoorId)
    w.save()


def display_error(msg_content):
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
     :return: 0 if everything is ok
     """
    return 0


def check_trapdoor(direction, trapdoorId):
    """
      Check food level left in each container, according to the most recent message received

      param msg_content: id of the food container to be checked
      :return:  0 if everything is ok
      """
    return 0


def check_heartbeat(petId):
    """
      Check food level left in each container, according to the most recent message received

      :return: 0 if everything is ok
      """
    return 0


def collect_data(msg_type, msg_raw):
    """
    Called when a new message is received;
    it reads the message, saves it if necessary, and eventually perform control actions

    param type: a string that also is a topic ["food","heartbeat","trapdoor"]
    param raw_msg: a msg received in mqtt
    :return: (code,target)
    code 0: no further actions are necessary
    other codes: more actions to be performed
    """
    msg_content = decode_message(msg_type, msg_raw)
    if msg_content == "error":
        display_error("Received MQTT message with no type")
        return 0,
    if msg_type == "food":
        save_food(msg_content)
        return check_food_level(msg_content.containerId)
    if msg_type == "heartbeat":
        save_heartbeat(msg_content)
        return check_heartbeat(msg_content.petId)
    if msg_type == "trapdoor":
        save_trapdoor(msg_content)
        return check_trapdoor(msg_content.direction, msg_content.trapdoorId)

