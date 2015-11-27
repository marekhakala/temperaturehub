#!/usr/local/Cellar/python3/3.5.0/bin/python3

import sqlite3

connect = sqlite3.connect('./measurement.db')
cursor = connect.cursor()

cursor.execute("CREATE TABLE temperature (id INTEGER PRIMARY KEY, temperature_id INTEGER, hostname TEXT, port TEXT, title TEXT, description TEXT, latitude TEXT, longitude TEXT)")
cursor.execute("CREATE TABLE sensor (id INTEGER PRIMARY KEY, sensor_id INTEGER, description TEXT, temperature_id INTEGER, FOREIGN KEY (temperature_id) REFERENCES temperature(id))")
cursor.execute("CREATE TABLE measurement (id INTEGER PRIMARY KEY, temperature_id INTEGER, sensor_id INTEGER, celsius TEXT, fahrenheit TEXT, humidity TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (temperature_id) REFERENCES temperature(id), FOREIGN KEY (sensor_id) REFERENCES sensor(id))")

connect.commit()
connect.close()
