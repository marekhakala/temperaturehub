
class XMLLoader(object):
    def __init__(self, filename):
        self.filename = filename

    def loadFile(self):
        self.file = open(self.filename, 'r')
        self.fileContent = str(self.file.read())

    def closeFile(self):
        self.file.close()

    def getContent(self):
        return str(self.fileContent)
