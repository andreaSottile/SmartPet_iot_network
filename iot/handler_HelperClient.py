from coapthon.client.helperclient import HelperClient

class coapConnectionHandler:


    coapConnectionDict={}

    def createConnection(self, nodeId, actuatorAddress):
        coapConnectionHandler.coapConnectionDict[nodeId]= HelperClient(actuatorAddress)

    def getConnectionHelperClient(self, nodeId):
        return coapConnectionHandler.coapConnectionDict[nodeId]