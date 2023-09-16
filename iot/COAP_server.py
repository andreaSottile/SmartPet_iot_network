#!/usr/bin/env python
import threading

from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource

#import from tanganelli
from coapthon.serializer import Serializer
import socket
import logging
import collections
from coapthon.messages.response import Response
from coapthon import defines
from coapthon.messages.message import Message
from coapthon.messages.request import Request



from iot.data_manager import register_actuator

logger = logging.getLogger(__name__)

class ResExample(Resource):
    def __init__(self, name="ResExample", coap_server=None):
        super(ResExample, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "Basic Resource"

    def render_GET(self, request):
        print("Render_GET received request")
        digested_msg = request.payload.split("_")
        if digested_msg[0] == "food":
            register_actuator(digested_msg[1], digested_msg[0], request.source)
        elif digested_msg[0] == "hatch":
            register_actuator(digested_msg[1], digested_msg[0], request.source)
        return self


class CoAPServer(CoAP):
    host_address = None
    port_address = None
    multicast_setting = False

    def __init__(self, host, port, multicast=False):
        self.host_address = host
        self.port_address = port
        self.multicast_setting = multicast
        CoAP.__init__(self, (host, port), multicast)
        self.add_resource("hello", ResExample())

        print("CoAP Server start on " + host + ":" + str(port))
        print(self.root.dump())

    def start_server(self):
        try:
            print("COAP Server Listening")
            self.listen(30)
            print("COAP server STOPPED listening")
        except KeyboardInterrupt:
            print("Server Shutdown")
            self.close()
            print("Exiting...")

    def listen(self, timeout=10):
        """
        Listen for incoming messages. Timeout is used to check if the server must be switched off.

        :param timeout: Socket Timeout in seconds
        """
        self._socket.settimeout(float(timeout))
        while not self.stopped.isSet():
            try:
                data, client_address = self._socket.recvfrom(4096)
                if len(client_address) > 2:
                    client_address = (client_address[0], client_address[1])
            except socket.timeout:
                continue
            except Exception as e:
                if self._cb_ignore_listen_exception is not None and isinstance(self._cb_ignore_listen_exception,
                                                                               collections.Callable):
                    if self._cb_ignore_listen_exception(e, self):
                        continue
                raise
            try:
                serializer = Serializer()
                print(str(client_address[0]) + " port:" + str(client_address[1]) + "datagram to serialize:" + str(data))
                message = serializer.deserialize(data, client_address)
                if isinstance(message, int):
                    print("sono nella bad request")
                    logger.error("receive_datagram - BAD REQUEST")

                    rst = Message()
                    rst.destination = client_address
                    rst.type = defines.Types["RST"]
                    rst.code = message
                    rst.mid = self._messageLayer.fetch_mid()
                    self.send_datagram(rst)
                    continue

                logger.info("receive_datagram - " + str(message))
                if isinstance(message, Request):
                    transaction = self._messageLayer.receive_request(message)
                    if transaction.request.duplicated and transaction.completed:
                        logger.debug("message duplicated, transaction completed")
                        if transaction.response is not None:
                            self.send_datagram(transaction.response)
                        continue
                    elif transaction.request.duplicated and not transaction.completed:
                        logger.debug("message duplicated, transaction NOT completed")
                        self._send_ack(transaction)
                        continue
                    args = (transaction,)
                    t = threading.Thread(target=self.receive_request, args=args)
                    t.start()
                # self.receive_datagram(data, client_address)
                elif isinstance(message, Response):
                    logger.error("Received response from %s", message.source)

                else:  # is Message
                    transaction = self._messageLayer.receive_empty(message)
                    if transaction is not None:
                        with transaction:
                            self._blockLayer.receive_empty(message, transaction)
                            self._observeLayer.receive_empty(message, transaction)

            except RuntimeError:
                logger.exception("Exception with Executor")
        self._socket.close()



