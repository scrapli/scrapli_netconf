from pathlib import Path

import scrapli_netconf

from ..helper import (
    cisco_iosxe_replace_config_data,
    cisco_iosxr_replace_config_data,
    juniper_junos_replace_config_data,
)
from .inputs_and_outputs import cisco_iosxe_1_0 as cisco_iosxe_1_0_inputs_outputs
from .inputs_and_outputs import cisco_iosxe_1_1 as cisco_iosxe_1_1_inputs_outputs
from .inputs_and_outputs import cisco_iosxr_1_1 as cisco_iosxr_1_1_inputs_outputs
from .inputs_and_outputs import juniper_junos_1_0 as juniper_junos_1_0_inputs_outputs

TEST_DATA_PATH = f"{Path(scrapli_netconf.__file__).parents[1]}/tests/test_data"

FUNCTIONAL_USERNAME = "vrnetlab"
FUNCTIONAL_PASSWORD = "VR-netlab9"
PRIVATE_KEY = f"{TEST_DATA_PATH}/files/vrnetlab_key"
INVALID_PRIVATE_KEY = f"{TEST_DATA_PATH}/files/invalid_key"

DEVICES = {
    "cisco_iosxe_1_0": {
        "auth_username": FUNCTIONAL_USERNAME,
        "auth_password": FUNCTIONAL_PASSWORD,
        "auth_strict_key": False,
        "host": "172.18.0.11",
        "port": 22,
        "strip_namespaces": False,
    },
    "cisco_iosxe_1_1": {
        "auth_username": FUNCTIONAL_USERNAME,
        "auth_password": FUNCTIONAL_PASSWORD,
        "auth_strict_key": False,
        "host": "172.18.0.11",
        "port": 830,
        "strip_namespaces": False,
    },
    "cisco_iosxr_1_1": {
        "auth_username": FUNCTIONAL_USERNAME,
        "auth_password": FUNCTIONAL_PASSWORD,
        "auth_strict_key": False,
        "host": "172.18.0.13",
        "port": 830,
        "strip_namespaces": False,
    },
    "juniper_junos_1_0": {
        "auth_username": FUNCTIONAL_USERNAME,
        "auth_password": FUNCTIONAL_PASSWORD,
        "auth_strict_key": False,
        "host": "172.18.0.15",
        "port": 22,
        "strip_namespaces": False,
        # commits takes a long time and transport gets nothing during this time
        "timeout_transport": 15,
    },
}

CONFIG_REPLACER = {
    "cisco_iosxe_1_0": cisco_iosxe_replace_config_data,
    "cisco_iosxe_1_1": cisco_iosxe_replace_config_data,
    "cisco_iosxr_1_1": cisco_iosxr_replace_config_data,
    "juniper_junos_1_0": juniper_junos_replace_config_data,
}


INPUTS_OUTPUTS = {
    "cisco_iosxe_1_0": cisco_iosxe_1_0_inputs_outputs,
    "cisco_iosxe_1_1": cisco_iosxe_1_1_inputs_outputs,
    "cisco_iosxr_1_1": cisco_iosxr_1_1_inputs_outputs,
    "juniper_junos_1_0": juniper_junos_1_0_inputs_outputs,
}
