"""scrapli_netconf.constants"""

from enum import Enum


class XmlParserVersion(Enum):
    COMPRESSED_PARSER = "flat"
    STANDARD_PARSER = "standard"


class NetconfVersion(Enum):
    UNKNOWN = "unknown"
    VERSION_1_0 = "1.0"
    VERSION_1_1 = "1.1"


class NetconfClientCapabilities(Enum):
    UNKNOWN = "unknown"
    CAPABILITIES_1_0 = """
<?xml version="1.0" encoding="utf-8"?>
    <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <capabilities>
            <capability>urn:ietf:params:netconf:base:1.0</capability>
        </capabilities>
</hello>]]>]]>"""
    CAPABILITIES_1_1 = """
<?xml version="1.0" encoding="utf-8"?>
    <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <capabilities>
            <capability>urn:ietf:params:netconf:base:1.1</capability>
        </capabilities>
</hello>]]>]]>"""
