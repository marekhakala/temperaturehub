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

import os, sys
import sched, time

import re
import magic
import threading
import logging
import logging.handlers

from http.server import BaseHTTPRequestHandler, HTTPServer

from datetime import datetime, timedelta
from time import gmtime, strftime

# Import of my custom classes
sys.path.append(os.path.abspath("./classes/"))
from config_loader import *
from thermometer_client import *
from xml_builders import *
from xml_validator import *
from file_loader import *

# Configuration
APPLICATION_NAME = "HTS"
APPLICATION_VERSION = "0.0.1 alpha"

DEBUG_MODE = logging.INFO # Log mode
CONFIGURATION_FILE = "./config.xml"
NOT_FOUND_FILE = "notfound.html"

def application_motd():
    return str("Starting Temperature HUB server v " + APPLICATION_VERSION)

def init_console_logger():
    logger = logging.getLogger(APPLICATION_NAME)
    logger.setLevel(DEBUG_MODE)
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] >> %(message)s")

    # Console log
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(logFormatter)
    logger.addHandler(streamHandler)
    return logger

def get_logger():
    return logging.getLogger(APPLICATION_NAME)

def get_configuration():
    conf = ConfigLoader(CONFIGURATION_FILE)
    conf.loadFile()

    configuration = conf.getConfiguration()
    configuration.filename = CONFIGURATION_FILE

    return configuration

def load_configuration():
    # Init logger
    logger = init_console_logger()

    # Print application MOTD
    print("------------------------------------------------------------------------------------")
    logger.log(51, application_motd())
    print("------------------------------------------------------------------------------------\n")

    # Init configuration
    logger.info("Loading configuration from file: " + CONFIGURATION_FILE)

    if not os.path.exists(CONFIGURATION_FILE):
        logger.error("Configuration file " + CONFIGURATION_FILE + " not found.")
        return None

    try:
        configuration = get_configuration()
    except etree.XMLSyntaxError as error:
        if logger != None:
            logger.error("File config.xml: " + str(error))
        return None

    if configuration == None:
        return None

    configuration.initFileLogger(logger)
    logger = configuration.logger

    # Init SQLite3 database
    logger.info("Checking SQLite3 database ...")

    if not os.path.exists(configuration.database_filename):
        logger.error("SQLite3 database file " + configuration.database_filename + " not found.")
        logger.info("Creating SQLite3 database file " + configuration.database_filename + " ...")
        os.system("./init_db.py")
    else:
        logger.info("SQLite3 database file " + configuration.database_filename + ". OK")

    # Log - configuration info
    logger.info("Data sync time: " + configuration.updatetime + "s")
    logger.info("Configuration loaded")

    return configuration

def sync_data(sc, configuration):
    configuration.logger.info("Data sync from thermometers ...")

    # Data sync from thermometers
    for thermometer in configuration.thermometers:
        tc = ThermometerClient(configuration, thermometer)
        dataSchema = tc.fetchDataSchema()

        if dataSchema != None:
            data = tc.fetchData()

            if data != None:
                xmlValidator = XMLValidator(dataSchema)

                if xmlValidator.validate(data):
                    configuration.logger.info("Thermometer|" + str(tc.thermometer["hostname"])
                    + ":" + str(tc.thermometer["port"]) + "|XML validation: OK")
                    pdata = tc.parseData(data)
                    tc.saveToDatabase(pdata, tc.getThermometerId(pdata))
                else:
                    configuration.logger.error("Thermometer|" + str(tc.thermometer["hostname"])
                    + ":" + str(tc.thermometer["port"]) + "|XML validation: FAIL")

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
        configuration = get_configuration()
        configuration.logger = get_logger()

        re_assets = re.compile("[/]{1}(assets)[?]?([A-Za-z]*)[=]?([\S]*)")
        re_history = re.compile("[/]{1}(history)[?]?([A-Za-z]*)[=]?([\d]*)[&]?([A-Za-z]*)[=]?([\d]*)")

        if re_assets.match(s.path):
            params = re_assets.match(s.path).groups()
        elif re_history.match(s.path):
            params = re_history.match(s.path).groups()
        else:
            params = []

        if s.path == "/":
            s.send_response(200)
            s.send_header("Content-type", "text/xml")
            s.end_headers()

            current_state = XMLCurrentState(configuration)
            current_state.buildXML()
            s.wfile.write(b"<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
            s.wfile.write(b"<?xml-stylesheet type=\"text/xsl\" href=\"assets?filename=current_state.xsl\"?>")
            s.wfile.write(current_state.xml())
        elif re_assets.match(s.path) and len(params) > 1 and params[0] == "assets" and params[1] == "filename":
            file_path = params[2].replace("/../", "")
            file_path = file_path.replace("../", "")
            file_path = configuration.assets_path + file_path

            if os.path.exists(file_path) and os.path.isfile(file_path):
                s.send_response(200)
            else:
                s.send_response(404)
                file_path = configuration.assets_path + NOT_FOUND_FILE

            loader = FileLoader(file_path)
            mime = magic.Magic()
            mime_type = mime.from_file(file_path)
            s.send_header("Content-type", str(mime_type))

            loader.loadFile()
            content = loader.getContent()

            s.end_headers()
            s.wfile.write(content)
        elif re_history.match(s.path) and params[0] == "history":
            page = -1
            thermometer = 0

            temp_params = []
            len_params = len(params)

            if len_params > 2: temp_params.append((params[1], params[2]))
            if len_params > 4: temp_params.append((params[3], params[4]))

            for param in temp_params:
                if param[0] == "thermometer":
                    try:
                        thermometer = int(param[1])
                    except ValueError:
                        thermometer = 0

                elif param[0] == "page":
                    try:
                        page = int(param[1])
                    except ValueError:
                        page = -1

            if thermometer < 0: thermometer = 0

            history = XMLHistory(configuration)
            history.buildXML(thermometer, page)

            s.send_response(200)
            s.send_header("Content-type", "text/xml")
            s.end_headers()

            s.wfile.write(b"<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
            s.wfile.write(b"<?xml-stylesheet type=\"text/xsl\" href=\"assets?filename=history.xsl\"?>")
            s.wfile.write(history.xml())
        else:
            s.send_response(404)
            file_path = configuration.assets_path + NOT_FOUND_FILE

            loader = FileLoader(file_path)
            mime = magic.Magic()
            mime_type = mime.from_file(file_path)
            s.send_header("Content-type", str(mime_type))

            loader.loadFile()
            content = loader.getContent()

            s.end_headers()
            s.wfile.write(content)

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
