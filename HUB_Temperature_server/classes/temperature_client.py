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

import sqlite3
import http.client
import xml.etree.ElementTree as ET

class SensorInfo(object):
    def __init__(self):
        self.id = None
        self.description = None
        self.celsius = None
        self.fahrenheit = None
        self.humidity = None

    def __str__(self):
        return "id: " + str(self.id) + ", celsius: " + str(self.celsius) + ", fahrenheit: \
" + str(self.fahrenheit) + ", humidity: " + str(self.humidity)

class TemperatureInfo(object):
    def __init__(self):
        self.id = None
        self.title = None
        self.description = None
        self.location = (0.0000, 0.0000)
        self.sensors = []

        self.hostname = None
        self.port = None

    def __str__(self):
        output = "Temperature " + str(self.id) + "(" + str(self.title) + ")\n"
        output += "- Addr: " + str(self.hostname) + ":" + str(self.port) + "\n"
        output += "- Location: " + str(self.location) + "\n"

        for sensor in self.sensors:
            output += "-- Sensor " + str(sensor) + "\n"

        return output

class TemperatureClient(object):
    def __init__(self, configuration, temperature):
        self.configuration = configuration
        self.temperature = temperature

    def fetchData(self):
        try:
            connection = http.client.HTTPConnection(self.temperature["hostname"],
                                                self.temperature["port"],
                                                timeout = 12)
            connection.request('GET', '/')
            response = connection.getresponse()

            if response.status == 200:
                self.configuration.logger.info("Temperature|" + str(self.temperature["hostname"])
                + ":" + str(self.temperature["port"]) + ": OK")
                response_source = response.read().decode()
                connection.close();
                data = self.parseData(response_source)
                return data

            connection.close();

        except Exception as e:
            self.configuration.logger.error("Temperature|" + str(self.temperature["hostname"])
            + ":" + str(self.temperature["port"]) + ": " + str(e))
            return None

    def parseData(self, data):
        root = ET.fromstring(data)
        # TODO: XML schema validation

        info = TemperatureInfo()
        info.id = self.temperature["id"]
        info.title = root.find("title").text
        info.description = root.find("description").text
        info.location = (root.find("location/latitude").text, root.find("location/longitude").text)
        sensors = root.findall("sensors/sensor")

        for sensor in sensors:
            sensor_info = SensorInfo()
            sensor_info.id = sensor.attrib["id"]
            sensor_info.description = sensor.find("description").text
            values = sensor.findall("values/value")

            for value in values:
                if value.attrib["type"] == "temperature" and value.attrib["unit"] == "celsius":
                    sensor_info.celsius = value.text
                elif value.attrib["type"] == "temperature" and value.attrib["unit"] == "fahrenheit":
                    sensor_info.fahrenheit = value.text
                elif value.attrib["type"] == "humidity" and value.attrib["unit"] == "percentage":
                    sensor_info.humidity = value.text

            info.sensors.append(sensor_info)
            info.hostname = self.temperature["hostname"]
            info.port = self.temperature["port"]

        return info

    def getTemperatureId(self, info):
        connect = sqlite3.connect(self.configuration.database_filename)
        cursor = connect.cursor()

        # Debug info
        self.configuration.logger.debug(info)

        # Temperatures
        values = (int(info.id), str(info.hostname), str(info.port),)
        cursor.execute("SELECT id FROM temperature WHERE temperature_id = ? \
                                AND hostname = ? AND port = ?", values)

        dataAll = cursor.fetchall()

        if len(dataAll) == 0:
            values = (str(info.id), str(info.hostname), str(info.port),
                      str(info.title), str(info.description), str(info.location[0]), str(info.location[1]),)
            result = cursor.execute("INSERT INTO temperature (temperature_id, hostname, port, title, \
                                    description, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?)", values)
            temperature_id = result.lastrowid

            for sensor in info.sensors:
                values = (str(sensor.id), str(sensor.description), str(temperature_id),)
                cursor.execute("INSERT INTO sensor (sensor_id, description, temperature_id) \
                                VALUES (?, ?, ?)", values)
            connect.commit()
        else:
            temperature_id = dataAll[0][0]

        return temperature_id

    def saveToDatabase(self, info, temperature_id):
        connect = sqlite3.connect(self.configuration.database_filename)
        cursor = connect.cursor()

        for sensor in info.sensors:
            values = (str(temperature_id), str(sensor.id), str(sensor.celsius),
                      str(sensor.fahrenheit), str(sensor.humidity),)
            cursor.execute("INSERT INTO measurement (temperature_id, sensor_id, celsius, fahrenheit, humidity) \
                            VALUES (?, ?, ?, ?, ?)", values)
        connect.commit()
