#!/usr/bin/env python

from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource

from iot.utils import register_actuator


class ResExample(Resource):

    def __init__(self, name="ResExample", coap_server=None):
        super(ResExample, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "Basic Resource"

    def render_GET(self, request):
        digested_msg = request.payload.split("_")
        if digested_msg[0] == "food":
            register_actuator(digested_msg[1], digested_msg[0], request.source)
        elif digested_msg[0] == "hatch":
            register_actuator(digested_msg[1], digested_msg[0], request.source)
        return self


class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port), False)
        self.add_resource("hello/", ResExample())
