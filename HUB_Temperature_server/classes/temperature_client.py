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
        return "id: " + str(self.id) + ", celsius: " + str(self.celsius)
        + ", fahrenheit: " + str(self.fahrenheit) + ", humidity: " + str(self.humidity)

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
        output = "- Temperature " + str(self.id) + "(" + str(self.title) + ")\n"
        output += "- Addr: " + str(self.hostname) + ":" + str(self.port) + "\n"
        output += "- Location: " + str(self.location) + "\n"

        for sensor in self.sensors:
            output += "-- " + str(sensor) + "\n"

        return output

class TemperatureClient(object):
    def __init__(self, temperature):
        self.temperature = temperature

    def fetchData(self):
        try:
            connection = http.client.HTTPConnection(self.temperature["hostname"],
                                                self.temperature["port"],
                                                timeout = 12)
            connection.request('GET', '/')
            response = connection.getresponse()

            if response.status == 200:
                print ("- Temperature|" + str(self.temperature["hostname"])
                 + ":" + str(self.temperature["port"]) + ": OK")
                response_source = response.read().decode()
                connection.close();
                data = self.parseData(response_source)
                return data

            connection.close();

        except Exception as e:
            print ("- Temperature|" + str(self.temperature["hostname"])
            + ":" + str(self.temperature["port"]) + ": " + str(e))

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
        connect = sqlite3.connect("./measurement.db")
        cursor = connect.cursor()

        # Temperatures
        cursor.execute("SELECT id FROM temperature WHERE temperature_id = " + str(info.id) + " \
                                AND hostname = \"" + info.hostname + "\" \
                                AND port = \"" + info.port + "\"")
        dataAll = cursor.fetchall()

        if len(dataAll) == 0:
            result = cursor.execute("INSERT INTO temperature (temperature_id, hostname, port, title, \
                                    description, latitude, longitude) VALUES (" + str(info.id) + ", \
                                    \"" + str(info.hostname) + "\", \"" + str(info.port) + "\", \
                                    \"" + str(info.title) + "\", \"" + str(info.description) + "\", \
                                    \"" + str(info.location[0]) + "\", \"" + str(info.location[1]) + "\")")
            temperature_id = result.lastrowid

            for sensor in info.sensors:
                cursor.execute("INSERT INTO sensor (sensor_id, description, temperature_id) \
                                VALUES (" + str(sensor.id) + ", \"" + str(sensor.description) + "\", \
                                \"" + str(temperature_id) + "\")")
            connect.commit()
        else:
            temperature_id = dataAll[0][0]

        return temperature_id

    def saveToDatabase(self, info, temperature_id):
        connect = sqlite3.connect("./measurement.db")
        cursor = connect.cursor()

        for sensor in info.sensors:
            cursor.execute("INSERT INTO measurement (temperature_id, sensor_id, celsius, fahrenheit, humidity) \
                            VALUES (" + str(temperature_id) + ", " + str(sensor.id) + ", \"" + str(sensor.celsius) + "\", \
                            \"" + str(sensor.fahrenheit) + "\", \"" + str(sensor.humidity) + "\")")
        connect.commit()
