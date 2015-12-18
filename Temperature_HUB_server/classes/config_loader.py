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

class ConfigEntitySingleton:
    def __init__(self,_class):
        self._class = _class
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance == None:
            self.instance = self._class(*args, **kwds)
        return self.instance

class ConfigEntity(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigEntity, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.hostname = None
        self.port = None
        self.updatetime = None
        self.historydays = None
        self.filename = None
        self.page_limit = None
        self.pages_limit = None
        self.database_filename = None
        self.log_filename = None
        self.assets_path = None
        self.thermometers = []

    def addThermometer(self, thermometer):
        self.thermometers.append(thermometer)

    def removeThermometer(self, thermometer):
        self.thermometers.remove(thermometer)

    def size(self):
        return len(self.thermometers)

    def __str__(self):
        output = "Hostname: " + str(self.hostname) + ":" + str(self.port) + "\n"
        output += " - Thermometers count: " + str(self.size()) + "\n"

        for index, thermometer in enumerate(self.thermometers):
            thermo = "#" + str(index) + "|" + str(thermometer["hostname"]) + ":" + str(thermometer["port"])
            output += " -- thermometer " + thermo + "\n"

        return output

class ConfigLoader(object):
    def __init__(self, filename):
        self.filename = filename
        self.configSingleton = ConfigEntitySingleton(ConfigEntity)

    def loadFile(self):
        self.root_element = ET.parse(self.filename).getroot()
        # TODO: XML schema validation

    def getConfiguration(self):
        entity = self.configSingleton()
        entity.updatetime = self.root_element.find("updatetime").text
        entity.database_filename = self.root_element.find("databasefile").text
        entity.log_filename = self.root_element.find("logfile").text
        entity.assets_path = self.root_element.find("assetspath").text
        entity.page_limit = int(self.root_element.find("pagelimit").text)
        entity.pages_limit = int(self.root_element.find("pageslimit").text)
        entity.historydays = int(self.root_element.find("historydays").text)
        entity.hostname = self.root_element.find("server/listen").text
        entity.port = self.root_element.find("server/port").text
        elements = self.root_element.findall("thermometers/thermometer")

        index = 0
        for element in elements:
            entity.addThermometer({ "id" : index, "hostname" : element.find("hostname").text,
            "port" : element.find("port").text })
            index += 1

        return entity
