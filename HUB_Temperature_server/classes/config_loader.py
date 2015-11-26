import xml.etree.ElementTree as ET

class ConfigEntity(object):
    def __init__(self):
        self.listen = None
        self.port = None
        self.temperatures = []

    def addTemperature(self, temperature):
        self.temperatures.append(temperature)

    def removeTemperature(self, temperature):
        self.temperatures.remove(temperature)

    def size(self):
        return len(self.temperatures)

    def __str__(self):
        output = " - Hostname: " + str(self.listen) + ":" + str(self.port) + "\n"
        output += " - Temperatures count: " + str(self.size()) + "\n"

        for index, temperature in enumerate(self.temperatures):
            temp = "#" + str(index) + "|" + str(temperature["hostname"]) + ":" + str(temperature["port"])
            output += " -- Temperature " + temp + "\n"

        return output

class ConfigLoader(object):
    def __init__(self, filename):
        self.filename = filename

    def loadFile(self):
        self.root_element = ET.parse(self.filename).getroot()
        # TODO: XML schema validation

    def getConfiguration(self):
        entity = ConfigEntity()
        entity.listen = self.root_element.find("server/listen").text
        entity.port = self.root_element.find("server/port").text
        elements = self.root_element.findall("temperatures/temperature")

        for element in elements:
            entity.addTemperature({ "hostname" : element.find("hostname").text,
            "port" : element.find("port").text })

        return entity
