#!/usr/bin/env python3
#
# (C) Copyright 2015 by Marek Hakala <hakala.marek@gmail.com>
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

connect = sqlite3.connect('./measurement.db')
cursor = connect.cursor()

cursor.execute("CREATE TABLE thermometer (id INTEGER PRIMARY KEY, thermometer_id INTEGER, hostname TEXT, port TEXT, title TEXT, description TEXT, latitude TEXT, longitude TEXT)")
cursor.execute("CREATE TABLE sensor (id INTEGER PRIMARY KEY, sensor_id INTEGER, description TEXT, thermometer_id INTEGER, FOREIGN KEY (thermometer_id) REFERENCES thermometer(id))")
cursor.execute("CREATE TABLE measurement (id INTEGER PRIMARY KEY, thermometer_id INTEGER, sensor_id INTEGER, celsius TEXT, fahrenheit TEXT, humidity TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (thermometer_id) REFERENCES thermometer(id), FOREIGN KEY (sensor_id) REFERENCES sensor(id))")

connect.commit()
connect.close()
