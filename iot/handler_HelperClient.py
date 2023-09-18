from coapthon.client.helperclient import HelperClient


def getConnectionHelperClient(nodeId):
    return coapConnectionHandler.coapConnectionDict[str(nodeId)]


def createConnection(nodeId, actuatorAddress):
    coapConnectionHandler.coapConnectionDict[str(nodeId)] = HelperClient(actuatorAddress)


class coapConnectionHandler:
    coapConnectionDict = {}
