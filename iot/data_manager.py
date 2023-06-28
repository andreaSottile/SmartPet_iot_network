from Network_Controller.models import Food


# MSG TEMPLATE:
# { type:[Food, Heartbeat, Window] config:[false,true] arguments:{a:1 b:2 c:3} }


def decode_message(raw_msg):
    if not raw_msg.config:
        t = raw_msg.type
        if t == "food":
            msg = raw_msg.arguments.lvl, raw_msg.arguments.time, raw_msg.arguments.cid
            return t, msg
        if t == "heartbeat":
            msg = raw_msg.arguments.freq, raw_msg.arguments.time, raw_msg.arguments.pid
            return t, msg
        if t == "window":
            msg = raw_msg.arguments.dir, raw_msg.arguments.time, raw_msg.arguments.wid
            return t, msg


def save_food(food_msg):
    node_id, food_level, timestamp = decode_message(food_msg)
    f = Food(lvl=food_level, time=timestamp, containerID=node_id)
    f.save()


def collect_data(raw_msg):
    msg_type, msg_content = decode_message(raw_msg)
