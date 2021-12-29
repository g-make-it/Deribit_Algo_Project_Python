from gatherData import GatherData
from generateSignals import GenerateSignals
from orderManagement import OrderManagement
from positionManagement import PositionManagement
from clients import Clients
from algorithmScaling import AlgorithmScaling
import time

class Controller:
    def __init__(self):
        self.gatherDataObject = GatherData()
        self.generateSignalObject = GenerateSignals()
        self.orderManagementObject = OrderManagement()
        self.positionManagementObject = PositionManagement()
        self.client = Clients()
        self.algorithm = AlgorithmScaling()

    def run(self):
        clientMap = self.client.authenticate()
        self.gatherDataObject.setting_url(clientMap)
        self.positionManagementObject.setClients(clientMap)
        self.gatherDataObject.start()

        while(True):
            # modular objects, this way all objects are created externally and can be appened on
            data = self.gatherDataObject.run(clientMap)

            # problem with data access and waiting a while and resetting the connection would be a good idea
            if data == None: continue

            positionStatus = self.positionManagementObject.findOurCurrentPosition()

            if (positionStatus != None) and ("error" in positionStatus): continue

            self.orderManagementObject.run(clientMap)

            mapOfSignals = self.generateSignalObject.run(data,positionStatus, self.orderManagementObject)

            self.algorithm.run(data,mapOfSignals, self.positionManagementObject, self.orderManagementObject)