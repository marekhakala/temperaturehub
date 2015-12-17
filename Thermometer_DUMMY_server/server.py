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
from file_loader import *

# Configuration
APPLICATION_NAME = "HTS"
APPLICATION_VERSION = "0.0.1 alpha"

DEBUG_MODE = logging.INFO # Log mode
CONFIGURATION_FILE = "./config.xml"

def application_motd():
    return str("Starting Thermometer DUMMY server v " + APPLICATION_VERSION)

def init_logger():
    logger = logging.getLogger(APPLICATION_NAME)
    logger.setLevel(DEBUG_MODE)
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] >> %(message)s")

    configuration = get_configuration()

    # Rotating log file (Max size 5 MB)
    fileHandler = logging.handlers.RotatingFileHandler(configuration.log_filename, maxBytes=(1048576*5), backupCount=7)
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

    return configuration

def load_configuration():
    # Init logger
    logger = init_logger()

    # Print application MOTD
    print("-------------------------------------------------------------------------------------")
    logger.log(51, application_motd())
    print("-------------------------------------------------------------------------------------\n")

    # Init configuration
    logger.info("Loading configuration from file: " + CONFIGURATION_FILE)

    if not os.path.exists(CONFIGURATION_FILE):
        logger.error("Configuration file " + CONFIGURATION_FILE + " not found.")
        return None

    configuration = get_configuration()
    configuration.logger = logger

    # Log - configuration info
    logger.info("Configuration loaded")

    return configuration

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

        if s.path == "/client.xsd":
            loader = FileLoader("./client.xsd")
        else:
            loader = FileLoader("./client.xml")

        loader.loadFile()
        content = loader.getContent()
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

    # Start HTTP server
    try:
        httpd = HTTPServer((configuration.hostname, int(configuration.port)),
        HandlerConfigurationWrapper(configuration).getHandler())
        configuration.logger.info("Starting HTTP server on \
" + str(configuration.hostname) + ":" + str(configuration.port))
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    configuration.logger.info("Stopping HTTP server")
