from datetime import datetime

import pytest
from lxml import etree

from scrapli.exceptions import ScrapliCommandFailure
from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.response import NetconfResponse

RESPONSE_1_0 = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/17.3R2/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <data>
    <configuration xmlns="http://xml.juniper.net/xnm/1.1/xnm" junos:commit-seconds="1592677253" junos:commit-localtime="2020-06-20 18:20:53 UTC" junos:commit-user="vrnetlab">
      <interfaces>
        <interface>
          <name>fxp0</name>
          <unit>
            <name>0</name>
            <family>
              <inet>
                <address>
                  <name>10.0.0.15/24</name>
                </address>
              </inet>
            </family>
          </unit>
        </interface>
      </interfaces>
      <system>
        <services>
          <ssh>
            <protocol-version>v2</protocol-version>
          </ssh>
        </services>
      </system>
    </configuration>
    <database-status-information>
</database-status-information>
  </data>
</rpc-reply>
"""
RESULT_1_0 = RESPONSE_1_0
RESULT_1_0_STRIP = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/17.3R2/junos" message-id="101">
  <data>
    <configuration junos:commit-seconds="1592677253" junos:commit-localtime="2020-06-20 18:20:53 UTC" junos:commit-user="vrnetlab">
      <interfaces>
        <interface>
          <name>fxp0</name>
          <unit>
            <name>0</name>
            <family>
              <inet>
                <address>
                  <name>10.0.0.15/24</name>
                </address>
              </inet>
            </family>
          </unit>
        </interface>
      </interfaces>
      <system>
        <services>
          <ssh>
            <protocol-version>v2</protocol-version>
          </ssh>
        </services>
      </system>
    </configuration>
    <database-status-information>
</database-status-information>
  </data>
</rpc-reply>
"""
XML_ELEMENTS_1_0 = ["configuration", "database-status-information"]

RESPONSE_1_1 = """#520
<?xml version="1.0"?>
<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
 <data>
  <components xmlns="http://openconfig.net/yang/platform">
   <component>
    <name>0/0-Virtual-Motherboard</name>
    <state>
     <description>Cisco IOS-XRv 9000 Virtual LC Motherboard</description>
     <name>0/0-Virtual-Motherboard</name>
     <type xmlns:idx="http://openconfig.net/yang/platform-types">idx:MODULE</type>
     <id>65538</id>
    </state>
   </component>
  </components>
 </data>
</rpc-reply>

##"""
RESULT_1_1 = """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <data>
    <components xmlns="http://openconfig.net/yang/platform">
      <component>
        <name>0/0-Virtual-Motherboard</name>
        <state>
          <description>Cisco IOS-XRv 9000 Virtual LC Motherboard</description>
          <name>0/0-Virtual-Motherboard</name>
          <type xmlns:idx="http://openconfig.net/yang/platform-types">idx:MODULE</type>
          <id>65538</id>
        </state>
      </component>
    </components>
  </data>
</rpc-reply>
"""
RESULT_1_1_STRIP = """<rpc-reply message-id="101">
  <data>
    <components>
      <component>
        <name>0/0-Virtual-Motherboard</name>
        <state>
          <description>Cisco IOS-XRv 9000 Virtual LC Motherboard</description>
          <name>0/0-Virtual-Motherboard</name>
          <type>idx:MODULE</type>
          <id>65538</id>
        </state>
      </component>
    </components>
  </data>
</rpc-reply>
"""
XML_ELEMENTS_1_1 = ["components"]


def test_response_init_exception():
    netconf_version = "blah"
    channel_input = "<something/>"
    xml_input = etree.fromstring(text=channel_input)
    with pytest.raises(ValueError) as exc:
        NetconfResponse(
            host="localhost",
            channel_input=channel_input,
            xml_input=xml_input,
            netconf_version=netconf_version,
            failed_when_contains=[b"<rpc-error>"],
        )
    assert str(exc.value) == "`netconf_version` should be one of 1.0|1.1, got `blah`"


@pytest.mark.parametrize(
    "response_setup",
    [
        (NetconfVersion.VERSION_1_0, "<something/>"),
        (NetconfVersion.VERSION_1_1, "<something/>"),
    ],
    ids=["1.0", "1.1"],
)
def test_response_init(response_setup):
    netconf_version = response_setup[0]
    channel_input = response_setup[1]
    xml_input = etree.fromstring(text=channel_input)
    response = NetconfResponse(
        host="localhost",
        channel_input=channel_input,
        xml_input=xml_input,
        netconf_version=netconf_version,
        failed_when_contains=[b"<rpc-error>"],
    )
    response_start_time = str(datetime.now())[:-7]
    assert response.host == "localhost"
    assert response.channel_input == "<something/>"
    assert response.xml_input == xml_input
    assert str(response.start_time)[:-7] == response_start_time
    assert response.failed is True
    assert bool(response) is True
    assert repr(response) == "Response <Success: False>"
    assert str(response) == "Response <Success: False>"
    assert response.failed_when_contains == [b"<rpc-error>"]
    with pytest.raises(ScrapliCommandFailure):
        response.raise_for_status()


@pytest.mark.parametrize(
    "response_setup",
    [
        (
            NetconfVersion.VERSION_1_0,
            False,
            "<something/>",
            RESPONSE_1_0,
            RESULT_1_0,
            XML_ELEMENTS_1_0,
        ),
        (
            NetconfVersion.VERSION_1_1,
            False,
            "<something/>",
            RESPONSE_1_1,
            RESULT_1_1,
            XML_ELEMENTS_1_1,
        ),
        (
            NetconfVersion.VERSION_1_0,
            True,
            "<something/>",
            RESPONSE_1_0,
            RESULT_1_0_STRIP,
            XML_ELEMENTS_1_0,
        ),
        (
            NetconfVersion.VERSION_1_1,
            True,
            "<something/>",
            RESPONSE_1_1,
            RESULT_1_1_STRIP,
            XML_ELEMENTS_1_1,
        ),
    ],
    ids=["1.0", "1.1", "1.0_strip_namespace", "1.1_strip_namespace"],
)
def test_record_response(response_setup):
    netconf_version = response_setup[0]
    strip_namespaces = response_setup[1]
    channel_input = response_setup[2]
    result = response_setup[3]
    final_result = response_setup[4]
    xml_elements = response_setup[5]
    xml_input = etree.fromstring(text=channel_input)
    response_end_time = str(datetime.now())[:-7]
    response = NetconfResponse(
        host="localhost",
        channel_input=channel_input,
        xml_input=xml_input,
        netconf_version=netconf_version,
        failed_when_contains=[b"<rpc-error>"],
        strip_namespaces=strip_namespaces,
    )
    response._record_response(result=result.encode())
    assert str(response.finish_time)[:-7] == response_end_time
    assert response.result == final_result
    assert response.failed is False
    assert list(response.get_xml_elements().keys()) == xml_elements


@pytest.mark.parametrize(
    "method_to_test",
    ["textfsm", "genie"],
    ids=["textfsm", "genie"],
)
def test_response_not_implemented_exceptions(method_to_test):
    channel_input = "<something/>"
    xml_input = etree.fromstring(text=channel_input)
    response = NetconfResponse(
        host="localhost",
        channel_input=channel_input,
        xml_input=xml_input,
        netconf_version=NetconfVersion.VERSION_1_0,
        failed_when_contains=[b"<rpc-error>"],
    )
    method = getattr(response, f"{method_to_test}_parse_output")
    with pytest.raises(NotImplementedError) as exc:
        method()
    assert str(exc.value) == f"No {method_to_test} parsing for netconf output!"
