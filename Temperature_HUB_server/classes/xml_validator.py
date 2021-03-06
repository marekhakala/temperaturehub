#
# Copyright 2015 by Marek Hakala <hakala.marek@gmail.com>
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

import re
from lxml import etree

def remove_encoding(xml_root):
    return re.sub(r'(<\?xml version=".+" encoding=".+"\?>)\n', '', xml_root)

class XMLValidator(object):
    def __init__(self, xmlschema_root):
        self.xml_schema = etree.XMLSchema(etree.fromstring(remove_encoding(xmlschema_root)))
        self.xml_parser = etree.XMLParser(schema=self.xml_schema)

    def validate(self, xml_root):
        try:
            etree.fromstring(remove_encoding(xml_root), self.xml_parser)
            return True
        except etree.XMLSyntaxError:
            return False
