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
import logging
import logging.handlers
from time import gmtime, strftime

# Import of my custom classes
sys.path.append(os.path.abspath("./classes/"))
from config_loader import *
from temperature_client import *

# Configuration
APPLICATION_NAME = "HTS"
DEBUG_MODE = logging.DEBUG # Logging mode
CONFIGURATION_FILE = "./config.xml"
DATABASE_FILE = "./measurement.db"
LOG_FILE = "./hts.log"

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
UPDATETIME = 10

def application_motd():
    return "----------------------------------------------------------------------\n\
" + get_timestamp_mark() + " >> Starting HUB Temperature server v 0.0.1 alpha\n\
----------------------------------------------------------------------\n"

def get_timestamp_mark():
    return strftime(TIMESTAMP_FORMAT, gmtime())

def load_configuration():
    conf = ConfigLoader(CONFIGURATION_FILE)
    print(get_timestamp_mark() + " >> Loading configuration from file: " + CONFIGURATION_FILE)

    # Init configuration
    conf.loadFile()
    configuration = conf.getConfiguration()

    configuration.filename = CONFIGURATION_FILE
    configuration.database_filename = DATABASE_FILE
    configuration.timestamp_format = TIMESTAMP_FORMAT

    # Init logger
    configuration.logger = logging.getLogger(APPLICATION_NAME)
    configuration.logger.setLevel(DEBUG_MODE)
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] >> %(message)s")

    # Rotating log file (Max size 5 MB)
    fileHandler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=(1048576*5), backupCount=7)
    fileHandler.setFormatter(logFormatter)
    configuration.logger.addHandler(fileHandler)

    # Console log
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(logFormatter)
    configuration.logger.addHandler(streamHandler)

    # Log - configuration info
    configuration.logger.info("SQLite3 database file: " + configuration.database_filename)
    configuration.logger.info("Data sync time: " + configuration.updatetime + "s")
    configuration.logger.info("Configuration loaded")

    return configuration

def sync_data(sc, configuration):
    configuration.logger.info("Data sync from temperatures...")

    # Data sync from temperatures
    for temperature in configuration.temperatures:
        tc = TemperatureClient(configuration, temperature)
        data = tc.fetchData()

        if data != None:
            tc.saveToDatabase(data, tc.getTemperatureId(data))

    # Add next run batch
    sc.enter(float(configuration.updatetime), 1, sync_data, (sc,configuration,))

if __name__ == '__main__':
    print(application_motd())
    # Load configuration from temperatures
    configuration = load_configuration()
    #sync_data(None, configuration)

    # Loop for data sync
    s = sched.scheduler(time.time, time.sleep)
    s.enter(float(configuration.updatetime), 1, sync_data, (s,configuration,))
    s.run()
