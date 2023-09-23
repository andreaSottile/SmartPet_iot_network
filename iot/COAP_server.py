#!/usr/bin/env python
import threading

from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource

# import from tanganelli
from coapthon.serializer import Serializer
import socket
import logging
import collections
from coapthon.messages.response import Response
from coapthon import defines
from coapthon.messages.message import Message
from coapthon.messages.request import Request
import struct
from coapthon.messages.option import Option

from iot.data_manager import register_actuator
from iot.pubsubconfig import debug_mode

logger = logging.getLogger(__name__)


class ResExample(Resource):
    def __init__(self, name="ResExample", coap_server=None):
        super(ResExample, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "Basic Resource"

    def render_GET(self, request):
        if debug_mode:
            print("Render_GET received request")
        digested_msg = request.payload.split("_")
        utf8_msg = digested_msg[1][0:3]
        if debug_mode:
            print(utf8_msg)
        if digested_msg[0] == "food":
            register_actuator(utf8_msg, digested_msg[0], request.source)
        elif digested_msg[0] == "hatch":
            register_actuator(utf8_msg, digested_msg[0], request.source)
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
                if debug_mode:
                    print(str(client_address[0]) + " port:" + str(client_address[1]) + "datagram to serialize:" + str(
                        data))
                message = self.deserialize(data, client_address)
                if isinstance(message, int):
                    if debug_mode:
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

    def deserialize(self, datagram, source):
        """
        De-serialize a stream of byte to a message.

        :param datagram: the incoming udp message
        :param source: the source address and port (ip, port)
        :return: the message
        :rtype: Message
        """
        try:
            fmt = "!BBH"
            pos = struct.calcsize(fmt)
            s = struct.Struct(fmt)
            values = s.unpack_from(datagram)
            if debug_mode:
                print("first " + str(values[0]) + " code:" + str(values[1]) + " mid:" + str(values[2]))
            first = values[0]
            code = values[1]
            mid = values[2]
            version = (first & 0xC0) >> 6
            message_type = (first & 0x30) >> 4
            token_length = (first & 0x0F)
            if debug_mode:
                print(
                    "version " + str(version) + " message_type:" + str(message_type) + " token_length:" + str(token_length))
            if Serializer.is_response(code):
                if debug_mode:
                    print("è un response")
                message = Response()
                message.code = code
            elif Serializer.is_request(code):
                if debug_mode:
                    print("è un request")
                message = Request()
                message.code = code
            else:
                if debug_mode:
                    print("nessun dei 2")
                message = Message()
            message.source = source
            message.destination = None
            message.version = version
            message.type = message_type
            message.mid = mid
            if token_length > 0:
                message.token = datagram[pos:pos + token_length]
            else:
                message.token = None

            pos += token_length
            current_option = 0
            values = datagram[pos:]
            length_packet = len(values)
            pos = 0
            while pos < length_packet:
                next_byte = struct.unpack("B", values[pos].to_bytes(1, "big"))[0]
                pos += 1
                if next_byte != int(defines.PAYLOAD_MARKER):
                    # the first 4 bits of the byte represent the option delta
                    # delta = self._reader.read(4).uint
                    num, option_length, pos = Serializer.read_option_value_len_from_byte(next_byte, pos, values)
                    logger.debug("option value (delta): %d len: %d", num, option_length)
                    current_option += num
                    # read option
                    try:
                        option_item = defines.OptionRegistry.LIST[current_option]
                    except KeyError:
                        (opt_critical, _, _) = defines.OptionRegistry.get_option_flags(current_option)
                        if opt_critical:
                            raise AttributeError("Critical option %s unknown" % current_option)
                        else:
                            # If the non-critical option is unknown
                            # (vendor-specific, proprietary) - just skip it
                            logger.warning("unrecognized option %d", current_option)
                    else:
                        if option_length == 0:
                            value = None
                        elif option_item.value_type == defines.INTEGER:
                            tmp = values[pos: pos + option_length]
                            value = 0
                            for b in tmp:
                                value = (value << 8) | struct.unpack("B", b.to_bytes(1, "big"))[0]
                        elif option_item.value_type == defines.OPAQUE:
                            tmp = values[pos: pos + option_length]
                            value = tmp
                        else:
                            value = values[pos: pos + option_length]

                        option = Option()
                        option.number = current_option
                        option.value = Serializer.convert_to_raw(current_option, value, option_length)

                        message.add_option(option)
                        if option.number == defines.OptionRegistry.CONTENT_TYPE.number:
                            message.payload_type = option.value
                    finally:
                        pos += option_length
                else:

                    if length_packet <= pos:
                        # log.err("Payload Marker with no payload")
                        raise AttributeError("Packet length %s, pos %s" % (length_packet, pos))
                    message.payload = ""
                    payload = values[pos:]
                    if hasattr(message, 'payload_type') and message.payload_type in [
                        defines.Content_types["application/octet-stream"],
                        defines.Content_types["application/exi"],
                        defines.Content_types["application/cbor"]
                    ]:
                        message.payload = payload
                    else:
                        try:
                            message.payload = payload.decode("utf-8", "ignore")
                        except AttributeError:
                            message.payload = payload
                    pos += len(payload)

            return message
        except AttributeError:
            if debug_mode:
                print("attribute error")
            return defines.Codes.BAD_REQUEST.number
        except struct.error:
            if debug_mode:
                print("struct error")
            return defines.Codes.BAD_REQUEST.number
        except UnicodeDecodeError as e:
            if debug_mode:
                print("unicode error" + str(e))
            logger.debug(e)
            return defines.Codes.BAD_REQUEST.number
