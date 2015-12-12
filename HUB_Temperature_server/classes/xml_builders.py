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

        temperatures = ET.SubElement(self.root, "temperatures")
        temperatures.set("count", str(len(self.configuration.temperatures)))

        for temperature in self.configuration.temperatures:
            values = (int(temperature["id"]), str(temperature["hostname"]), str(temperature["port"]),)
            cursor.execute("SELECT temperature_id, hostname, port, title, description, latitude, \
longitude, id FROM temperature WHERE temperature_id = ? AND hostname = ? AND port = ?", values)

            dataTemperature = cursor.fetchall()
            if len(dataTemperature) == 1:
                etemperature = ET.SubElement(temperatures, "temperature")
                etemperature.set("title", str(dataTemperature[0][3]))
                etemperature.set("index", str(temperature["id"]))

                description = ET.SubElement(etemperature, "description")
                description.text = dataTemperature[0][4]

                location = ET.SubElement(etemperature, "location")
                latitude = ET.SubElement(location, "latitude")
                latitude.text = dataTemperature[0][5]
                longitude = ET.SubElement(location, "longitude")
                longitude.text = dataTemperature[0][6]

                sensors = ET.SubElement(etemperature, "sensors")

                values = (int(dataTemperature[0][7]),)
                cursor.execute("SELECT sensor_id, description, temperature_id FROM sensor WHERE temperature_id = ?", values)

                dataSensor = cursor.fetchall()
                sensors.set("count", str(len(dataSensor)))

                for sensor in dataSensor:
                    esensor = ET.SubElement(sensors, "sensor")
                    esensor.set("id", str(sensor[0]))
                    description = ET.SubElement(esensor, "description")
                    description.text = str(sensor[1])

                    evalues = ET.SubElement(esensor, "values")

                    values = (int(dataTemperature[0][7]), int(sensor[0]),)
                    cursor.execute("SELECT temperature_id, sensor_id, celsius, fahrenheit, humidity, \
timestamp FROM measurement WHERE temperature_id = ? AND sensor_id = ? ORDER BY timestamp DESC", values)
                    dataValues = cursor.fetchall()

                    if len(dataValues) > 0:
                        evalues.set("count", "3")

                        value1 = ET.SubElement(evalues, "value")
                        value1.set("type", "temperature")
                        value1.set("unit", "celsius")
                        value1.text = dataValues[0][2]

                        value2 = ET.SubElement(evalues, "value")
                        value2.set("type", "temperature")
                        value2.set("unit", "fahrenheit")
                        value2.text = dataValues[0][3]

                        value3 = ET.SubElement(evalues, "value")
                        value3.set("type", "humidity")
                        value3.set("unit", "percentage")
                        value3.text = dataValues[0][4]

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

        temperatures = ET.SubElement(self.root, "temperatures")
        temperatures.set("count", str(len(self.configuration.temperatures)))

        for temperature in self.configuration.temperatures:
            values = (int(temperature["id"]), str(temperature["hostname"]), str(temperature["port"]),)
            cursor.execute("SELECT temperature_id, hostname, port, title, description, latitude, \
longitude, id FROM temperature WHERE temperature_id = ? AND hostname = ? AND port = ?", values)
            dataTemperature = cursor.fetchall()

            if len(dataTemperature) == 1:
                etemperature = ET.SubElement(temperatures, "temperature")
                etemperature.set("title", str(dataTemperature[0][3]))
                etemperature.set("index", str(temperature["id"]))

                description = ET.SubElement(etemperature, "description")
                description.text = dataTemperature[0][4]

                location = ET.SubElement(etemperature, "location")
                latitude = ET.SubElement(location, "latitude")
                latitude.text = dataTemperature[0][5]
                longitude = ET.SubElement(location, "longitude")
                longitude.text = dataTemperature[0][6]

                sensors = ET.SubElement(etemperature, "sensors")

                values = (int(dataTemperature[0][7]),)
                cursor.execute("SELECT sensor_id, description, temperature_id FROM sensor WHERE temperature_id = ?", values)
                dataSensor = cursor.fetchall()

                sensors.set("count", str(len(dataSensor)))

                for sensor in dataSensor:
                    esensor = ET.SubElement(sensors, "sensor")
                    esensor.set("id", str(sensor[0]))
                    description = ET.SubElement(esensor, "description")
                    description.text = str(sensor[1])

        efilter = ET.SubElement(self.root, "filter")
        efilter_from = ET.SubElement(efilter, "from")
        efilter_from.text = from_timestamp

        efilter_to = ET.SubElement(efilter, "to")
        efilter_to.text = to_timestamp
        efilter_temperatures_ids = ET.SubElement(efilter, "temperaturesids")

        evalues = ET.SubElement(self.root, "values")

        for temperature in self.configuration.temperatures:
            temperature_id = ET.SubElement(efilter_temperatures_ids, "temperatureid")
            temperature_id.text = str(temperature["id"])

            print(str(from_timestamp))
            print(str(to_timestamp))

            values = (int(temperature["id"]), str(from_timestamp), str(to_timestamp),)
            cursor.execute("SELECT m.temperature_id, m.sensor_id, m.celsius, m.fahrenheit, m.humidity, m.timestamp \
FROM measurement m LEFT OUTER JOIN sensor s ON m.temperature_id = s.temperature_id \
WHERE m.temperature_id = ? AND m.timestamp >= ? AND m.timestamp <= ?", values)
            dataMeasurement = cursor.fetchall()

            for measurement in dataMeasurement:
                esensor = ET.SubElement(evalues, "sensor")
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
