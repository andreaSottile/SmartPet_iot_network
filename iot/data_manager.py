from Network_Controller.models import Food, Heartbeat, Trapdoor


# MSG TEMPLATE:
# { type:[Food, Heartbeat, Window] config:[false,true] arguments:{a:1 b:2 c:3} }


def decode_message(raw_msg):
    """
    Reads a json (obtained from a remote message) and decodes it based on the type;
    the output is ready to be saved in a new database row.

    param raw_msg: a json element like { config: t , type:{ lvl:a , time:b, id:c } }
    :return: a tuple (type,content), where type is a string ["error","food","heartbeat","window"]
    """
    t = raw_msg.type
    if not raw_msg.config:  # content message
        if t == "food":
            msg = raw_msg.arguments.lvl, raw_msg.arguments.time, raw_msg.arguments.cid
            return t, msg
        if t == "heartbeat":
            msg = raw_msg.arguments.freq, raw_msg.arguments.time, raw_msg.arguments.pid
            return t, msg
        if t == "window":
            msg = raw_msg.arguments.dir, raw_msg.arguments.time, raw_msg.arguments.wid
            return t, msg
        return "error", "content msg: type not found"
    else:  # config message
        # only content messages should be received by the controller
        return "error", "received a config msg for type " + t
    # IL CONTROLLORE INVIA I CONFIG MSG, NON LI RICEVE
    #   if t == "food":
    #       msg = raw_msg.arguments.lvlmax, raw_msg.arguments.lvlmin, raw_msg.arguments.lvlth, raw_msg.arguments.cid
    #       return "config_food", msg
    #   if t == "heartbeat":
    #       msg = raw_msg.arguments.freqhigh, raw_msg.arguments.freqlow, raw_msg.arguments.pid
    #       return "config_heartbeat", msg
    #   if t == "window":
    #       msg = raw_msg.arguments.unlocked, raw_msg.arguments.wid
    #       return "config_window", msg


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
    Saves a new tuple in the windows table

    param msg_content: a tuple containing direction,timestamp,windowId
    """
    direction, time, trapdoorId = decode_message(msg_content)
    w = Trapdoor(direction_Trigger=direction, time=time, windowId=trapdoorId)
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
     :return: true if the container is above the threshold
     false if the container should be refilled
     """
    pass


def check_window(direction, windowId):
    """
      Check food level left in each container, according to the most recent message received

      param msg_content: id of the food container to be checked
      :return: true if the container is above the threshold
      false if the container should be refilled
      """
    pass


def check_heartbeat(petId):
    """
      Check food level left in each container, according to the most recent message received

      :return: true if the container is above the threshold
      false if the container should be refilled
      """
    pass


def collect_data(raw_msg):
    """
    Called when a new message is received;
    it reads the message, saves it if necessary, and eventually perform control actions

    param raw_msg: a msg received in mqtt
    :return: (code,target)
    code 0: no further actions are necessary
    other codes: more actions to be performed
    target: the target of following actions (meaningless for code=0)
    """
    msg_type, msg_content = decode_message(raw_msg)
    if type == "error":
        display_error(msg_content)
        return 0, 0
    if type == "food":
        save_food(msg_content)
        if check_food_level(msg_content.containerId):
            return 0, 0
        else:
            return "refill", msg_content.containerId
    if type == "heartbeat":
        save_heartbeat(msg_content)
        if check_heartbeat(msg_content.petId):
            # TODO send emergency alert
            pass
        return 0, 0
    if type == "window":
        save_trapdoor(msg_content)
        if check_window(msg_content.direction, msg_content.windowId):
            return 0, 0
        else:
            return "window", msg_content.windowId
