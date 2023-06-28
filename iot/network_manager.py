from iot.data_manager import collect_data


def boot():
    print("network starting up")


def receive(msg):
    # receive msg

    # read content, save in DB if necessary
    rec_msg_code = collect_data(msg)

    # azioni da eseguire dopo
    # switch rec_msg_code:
    if rec_msg_code == 0:  # nothing to do after saving msg in database
        return
