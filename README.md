# TemperatureHUB 1.0.0 (XML API)

![TemperatureHUB Logo](temperaturehub.png)

TemperatureHUB is Python3 application for downloading temperature / humidity values
from remote weather stations that are located on the local network.

Application contain server part and client example part. Server application provide
HTTP server with XML data that can be displayed in web browser by XSLT transformation.

[Screenshots](Screenshots/)

## API

* `/` - List of weather stations and current values
* `/history` - List of measured values

# Setup

Clone this repository and after install required packages for your operation system.

`git clone https://github.com/marekhakala/temperaturehub.git`

## Requirements

* Python 3.5+
* Python 3 Lxml 3.5.0+
* Python 3 Magic
* SQLite3

## Installation

### Mac OS X / macOS

* `brew install libxml2`
* `brew install imagemagick`
* `brew install libmagic`
* `brew install python3`

* `pip3 install lxml`
* `pip3 install magic`

### Linux - Debian/Ubuntu

* `aptitude install python3`
* `aptitude install python3-pip`
* `aptitude install libxml2-dev libxslt1-dev python-dev`
* `aptitude install python3-lxml`
* `aptitude install python3-magic`

## Configuration (config.xml)

`<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="config.xsd">
  <server>
    <listen>0.0.0.0</listen>
    <port>8000</port>
  </server>
  <databasefile>./measurement.db</databasefile>
  <logfile>./hts.log</logfile>
  <assetspath>./assets/</assetspath>
  <historydays>5</historydays>
  <updatetime>10</updatetime>
  <pagelimit>50</pagelimit>
  <pageslimit>10</pageslimit>
  <thermometers>
    <thermometer>
      <hostname>127.0.0.1</hostname>
      <port>9000</port>
    </thermometer>
    <thermometer>
      <hostname>127.0.0.1</hostname>
      <port>9001</port>
    </thermometer>
    <!-- Add another thermometer -->
  </thermometers>
</config>`

## Run

* `python3 ./server.py`

# License - Apache License, Version 2.0

```
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
```
