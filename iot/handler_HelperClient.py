from coapthon.client.helperclient import HelperClient


def getConnectionHelperClient(nodeId):
    return coapConnectionHandler.coapConnectionDict[nodeId]


def createConnection(nodeId, actuatorAddress):
    coapConnectionHandler.coapConnectionDict[nodeId] = HelperClient(actuatorAddress)


class coapConnectionHandler:
    coapConnectionDict = {}
