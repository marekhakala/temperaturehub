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

from datetime import datetime, timedelta
from time import gmtime, strftime

import sqlite3
import xml.etree.ElementTree as ET

class XMLCurrentState(object):
    def __init__(self, configuration):
        self.root = None
        self.configuration = configuration

    def buildXML(self):
        self.root = ET.Element('response')
        self.root.set("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

        connect = sqlite3.connect(self.configuration.database_filename)
        cursor = connect.cursor()

        etemperatures = ET.SubElement(self.root, "temperatures")
        temperatures_count = 0

        for temperature in self.configuration.temperatures:
            values = (int(temperature["id"]), str(temperature["hostname"]), str(temperature["port"]),)
            cursor.execute("SELECT temperature_id, hostname, port, title, description, latitude, \
longitude, id FROM temperature WHERE temperature_id = ? AND hostname = ? AND port = ?", values)

            dataTemperature = cursor.fetchall()

            if len(dataTemperature) == 1:
                etemperature = ET.SubElement(etemperatures, "temperature")
                etemperature.set("index", str(temperature["id"]))
                temperatures_count += 1

                self.buildInfoValues(etemperature, dataTemperature)
                esensors = ET.SubElement(etemperature, "sensors")

                values = (int(dataTemperature[0][7]),)
                cursor.execute("SELECT sensor_id, description, temperature_id FROM sensor WHERE temperature_id = ?", values)

                dataSensor = cursor.fetchall()
                esensors.set("count", str(len(dataSensor)))

                for sensor in dataSensor:
                    esensor = ET.SubElement(esensors, "sensor")
                    esensor.set("id", str(sensor[0]))
                    description = ET.SubElement(esensor, "description")
                    description.text = str(sensor[1])

                    evalues = ET.SubElement(esensor, "values")
                    self.buildValues(cursor, evalues, (int(dataTemperature[0][7]), int(sensor[0]),))

        etemperatures.set("count", str(temperatures_count))

    def buildInfoValues(self, element, dataTemperature):
        element.set("title", str(dataTemperature[0][3]))

        description = ET.SubElement(element, "description")
        description.text = str(dataTemperature[0][4])

        elocation = ET.SubElement(element, "location")
        elatitude = ET.SubElement(elocation, "latitude")
        elatitude.text = str(dataTemperature[0][5])
        elongitude = ET.SubElement(elocation, "longitude")
        elongitude.text = str(dataTemperature[0][6])

    def buildValues(self, cursor, element, values):
        cursor.execute("SELECT temperature_id, sensor_id, celsius, fahrenheit, humidity, \
timestamp FROM measurement WHERE temperature_id = ? AND sensor_id = ? ORDER BY timestamp DESC", values)

        dataValues = cursor.fetchall()

        if len(dataValues) > 0:
            element.set("count", "3")

            value1 = ET.SubElement(element, "value")
            value1.set("type", "temperature")
            value1.set("unit", "celsius")
            value1.text = str(dataValues[0][2])

            value2 = ET.SubElement(element, "value")
            value2.set("type", "temperature")
            value2.set("unit", "fahrenheit")
            value2.text = str(dataValues[0][3])

            value3 = ET.SubElement(element, "value")
            value3.set("type", "humidity")
            value3.set("unit", "percentage")
            value3.text = str(dataValues[0][4])

    def xml(self):
        return ET.tostring(self.root, encoding="utf-8", method="xml")

class XMLHistory(object):
    def __init__(self, configuration):
        self.root = None
        self.configuration = configuration

    def buildXML(self):
        self.root = ET.Element('response')
        self.root.set("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

        connect = sqlite3.connect(self.configuration.database_filename)
        cursor = connect.cursor()

        to_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        from_timestamp = (datetime.utcnow() + timedelta(days=-self.configuration.historydays)).strftime("%Y-%m-%d %H:%M:%S")

        etemperatures = ET.SubElement(self.root, "temperatures")
        temperatures_count = 0

        for temperature in self.configuration.temperatures:
            values = (int(temperature["id"]), str(temperature["hostname"]), str(temperature["port"]),)
            cursor.execute("SELECT temperature_id, hostname, port, title, description, latitude, \
longitude, id FROM temperature WHERE temperature_id = ? AND hostname = ? AND port = ?", values)
            dataTemperature = cursor.fetchall()

            if len(dataTemperature) == 1:
                etemperature = ET.SubElement(etemperatures, "temperature")
                etemperature.set("index", str(temperature["id"]))
                temperatures_count += 1

                self.buildInfoValues(etemperature, dataTemperature)
                esensors = ET.SubElement(etemperature, "sensors")

                values = (int(dataTemperature[0][7]),)
                cursor.execute("SELECT sensor_id, description, temperature_id FROM sensor WHERE temperature_id = ?", values)
                dataSensor = cursor.fetchall()

                esensors.set("count", str(len(dataSensor)))

                for sensor in dataSensor:
                    esensor = ET.SubElement(esensors, "sensor")
                    esensor.set("id", str(sensor[0]))
                    edescription = ET.SubElement(esensor, "description")
                    edescription.text = str(sensor[1])

        etemperatures.set("count", str(temperatures_count))

        efilter = ET.SubElement(self.root, "filter")
        efilter_from = ET.SubElement(efilter, "from")
        efilter_from.text = str(from_timestamp)

        efilter_to = ET.SubElement(efilter, "to")
        efilter_to.text = str(to_timestamp)
        efilter_temperatures_ids = ET.SubElement(efilter, "temperaturesids")

        evalues = ET.SubElement(self.root, "values")

        for temperature in self.configuration.temperatures:
            temperature_id = ET.SubElement(efilter_temperatures_ids, "temperatureid")
            temperature_id.text = str(temperature["id"])
            self.buildValues(cursor, evalues, (int(temperature["id"]), str(from_timestamp), str(to_timestamp),))

    def buildInfoValues(self, element, dataTemperature):
        element.set("title", str(dataTemperature[0][3]))
        edescription = ET.SubElement(element, "description")
        edescription.text = str(dataTemperature[0][4])

        elocation = ET.SubElement(element, "location")
        elatitude = ET.SubElement(elocation, "latitude")
        elatitude.text = str(dataTemperature[0][5])
        elongitude = ET.SubElement(elocation, "longitude")
        elongitude.text = str(dataTemperature[0][6])

    def buildValues(self, cursor, element, values):
        cursor.execute("SELECT m.temperature_id, m.sensor_id, m.celsius, m.fahrenheit, m.humidity, m.timestamp \
FROM measurement m LEFT OUTER JOIN sensor s ON m.temperature_id = s.temperature_id \
WHERE m.temperature_id = ? AND m.timestamp >= ? AND m.timestamp <= ? LIMIT 20", values)
        dataMeasurement = cursor.fetchall()

        for measurement in dataMeasurement:
            esensor = ET.SubElement(element, "sensor")
            esensor.set("temperatureid", str(measurement[0]))
            esensor.set("sensorid", str(measurement[1]))
            esensor.set("timestamp", str(measurement[5]))

            evalue1 = ET.SubElement(esensor, "value")
            evalue1.set("type", "temperature")
            evalue1.set("unit", "celsius")
            evalue1.text = str(measurement[2])

            evalue2 = ET.SubElement(esensor, "value")
            evalue2.set("type", "temperature")
            evalue2.set("unit", "fahrenheit")
            evalue2.text = str(measurement[3])

            evalue3 = ET.SubElement(esensor, "value")
            evalue3.set("type", "humidity")
            evalue3.set("unit", "percentage")
            evalue3.text = str(measurement[4])

    def xml(self):
        return ET.tostring(self.root, encoding="utf-8", method="xml")
