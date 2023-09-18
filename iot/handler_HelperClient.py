from coapthon.client.helperclient import HelperClient


def getConnectionHelperClient(nodeId):
    print("sono nella getconnection e sto per stampare le key del dizionario")
    for key in coapConnectionHandler.coapConnectionDict.keys():
        print(key)
    return coapConnectionHandler.coapConnectionDict[nodeId]


def createConnection(nodeId, actuatorAddress):
    coapConnectionHandler.coapConnectionDict[nodeId] = HelperClient(actuatorAddress)
    print("fatto con nodeId:" + str(nodeId) + "e actuatorAddress:" + str(actuatorAddress))
    for key in coapConnectionHandler.coapConnectionDict.keys():
        print(key)


class coapConnectionHandler:
    coapConnectionDict = {}
