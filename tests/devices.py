import os
from pathlib import Path

from helper import (
    cisco_iosxe_replace_config_data,
    cisco_iosxr_replace_config_data,
    juniper_junos_replace_config_data,
)

import scrapli_netconf

TEST_DATA_PATH = f"{Path(scrapli_netconf.__file__).parents[1]}/tests/test_data"

VRNETLAB_MODE = bool(os.environ.get("SCRAPLI_VRNETLAB", False))
USERNAME = "boxen" if not VRNETLAB_MODE else "vrnetlab"
PASSWORD = "b0x3N-b0x3N" if not VRNETLAB_MODE else "VR-netlab9"
PRIVATE_KEY = f"{TEST_DATA_PATH}/files/vrnetlab_key"
INVALID_PRIVATE_KEY = f"{TEST_DATA_PATH}/files/invalid_key"

DEVICES = {
    "cisco_iosxe_1_0": {
        "auth_username": USERNAME,
        "auth_password": PASSWORD,
        "auth_strict_key": False,
        "host": "localhost" if not VRNETLAB_MODE else "172.18.0.11",
        "port": 21022 if not VRNETLAB_MODE else 22,
        "strip_namespaces": False,
    },
    "cisco_iosxe_1_1": {
        "auth_username": USERNAME,
        "auth_password": PASSWORD,
        "auth_strict_key": False,
        "host": "localhost" if not VRNETLAB_MODE else "172.18.0.11",
        "port": 21830 if not VRNETLAB_MODE else 830,
        "strip_namespaces": False,
    },
    "cisco_iosxr_1_1": {
        "auth_username": USERNAME,
        "auth_password": PASSWORD,
        "auth_strict_key": False,
        "host": "localhost" if not VRNETLAB_MODE else "172.18.0.13",
        "port": 23830 if not VRNETLAB_MODE else 830,
        "strip_namespaces": False,
        "timeout_transport": 30,
    },
    "juniper_junos_1_0": {
        "auth_username": USERNAME,
        "auth_password": PASSWORD,
        "auth_strict_key": False,
        "host": "localhost" if not VRNETLAB_MODE else "172.18.0.15",
        "port": 25022 if not VRNETLAB_MODE else 22,
        "strip_namespaces": False,
        # commits takes a long time and transport gets nothing during this time
        "timeout_transport": 30,
    },
}

CONFIG_REPLACER = {
    "cisco_iosxe_1_0": cisco_iosxe_replace_config_data,
    "cisco_iosxe_1_1": cisco_iosxe_replace_config_data,
    "cisco_iosxr_1_1": cisco_iosxr_replace_config_data,
    "juniper_junos_1_0": juniper_junos_replace_config_data,
}
