#
# Copyright 2015 by Marek Hakala <hakala.marek@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
#    limitations under the License.
#

import xml.etree.ElementTree as ET

class ConfigEntity(object):
    def __init__(self):
        self.hostname = None
        self.port = None
        self.updatetime = None
        self.filename = None
        self.database_filename = None
        self.temperatures = []

    def addTemperature(self, temperature):
        self.temperatures.append(temperature)

    def removeTemperature(self, temperature):
        self.temperatures.remove(temperature)

    def size(self):
        return len(self.temperatures)

    def __str__(self):
        output = "Hostname: " + str(self.hostname) + ":" + str(self.port) + "\n"
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
        entity.updatetime = self.root_element.find("updatetime").text
        entity.hostname = self.root_element.find("server/listen").text
        entity.port = self.root_element.find("server/port").text
        elements = self.root_element.findall("temperatures/temperature")

        index = 0
        for element in elements:
            entity.addTemperature({ "id" : index, "hostname" : element.find("hostname").text,
            "port" : element.find("port").text })
            index += 1

        return entity
