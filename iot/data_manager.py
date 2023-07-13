from Network_Controller.models import Food, Heartbeat, Hatch


# MSG TEMPLATE:
# { type:[Food, Heartbeat, Trapdoor] config:[false,true] arguments:{a:1 b:2 c:3} }


def decode_message(type_msg, raw_msg):
    """
    Reads a json (obtained from a remote message) and decodes it based on the type;
    the output is ready to be saved in a new database row.

    param type: a string that also is a topic ["food","heartbeat","trapdoor"]
    param raw_msg: a json element like { lvl:a , time:b, id:c }
    :return: content of the message
    """
    if type_msg == "food":
        return raw_msg["lvl"], raw_msg["time"], raw_msg["cid"]
    if type_msg == "heartbeat":
        return raw_msg["freq"], raw_msg["time"], raw_msg["pid"]
    if type_msg == "hatch":
        return raw_msg["dir"], raw_msg["time"], raw_msg["wid"]
    return "error", "error", "error"

    #   if t == "food":
    #       msg = raw_msg.arguments.lvlmax, raw_msg.arguments.lvlmin, raw_msg.arguments.lvlth, raw_msg.arguments.cid
    #       return "config_food", msg
    #   if t == "heartbeat":
    #       msg = raw_msg.arguments.freqhigh, raw_msg.arguments.freqlow, raw_msg.arguments.pid
    #       return "config_heartbeat", msg
    #   if t == "trapdoor":
    #       msg = raw_msg.arguments.unlocked, raw_msg.arguments.wid
    #       return "config_trapdoor", msg


def save_food(food_level, time, cid):
    """
    Saves a new tuple in the food table

    param msg_content: a tuple containing food_level,timestamp,containerId
    """

    f = Food(lvl=food_level, time=time, containerID=cid)
    f.save()


def save_heartbeat(frequency, time, pid):
    """
    Saves a new tuple in the heartbeat table

    param msg_content: a tuple containing frequency,timestamp,petId
    """
    hb = Heartbeat(frequency=frequency, time=time, petID=pid)
    hb.save()


def save_hatch(direction, time, wid):
    """
    Saves a new tuple in the trapdoors table

    param msg_content: a tuple containing direction,timestamp,trapdoorId
    """
    w = Hatch(direction_Trigger=direction, time=time, trapdoorId=wid)
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
     :return: 0 if everything is ok; id of target bowl if refilling is necessary
     """

    # check food level against requirements

    # if below required level
    # action: refill target bowl
    # return "start_refill", cid

    # if above max level
    # return "stop_refill", cid

    # else, no action to do
    return 0, 0


def check_hatch(direction, hatchId):
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
    return 0


def check_heartbeat(petId):
    """
      Check heartbeat level; send alert to client_application if value is outside the safe range

      :return: 0 if everything is ok
      """
    # if value out of safe range
    # show alert on client app
    # value is safe
    return 0, 0


def collect_data(msg_type, msg_raw):
    """
    Called when a new message is received;
    it reads the message, saves it if necessary, and eventually perform control actions

    param type: a string that also is a topic ["food","heartbeat","trapdoor"]
    param raw_msg: a msg received in mqtt
    :return: (code,target)
    code 0: no further actions are necessary
    other codes: more actions to be performed (topic to publish on)
    target: content of the message to be published
    """
    arg1, arg2, target_id = decode_message(msg_type, msg_raw)
    if target_id == "error":
        display_error("Received MQTT message with no type")
        return 0, 0

    if msg_type == "hatch":
        save_food(arg1, arg2, target_id)
        return check_food_level(target_id)
    if msg_type == "heartbeat":
        save_heartbeat(arg1, arg2, target_id)
        return check_heartbeat(target_id)
    if msg_type == "hatch":
        save_hatch(arg1, arg2, target_id)
        return check_hatch(direction=arg1, hatchId=target_id)
