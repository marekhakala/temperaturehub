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

import logging
import logging.handlers

from lxml import etree
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

        self.logger = None
        self.log_filename = None

    def initFileLogger(self, logger):
        logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] >> %(message)s")

        if self.log_filename != None and logger != None:
            # Rotating log file (Max size 5 MB)
            fileHandler = logging.handlers.RotatingFileHandler(self.log_filename, maxBytes=(1048576*5), backupCount=7)
            fileHandler.setFormatter(logFormatter)

            logger.addHandler(fileHandler)
            self.logger = logger

    def __str__(self):
        return "Hostname: " + str(self.hostname) + ":" + str(self.port) + "\n"

class XMLFileValidator(object):
    def __init__(self, schema_filename):
        self.schema_filename = schema_filename

        with open(self.schema_filename, 'rb') as xml_file:
            xmlschema_root = etree.XML(xml_file.read())

        self.xml_schema = etree.XMLSchema(xmlschema_root)
        self.xml_parser = etree.XMLParser(schema=self.xml_schema)

    def validate(self, xml_filename):
        try:
            with open(xml_filename, 'rb') as xml_file:
                etree.fromstring(xml_file.read(), self.xml_parser)
            return True
        except etree.XMLSchemaError:
            return False

class ConfigLoader(object):
    def __init__(self, filename):
        self.filename = filename
        self.configSingleton = ConfigEntitySingleton(ConfigEntity)

    def loadFile(self):
        validator = XMLFileValidator(self.filename + ".xsd")
        validator.validate(self.filename)
        self.root_element = ET.parse(self.filename).getroot()

    def getConfiguration(self):
        entity = self.configSingleton()
        entity.hostname = self.root_element.find("server/listen").text
        entity.port = self.root_element.find("server/port").text
        entity.log_filename = self.root_element.find("logfile").text

        return entity
