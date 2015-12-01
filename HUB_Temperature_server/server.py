#!/usr/local/Cellar/python3/3.5.0/bin/python3
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

import os, sys
import sched, time

import threading
import logging
import logging.handlers

from http.server import BaseHTTPRequestHandler, HTTPServer
from time import gmtime, strftime

# Import of my custom classes
sys.path.append(os.path.abspath("./classes/"))
from config_loader import *
from temperature_client import *
from xml_builders import *

# Configuration
APPLICATION_NAME = "HTS"
APPLICATION_VERSION = "0.0.1 alpha"

DEBUG_MODE = logging.INFO # Log mode
CONFIGURATION_FILE = "./config.xml"
DATABASE_FILE = "./measurement.db"
LOG_FILE = "./hts.log"

def application_motd():
    return str("Starting HUB Temperature server v " + APPLICATION_VERSION)

def init_logger():
    logger = logging.getLogger(APPLICATION_NAME)
    logger.setLevel(DEBUG_MODE)
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] >> %(message)s")

    # Rotating log file (Max size 5 MB)
    fileHandler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=(1048576*5), backupCount=7)
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    # Console log
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(logFormatter)
    logger.addHandler(streamHandler)
    return logger

def get_configuration():
    conf = ConfigLoader(CONFIGURATION_FILE)
    conf.loadFile()

    configuration = conf.getConfiguration()
    configuration.filename = CONFIGURATION_FILE
    configuration.database_filename = DATABASE_FILE

    return configuration

def load_configuration():
    # Init logger
    logger = init_logger()

    # Print application MOTD
    print("------------------------------------------------------------------------------------")
    logger.log(51, application_motd())
    print("------------------------------------------------------------------------------------\n")

    # Init configuration
    logger.info("Loading configuration from file: " + CONFIGURATION_FILE)

    if not os.path.exists(CONFIGURATION_FILE):
        logger.error("Configuration file " + CONFIGURATION_FILE + " not found.")
        return None

    configuration = get_configuration()
    configuration.logger = logger

    # Init SQLite3 database
    logger.info("Checking SQLite3 database ...")

    if not os.path.exists(DATABASE_FILE):
        logger.error("SQLite3 database file " + DATABASE_FILE + " not found.")
        logger.info("Creating SQLite3 database file " + DATABASE_FILE + " ...")
        os.system("./init_db.py")
    else:
        logger.info("SQLite3 database file " + DATABASE_FILE + ". OK")

    # Log - configuration info
    logger.info("Data sync time: " + configuration.updatetime + "s")
    logger.info("Configuration loaded")

    return configuration

def sync_data(sc, configuration):
    configuration.logger.info("Data sync from temperatures ...")

    # Data sync from temperatures
    for temperature in configuration.temperatures:
        tc = TemperatureClient(configuration, temperature)
        data = tc.fetchData()

        if data != None:
            tc.saveToDatabase(data, tc.getTemperatureId(data))

    # Add next run batch
    sc.enter(float(configuration.updatetime), 1, sync_data, (sc,configuration,))

class ServerHandler(BaseHTTPRequestHandler):
    def __init__(self, configuration, *args):
        self.configuration = configuration
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/xml")
        s.end_headers()

    def do_GET(s):
        s.send_response(200)
        s.send_header("Content-type", "text/xml")
        s.end_headers()

        if s.path == "/":
            current_state = XMLCurrentState(get_configuration())
            current_state.buildXML()
            s.wfile.write(b"<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
            s.wfile.write(current_state.xml())
        elif s.path == "/history":
            history = XMLHistory()
            history.buildXML()
            s.wfile.write(b"<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
            s.wfile.write(history.xml())

class HandlerConfigurationWrapper(object):
    def __init__(self, configuration):
        self.configuration = configuration

    def handler(self, *args):
        ServerHandler(self.configuration, *args)

    def getHandler(self):
        return self.handler

if __name__ == '__main__':
    # Load configuration from config.xml
    configuration = load_configuration()

    if configuration == None:
        sys.exit(1)

    #sync_data(None, configuration)

    # Start HTTP server & data sync
    try:
        httpd = HTTPServer((configuration.hostname, int(configuration.port)),
         HandlerConfigurationWrapper(configuration).getHandler())
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        configuration.logger.info("Starting HTTP server on \
" + str(configuration.hostname) + ":" + str(configuration.port))
        # Loop for data sync
        s = sched.scheduler(time.time, time.sleep)
        s.enter(float(configuration.updatetime), 1, sync_data, (s,configuration,))
        s.run()
    except KeyboardInterrupt:
        pass

    configuration.logger.info("Stopping Data synchronization")
    configuration.logger.info("Stopping HTTP server")
