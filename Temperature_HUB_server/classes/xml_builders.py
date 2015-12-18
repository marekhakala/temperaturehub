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
        self.cursor = None
        self.configuration = configuration

    def buildXML(self):
        self.root = ET.Element('response')
        self.root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.set("xsi:noNamespaceSchemaLocation", "assets?filename=current_state.xsd")
        self.root.set("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

        connect = sqlite3.connect(self.configuration.database_filename)
        self.cursor = connect.cursor()

        ethermometers = ET.SubElement(self.root, "thermometers")
        thermometers_count = 0

        for thermometer in self.configuration.thermometers:
            values = (int(thermometer["id"]), str(thermometer["hostname"]), str(thermometer["port"]),)
            self.cursor.execute("SELECT thermometer_id, hostname, port, title, description, latitude, \
longitude, id FROM thermometer WHERE thermometer_id = ? AND hostname = ? AND port = ?", values)

            dataThermometer = self.cursor.fetchall()

            if len(dataThermometer) == 1:
                ethermometer = ET.SubElement(ethermometers, "thermometer")
                ethermometer.set("index", str(thermometer["id"]))
                thermometers_count += 1

                self.buildInfoValues(ethermometer, dataThermometer)
                esensors = ET.SubElement(ethermometer, "sensors")

                values = (int(dataThermometer[0][7]),)
                self.cursor.execute("SELECT sensor_id, description, thermometer_id FROM sensor WHERE thermometer_id = ?", values)

                dataSensor = self.cursor.fetchall()
                esensors.set("count", str(len(dataSensor)))

                for sensor in dataSensor:
                    esensor = ET.SubElement(esensors, "sensor")
                    esensor.set("index", str(sensor[0]))
                    description = ET.SubElement(esensor, "description")
                    description.text = str(sensor[1])

                    evalues = ET.SubElement(esensor, "values")
                    self.buildValues(evalues, (int(dataThermometer[0][7]), int(sensor[0]),))

        ethermometers.set("count", str(thermometers_count))

    def buildInfoValues(self, element, dataThermometer):
        element.set("title", str(dataThermometer[0][3]))

        description = ET.SubElement(element, "description")
        description.text = str(dataThermometer[0][4])

        elocation = ET.SubElement(element, "location")
        elatitude = ET.SubElement(elocation, "latitude")
        elatitude.text = str(dataThermometer[0][5])
        elongitude = ET.SubElement(elocation, "longitude")
        elongitude.text = str(dataThermometer[0][6])

    def buildValues(self, element, values):
        self.cursor.execute("SELECT thermometer_id, sensor_id, celsius, fahrenheit, humidity, \
timestamp FROM measurement WHERE thermometer_id = ? AND sensor_id = ? ORDER BY timestamp DESC", values)
        dataValues = self.cursor.fetchall()

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
        self.cursor = None
        self.thermometer_id = None
        self.thermometer_index = None
        self.efilter_page = None
        self.efilter_thermometer = None
        self.configuration = configuration

    def buildXML(self, thermometer_index, page):
        self.root = ET.Element('response')
        self.root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.set("xsi:noNamespaceSchemaLocation", "assets?filename=history.xsd")
        self.root.set("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

        connect = sqlite3.connect(self.configuration.database_filename)
        self.cursor = connect.cursor()

        to_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        from_timestamp = (datetime.utcnow() + timedelta(days=-self.configuration.historydays)).strftime("%Y-%m-%d %H:%M:%S")
        self.thermometer_id = -1

        if thermometer_index >= len(self.configuration.thermometers):
            thermometer_index = 0

        self.buildThermometerValues(thermometer_index, self.thermometer_id)
        self.buildFilterValues(from_timestamp, to_timestamp)
        self.thermometer_index = str(thermometer_index)
        self.efilter_thermometer.text = self.thermometer_index

        thermometers_ids = ET.SubElement(self.root, "thermometersids")
        epages = ET.SubElement(self.root, "pages")
        evalues = ET.SubElement(self.root, "values")
        self.buildThermometersIdValues(thermometers_ids, thermometer_index)

        values = (self.thermometer_id, str(from_timestamp), str(to_timestamp),)
        self.buildValues(epages, evalues, values, page)

    def buildThermometersIdValues(self, thermometers_ids, thermometer_index):
        for thermometer in self.configuration.thermometers:
            if self.isThermometerInDatabase(thermometer["id"]):
                ethermometer_id = ET.SubElement(thermometers_ids, "thermometerid")
                ethermometer_id.text = str(thermometer["id"])

                if thermometer["id"] == thermometer_index:
                    ethermometer_id.set("current", str("true"))

    def buildThermometerValues(self, thermometer_index, thermometer_id):
        values = (int(thermometer_index),)
        self.cursor.execute("SELECT thermometer_id, hostname, port, title, description, latitude, \
        longitude, id FROM thermometer WHERE thermometer_id = ?", values)
        dataThermometer = self.cursor.fetchall()

        if len(dataThermometer) == 1:
            ethermometer = ET.SubElement(self.root, "thermometer")
            ethermometer.set("index", str(thermometer_index))
            self.thermometer_id = int(dataThermometer[0][7])

            self.buildInfoValues(ethermometer, dataThermometer)
            esensors = ET.SubElement(ethermometer, "sensors")

            values = (self.thermometer_id,)
            self.cursor.execute("SELECT sensor_id, description, thermometer_id FROM sensor WHERE thermometer_id = ?", values)
            dataSensor = self.cursor.fetchall()

            esensors.set("count", str(len(dataSensor)))

            for sensor in dataSensor:
                esensor = ET.SubElement(esensors, "sensor")
                esensor.set("index", str(sensor[0]))
                edescription = ET.SubElement(esensor, "description")
                edescription.text = str(sensor[1])

    def buildFilterValues(self, from_timestamp, to_timestamp):
        efilter = ET.SubElement(self.root, "filter")
        self.efilter_page = ET.SubElement(efilter, "page")
        self.efilter_thermometer = ET.SubElement(efilter, "thermometer")

        efilter_from = ET.SubElement(efilter, "from")
        efilter_from.text = str(from_timestamp)

        efilter_to = ET.SubElement(efilter, "to")
        efilter_to.text = str(to_timestamp)

    def buildInfoValues(self, element, dataThermometer):
        element.set("title", str(dataThermometer[0][3]))
        edescription = ET.SubElement(element, "description")
        edescription.text = str(dataThermometer[0][4])

        elocation = ET.SubElement(element, "location")
        elatitude = ET.SubElement(elocation, "latitude")
        elatitude.text = str(dataThermometer[0][5])
        elongitude = ET.SubElement(elocation, "longitude")
        elongitude.text = str(dataThermometer[0][6])

    def buildValues(self, epages, evalues, values, page):
        self.cursor.execute("SELECT count(*) \
FROM measurement m LEFT OUTER JOIN sensor s ON m.thermometer_id = s.thermometer_id \
WHERE m.thermometer_id = ? AND m.timestamp >= ? AND m.timestamp <= ?", values)
        data = self.cursor.fetchall()
        float_round_up = lambda number: int(number + 1) if int(number) != number else int(number)

        pages_limit = self.configuration.pages_limit
        values_count = int(data[0][0])
        pages_count = float_round_up(float(values_count) / int(self.configuration.page_limit))

        if page == -1:
            page = pages_count
        page -= 1

        self.efilter_page.text = str(page + 1)
        offset = (self.configuration.page_limit * page)

        values2 = (values[0], values[1], values[2], self.configuration.page_limit, offset,)
        self.buildPagesValues(epages, evalues, page, int(values2[3]), pages_limit, values_count)
        self.buildMeasurementsValues(evalues, values2)

    def buildMeasurementsValues(self, evalues, values):
        self.cursor.execute("SELECT m.thermometer_id, m.sensor_id, m.celsius, m.fahrenheit, m.humidity, m.timestamp \
FROM measurement m LEFT OUTER JOIN sensor s ON m.thermometer_id = s.thermometer_id \
WHERE m.thermometer_id = ? AND m.timestamp >= ? AND m.timestamp <= ? LIMIT ? OFFSET ?", values)
        dataMeasurement = self.cursor.fetchall()

        for measurement in dataMeasurement:
            esensor = ET.SubElement(evalues, "sensor")
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

    def buildPagesValues(self, epages, evalues, page, limit, pages_limit, values_count):
        float_round_up = lambda number: int(number + 1) if int(number) != number else int(number)

        pages_count = float_round_up(float(values_count) / int(limit))
        pages_buckets_count = float_round_up(float(pages_count) / pages_limit)

        evalues.set("count", str(values_count))
        evalues.set("pages", str(pages_count))

        pages_bucket = float_round_up(float(page + 1) / pages_limit)
        pages_from = ((pages_bucket - 1) * pages_limit) + 1
        pages_to = (pages_bucket * pages_limit)

        if pages_from != 1:
            epage = ET.SubElement(epages, "page")
            epage.set("thermometer", str(self.thermometer_index))
            epage.set("index", str(pages_from - 1))
            epage.text = "Prev"

        for page_index in range(pages_from, min(pages_to + 1, pages_count + 1)):
            epage = ET.SubElement(epages, "page")
            epage.set("thermometer", str(self.thermometer_index))
            epage.set("index", str(page_index))
            epage.text = str(page_index)

            if (page + 1) == page_index:
                epage.set("current", str("true"))

        if pages_to < pages_count:
            epage = ET.SubElement(epages, "page")
            epage.set("thermometer", str(self.thermometer_index))
            epage.set("index", str(pages_to + 1))
            epage.text = "Next"

    def isThermometerInDatabase(self, thermometer_id):
        values = (int(thermometer_id),)
        self.cursor.execute("SELECT count(*) FROM thermometer t WHERE t.thermometer_id = ?", values)
        data = self.cursor.fetchall()

        if int(data[0][0]) == 1:
            return True
        return False

    def xml(self):
        return ET.tostring(self.root, encoding="utf-8", method="xml")
