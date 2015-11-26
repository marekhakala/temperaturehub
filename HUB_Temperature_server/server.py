#!/usr/local/Cellar/python3/3.5.0/bin/python3

import sys
import os
import time

sys.path.append(os.path.abspath("./classes/"))
from config_loader import *
from temperature_client import *

if __name__ == '__main__':
    conf = ConfigLoader("./config.xml")
    conf.loadFile()
    configuration = conf.getConfiguration()

    tc = TemperatureClient(configuration.temperatures[0])
    tc.fetchData()
