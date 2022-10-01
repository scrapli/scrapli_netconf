import os
from pathlib import Path
from typing import Tuple

from helper import (
    cisco_iosxe_replace_config_data,
    cisco_iosxr_replace_config_data,
    juniper_junos_replace_config_data,
)

import scrapli_netconf

TEST_DATA_PATH = f"{Path(scrapli_netconf.__file__).parents[1]}/tests/test_data"

PRIVATE_KEY = f"{TEST_DATA_PATH}/files/vrnetlab_key"
INVALID_PRIVATE_KEY = f"{TEST_DATA_PATH}/files/invalid_key"


def get_env_or_default(key: str, default: str) -> str:
    return os.getenv(key, default)


def get_functional_host_ip_port_linux_or_remote(platform: str) -> Tuple[str, int]:
    plats = {
        "cisco_iosxe_1_0": ("172.20.20.11", 22),
        "cisco_iosxe_1_1": ("172.20.20.11", 830),
        "cisco_iosxr_1_1": ("172.20.20.12", 830),
        "juniper_junos_1_0": ("172.20.20.15", 22),
    }

    return get_env_or_default(f"SCRAPLI_{platform.upper()}_HOST", plats[platform][0]), int(
        get_env_or_default(f"SCRAPLI_{platform.upper()}_PORT", plats[platform][1])
    )


def get_functional_host_ip_port(platform: str) -> Tuple[str, int]:
    if not get_env_or_default("SCRAPLI_HOST_FWD", ""):
        return get_functional_host_ip_port_linux_or_remote(platform)

    # otherwise we are running on darwin w/ local boxen w/ nat
    host = "localhost"

    if platform == "cisco_iosxe_1_0":
        return host, 21022
    if platform == "cisco_iosxe_1_1":
        return host, 21830
    if platform == "cisco_iosxr_1_1":
        return host, 22830
    if platform == "juniper_junos_1_0":
        return host, 25022


def get_functional_host_user_pass(platform: str) -> Tuple[str, str]:
    user = "admin"
    pwd = "admin"

    if "cisco_iosxe" in platform:
        return user, pwd
    if "cisco_iosxr" in platform:
        return "clab", "clab@123"
    if "juniper_junos" in platform:
        return user, "admin@123"


DEVICES = {
    "cisco_iosxe_1_0": {
        "auth_strict_key": False,
        "strip_namespaces": False,
        "transport_options": {
            "open_cmd": [
                "-o",
                "KexAlgorithms=+diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1",
            ]
        },
    },
    "cisco_iosxe_1_1": {
        "auth_strict_key": False,
        "strip_namespaces": False,
    },
    "cisco_iosxr_1_1": {
        "auth_strict_key": False,
        "strip_namespaces": False,
        "timeout_transport": 30,
    },
    "juniper_junos_1_0": {
        "auth_strict_key": False,
        "strip_namespaces": False,
        "timeout_transport": 30,
    },
}


def render_devices():
    for platform in ("cisco_iosxe_1_0", "cisco_iosxe_1_1", "cisco_iosxr_1_1", "juniper_junos_1_0"):
        host, port = get_functional_host_ip_port(platform)
        user, pwd = get_functional_host_user_pass(platform)

        DEVICES[platform]["host"] = host
        DEVICES[platform]["port"] = port
        DEVICES[platform]["auth_username"] = user
        DEVICES[platform]["auth_password"] = pwd


render_devices()

CONFIG_REPLACER = {
    "cisco_iosxe_1_0": cisco_iosxe_replace_config_data,
    "cisco_iosxe_1_1": cisco_iosxe_replace_config_data,
    "cisco_iosxr_1_1": cisco_iosxr_replace_config_data,
    "juniper_junos_1_0": juniper_junos_replace_config_data,
}
