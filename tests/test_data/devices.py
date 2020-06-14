from pathlib import Path

import scrapli_netconf

from ..helper import (
    cisco_iosxe_replace_config_data,
    cisco_iosxr_replace_config_data,
    juniper_junos_replace_config_data,
)
from .inputs_and_outputs import cisco_iosxe as cisco_iosxe_inputs_outputs
from .inputs_and_outputs import cisco_iosxr as cisco_iosxr_inputs_outputs
from .inputs_and_outputs import juniper_junos as juniper_junos_inputs_outputs

TEST_DATA_PATH = f"{Path(scrapli_netconf.__file__).parents[1]}/tests/test_data"

FUNCTIONAL_USERNAME = "vrnetlab"
FUNCTIONAL_PASSWORD = "VR-netlab9"
PRIVATE_KEY = f"{TEST_DATA_PATH}/files/vrnetlab_key"
INVALID_PRIVATE_KEY = f"{TEST_DATA_PATH}/files/invalid_key"

DEVICES = {
    "cisco_iosxe": {
        "auth_username": FUNCTIONAL_USERNAME,
        "auth_password": FUNCTIONAL_PASSWORD,
        "auth_strict_key": False,
        "host": "172.18.0.11",
        "port": 22,
        "strip_namespaces": False,
        "base_config": f"{TEST_DATA_PATH}/base_configs/cisco_iosxe",
    },
    "cisco_iosxr": {
        "auth_username": FUNCTIONAL_USERNAME,
        "auth_password": FUNCTIONAL_PASSWORD,
        "auth_strict_key": False,
        "host": "172.18.0.13",
        "port": 830,
        "strip_namespaces": False,
        "base_config": f"{TEST_DATA_PATH}/base_configs/cisco_iosxr",
    },
    "juniper_junos": {
        "auth_username": FUNCTIONAL_USERNAME,
        "auth_password": FUNCTIONAL_PASSWORD,
        "auth_strict_key": False,
        "host": "172.18.0.15",
        "port": 22,
        "strip_namespaces": False,
        "base_config": f"{TEST_DATA_PATH}/base_configs/juniper_junos",
    },
}

CONFIG_REPLACER = {
    "cisco_iosxe": cisco_iosxe_replace_config_data,
    "cisco_iosxr": cisco_iosxr_replace_config_data,
    "juniper_junos": juniper_junos_replace_config_data,
}


INPUTS_OUTPUTS = {
    "cisco_iosxe": cisco_iosxe_inputs_outputs,
    "cisco_iosxr": cisco_iosxr_inputs_outputs,
    "juniper_junos": juniper_junos_inputs_outputs,
}
