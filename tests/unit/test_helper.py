import pytest
from lxml import etree

from scrapli.exceptions import TransportPluginError
from scrapli_netconf.helper import _find_netconf_transport_plugin, remove_namespaces
from scrapli_netconf.transport import cssh2
from scrapli_netconf.transport.cssh2 import NetconfSSH2Transport
from scrapli_netconf.transport.miko import NetconfMikoTransport


def test_remove_namespaces():
    xml_with_namespace = """<?xml version="1.0"?>
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
</rpc-reply>"""

    xml_without_namespace = """<rpc-reply message-id="101">
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
</rpc-reply>"""
    etree_with_namespace = etree.fromstring(xml_with_namespace)
    etree_without_namespace = remove_namespaces(tree=etree_with_namespace)
    assert etree.tostring(etree_without_namespace).decode() == xml_without_namespace


def test___find_transport_plugin_module_not_found():
    with pytest.raises(ModuleNotFoundError) as exc:
        _find_netconf_transport_plugin(transport="blah")
    assert (
        str(exc.value)
        == "\n***** Module 'scrapli_blah' not found! ************************************************\nTo resolve this issue, ensure you are referencing a valid transport plugin. Transport plugins should be named similar to `scrapli_paramiko` or `scrapli_ssh2`, and can be selected by passing simply `paramiko` or `ssh2` into the scrapli driver. You can install most plugins with pip: `pip install scrapli-ssh2` for example.\n***** Module 'scrapli_blah' not found! ************************************************"
    )


def test___find_transport_plugin_module_failed_to_load(monkeypatch):
    monkeypatch.setattr(cssh2, "NetconfSSH2Transport", None)
    with pytest.raises(TransportPluginError) as exc:
        _find_netconf_transport_plugin(transport="ssh2")
    assert str(exc.value) == "Failed to load transport plugin `ssh2` transport class"


@pytest.mark.parametrize(
    "transport_plugin_data",
    [
        (
            "ssh2",
            NetconfSSH2Transport,
        ),
        (
            "paramiko",
            NetconfMikoTransport,
        ),
    ],
    ids=["ssh2", "paramiko"],
)
def test__find_transport_plugin_module(transport_plugin_data):
    transport_class_friendly_name = transport_plugin_data[0]
    expected_transport_class = transport_plugin_data[1]
    transport_class = _find_netconf_transport_plugin(transport=transport_class_friendly_name)
    assert transport_class == expected_transport_class
