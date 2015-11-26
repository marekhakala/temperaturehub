import http.client
import xml.etree.ElementTree as ET

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
                 + str(self.temperature["port"]) + ": OK")
                self.parseData(response.read().decode())

            connection.close();

        except Exception as e:
            print ("- Temperature|" + str(self.temperature["hostname"])
            + str(self.temperature["port"]) + ": " + str(e))

    def parseData(self, data):
        root = ET.fromstring(data)
        print (str(dom.text))
