from pathlib import Path

import pytest
from devices import CONFIG_REPLACER, DEVICES
from helper import xmldiffs

import scrapli_netconf

TEST_DATA_PATH = f"{Path(scrapli_netconf.__file__).parents[1]}/tests/test_data"


@pytest.fixture(scope="session")
def test_data_path():
    """Fixture to provide path to test data files"""
    return TEST_DATA_PATH


@pytest.fixture(scope="session")
def test_devices_dict():
    """Fixture to return test devices dict"""
    return DEVICES


@pytest.fixture(scope="session")
def config_replacer_dict():
    """Fixture to return dict of config replacer helper functions"""
    return CONFIG_REPLACER


@pytest.fixture(scope="session")
def xmldiffer():
    """Fixture to return xmldiffs function"""
    return xmldiffs


TEST_CASES = {
    "cisco_iosxe_1_0": {
        "get_filter_subtree": {
            "filter_": """
<config-format-text-cmd>
 <text-filter-spec> | include interface </text-filter-spec>
</config-format-text-cmd>""",
            "expected_config_elements": ["cli-config-data"],
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_0/get_subtree"
            ).read(),
        },
        "get_config": {
            "expected_config_elements": ["cli-config-data-block"],
            "expected_output": open(f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_0/get_config").read(),
        },
        "get_config_filtered_single": {
            "filter_": """
<config-format-text-cmd>
    <text-filter-spec>
        interface GigabitEthernet1
    </text-filter-spec>
</config-format-text-cmd>""",
            "expected_config_elements": ["cli-config-data"],
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_0/get_config_filtered_single"
            ).read(),
        },
        "edit_config": {
            "config": """
<config>
<cli-config-data>
<cmd>interface GigabitEthernet2</cmd>
<cmd>description scrapli was here!</cmd>
</cli-config-data>
</config>""",
            "remove_config": """
<config>
<cli-config-data>
<cmd>interface GigabitEthernet2</cmd>
<cmd>no description</cmd>
</cli-config-data>
</config>""",
            "validate_config_filter": """
<config-format-text-cmd>
 <text-filter-spec>
   interface GigabitEthernet2
 </text-filter-spec>
</config-format-text-cmd>
""",
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_0/edit_config"
            ).read(),
        },
        "rpc": {
            "filter_": """
<get><filter type="subtree"><config-format-text-cmd>
    <text-filter-spec> | include interface </text-filter-spec>
</config-format-text-cmd></filter></get>""",
            "expected_config_elements": ["cli-config-data"],
            "expected_output": open(f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_0/rpc").read(),
        },
    },
    "cisco_iosxe_1_1": {
        "get_filter_subtree": {
            "filter_": """
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name>
      GigabitEthernet1
    </name>
  </interface>
</interfaces>""",
            "expected_config_elements": ["interfaces"],
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_1/get_subtree"
            ).read(),
        },
        "get_filter_xpath": {
            "filter_": "//interfaces-state/interface[2]/name",
            "expected_config_elements": ["interfaces-state"],
            "expected_output": open(f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_1/get_xpath").read(),
        },
        "get_config": {
            "expected_config_elements": [
                "native",
                "licensing",
                "netconf-yang",
                "acl",
                "interfaces",
                "network-instances",
                "nacm",
                "routing",
            ],
            "expected_output": open(f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_1/get_config").read(),
        },
        "get_config_filtered_single": {
            "filter_": """
<interfaces xmlns="http://openconfig.net/yang/interfaces">
    <interface>
        <name>GigabitEthernet1</name>
    </interface>
</interfaces>""",
            "expected_config_elements": ["interfaces"],
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_1/get_config_filtered_single"
            ).read(),
        },
        "get_config_filtered_multi": {
            "filter_": """
<interfaces xmlns="http://openconfig.net/yang/interfaces">
    <interface>
        <name>GigabitEthernet1</name>
    </interface>
</interfaces>
<netconf-yang xmlns="http://cisco.com/yang/cisco-self-mgmt">
</netconf-yang>""",
            "expected_config_elements": ["interfaces", "netconf-yang"],
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_1/get_config_filtered_multi"
            ).read(),
        },
        "get_config_filtered_xpath": {
            "filter_": "/interfaces/interface[1]/name",
            "expected_config_elements": ["interfaces"],
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_1/get_config_filtered_xpath"
            ).read(),
        },
        "edit_config": {
            "config": """
<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>GigabitEthernet1</name>
            <description>scrapli was here!</description>
        </interface>
    </interfaces>
</config>""",
            "remove_config": """
<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>GigabitEthernet1</name>
            <description operation="delete"></description>
        </interface>
    </interfaces>
</config>""",
            "validate_config_filter": """
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name>
      GigabitEthernet1
    </name>
  </interface>
</interfaces>
""",
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_1/edit_config"
            ).read(),
        },
        "rpc": {
            "filter_": """
<get><filter type="subtree"><interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name>
      GigabitEthernet1
    </name>
  </interface>
</interfaces></filter></get>""",
            "expected_config_elements": ["interfaces"],
            "expected_output": open(f"{TEST_DATA_PATH}/expected/cisco_iosxe_1_1/rpc").read(),
        },
    },
    "cisco_iosxr_1_1": {
        "get_filter_subtree": {
            "filter_": """
<components xmlns="http://openconfig.net/yang/platform">
    <component>
        <name>
          0/0-Virtual-Motherboard
        </name>
        <state>
        </state>
    </component>
</components>""",
            "expected_config_elements": ["components"],
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/cisco_iosxr_1_1/get_subtree"
            ).read(),
        },
        "get_config": {
            "expected_config_elements": [
                "ssh",
                "xr-xml",
                "aaa",
                "call-home",
                "netconf-yang",
                "ip",
                "interface-configurations",
                "SNMP-COMMUNITY-MIB",
                "SNMP-NOTIFICATION-MIB",
                "SNMP-TARGET-MIB",
                "SNMP-USER-BASED-SM-MIB",
                "SNMP-VIEW-BASED-ACM-MIB",
                "SNMPv2-MIB",
                "fpd",
                "sdr-config",
                "private-sdr",
                "service",
                "interfaces",
                "lacp",
            ],
            "expected_output": open(f"{TEST_DATA_PATH}/expected/cisco_iosxr_1_1/get_config").read(),
        },
        "get_config_filtered_single": {
            "filter_": """
<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
    <interface-configuration>
        <active>act</active>
        <interface-name>MgmtEth0/RP0/CPU0/0</interface-name>
    </interface-configuration>
</interface-configurations>""",
            "expected_config_elements": ["interface-configurations"],
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/cisco_iosxr_1_1/get_config_filtered_single"
            ).read(),
        },
        "get_config_filtered_multi": {
            "filter_": """
<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
    <interface-configuration>
        <active>act</active>
        <interface-name>MgmtEth0/RP0/CPU0/0</interface-name>
    </interface-configuration>
</interface-configurations>
<ssh xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-crypto-ssh-cfg">
    <server>
        <v2>
        </v2>
    </server>
</ssh>""",
            "expected_config_elements": ["interface-configurations", "ssh"],
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/cisco_iosxr_1_1/get_config_filtered_multi"
            ).read(),
        },
        "edit_config": {
            "config": """
<config>
  <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
    <interface-configuration>
      <active>act</active>
      <interface-name>GigabitEthernet0/0/0/0</interface-name>
      <description>scrapli was here</description>
      <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
        <addresses>
          <primary>
            <address>10.10.0.1</address>
            <netmask>255.255.255.0</netmask>
          </primary>
        </addresses>
      </ipv4-network>
    </interface-configuration>
  </interface-configurations>
</config>""",
            "remove_config": """
<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
    <interface-configuration>
      <active>act</active>
      <interface-name>GigabitEthernet0/0/0/0</interface-name>
      <description xc:operation="delete"></description>
      <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
        <addresses>
          <primary xc:operation="delete">
          </primary>
        </addresses>
      </ipv4-network>
    </interface-configuration>
  </interface-configurations>
</config>""",
            "validate_config_filter": """
<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
  <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/0</interface-name>
    <description></description>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
      <addresses>
        <primary>
          <address></address>
          <netmask></netmask>
        </primary>
      </addresses>
    </ipv4-network>
  </interface-configuration>
</interface-configurations>
""",
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/cisco_iosxr_1_1/edit_config"
            ).read(),
        },
        "rpc": {
            "filter_": """
<get><filter type="subtree">
<components xmlns="http://openconfig.net/yang/platform">
    <component>
        <name>
          0/0-Virtual-Motherboard
        </name>
        <state>
        </state>
    </component>
</components></filter></get>""",
            "expected_config_elements": ["components"],
            "expected_output": open(f"{TEST_DATA_PATH}/expected/cisco_iosxr_1_1/rpc").read(),
        },
    },
    "juniper_junos_1_0": {
        "get_config": {
            "expected_config_elements": ["configuration"],
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/juniper_junos_1_0/get_config"
            ).read(),
        },
        "get_config_filtered_single": {
            "filter_": """
<configuration>
    <interfaces>
    </interfaces>
    <system>
        <services>
            <ssh>
            </ssh>
        </services>
    </system>    
</configuration>""",
            "expected_config_elements": ["configuration"],
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/juniper_junos_1_0/get_config_filtered_single"
            ).read(),
        },
        "edit_config": {
            "config": """
<config>
  <configuration>
    <interfaces>
        <interface>
            <name>ge-0/0/0</name>
            <description>scrapli was here</description>
        </interface>
    </interfaces>
  </configuration>
</config>""",
            "remove_config": """
<config>
  <configuration>
    <interfaces>
        <interface>
            <name>ge-0/0/0</name>
            <description operation="delete"></description>
        </interface>
    </interfaces>
  </configuration>
</config>""",
            "validate_config_filter": """
<configuration>
    <interfaces>
    </interfaces>
</configuration>
""",
            "expected_output": open(
                f"{TEST_DATA_PATH}/expected/juniper_junos_1_0/edit_config"
            ).read(),
        },
        "rpc": {
            "filter_": "<get-zones-information><terse/></get-zones-information>",
            "expected_config_elements": [],
            "expected_output": open(f"{TEST_DATA_PATH}/expected/juniper_junos_1_0/rpc").read(),
        },
    },
}


@pytest.fixture(scope="session")
def test_cases():
    """Fixture to return test cases shared across functional and integration tests"""
    return TEST_CASES
