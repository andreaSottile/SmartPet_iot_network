#!/usr/bin/env python

from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource

from iot.data_manager import register_actuator


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
