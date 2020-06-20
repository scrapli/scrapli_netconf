from lxml import etree

from scrapli_netconf.helper import remove_namespaces


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
