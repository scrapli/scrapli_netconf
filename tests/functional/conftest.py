import time

import pytest

from scrapli_netconf.driver.async_driver import AsyncNetconfDriver
from scrapli_netconf.driver.sync_driver import NetconfDriver

NETCONF_1_0_DEVICE_TYPES = ["cisco_iosxe_1_0", "juniper_junos_1_0"]
NETCONF_1_1_DEVICE_TYPES = ["cisco_iosxe_1_1", "cisco_iosxr_1_1"]
NETCONF_ALL_VERSIONS_DEVICE_TYPES = NETCONF_1_0_DEVICE_TYPES + NETCONF_1_1_DEVICE_TYPES


@pytest.fixture(scope="session")
def real_valid_ssh_key_path(test_data_path):
    return f"{test_data_path}/files/vrnetlab_key"


@pytest.fixture(scope="session", params=(True, False), ids=("compressed", "uncompressed"))
def use_compressed_parser(request):
    yield request.param


@pytest.fixture(
    scope="session",
    params=NETCONF_1_0_DEVICE_TYPES,
)
def device_type_1_0(request):
    yield request.param


@pytest.fixture(
    scope="session",
    params=NETCONF_1_1_DEVICE_TYPES,
)
def device_type_1_1(request):
    yield request.param


@pytest.fixture(
    scope="session",
    params=NETCONF_ALL_VERSIONS_DEVICE_TYPES,
)
def device_type(request):
    yield request.param


@pytest.fixture(scope="class", params=["system", "ssh2", "paramiko"])
def transport(request):
    yield request.param


@pytest.fixture(scope="session", params=["password"])
def auth_type(request):
    yield request.param


@pytest.fixture(scope="function")
def sync_conn_1_0(
    test_devices_dict, real_valid_ssh_key_path, device_type_1_0, auth_type, transport
):
    device = test_devices_dict[device_type_1_0].copy()
    if auth_type == "key":
        device.pop("auth_password")
        device["auth_private_key"] = real_valid_ssh_key_path
    conn = NetconfDriver(**device, transport=transport)
    yield conn, device_type_1_0
    if conn.isalive():
        conn.close()
        # slow down connections since the lab vms can be slow sometimes
        time.sleep(1)

        if "cisco_iosxr" in device_type_1_0:
            # doubly true for xr vm!
            time.sleep(2)


@pytest.fixture(scope="function")
async def async_conn_1_0(test_devices_dict, real_valid_ssh_key_path, device_type_1_0, auth_type):
    device = test_devices_dict[device_type_1_0].copy()
    device["transport"] = "asyncssh"
    if auth_type == "key":
        device.pop("auth_password")
        device["auth_private_key"] = real_valid_ssh_key_path
    conn = AsyncNetconfDriver(**device)
    yield conn, device_type_1_0
    if conn.isalive():
        await conn.close()
        # slow down connections since the lab vms can be slow sometimes
        time.sleep(1)

        if "cisco_iosxr" in device_type_1_0:
            # doubly true for xr vm!
            time.sleep(2)


@pytest.fixture(scope="function")
def sync_conn_1_1(
    test_devices_dict, real_valid_ssh_key_path, device_type_1_1, auth_type, transport
):
    device = test_devices_dict[device_type_1_1].copy()
    if auth_type == "key":
        device.pop("auth_password")
        device["auth_private_key"] = real_valid_ssh_key_path
    conn = NetconfDriver(**device, transport=transport)
    yield conn, device_type_1_1
    if conn.isalive():
        conn.close()
        # slow down connections since the lab vms can be slow sometimes
        time.sleep(1)

        if "cisco_iosxr" in device_type_1_1:
            # doubly true for xr vm!
            time.sleep(2)


@pytest.fixture(scope="function")
async def async_conn_1_1(test_devices_dict, real_valid_ssh_key_path, device_type_1_1, auth_type):
    device = test_devices_dict[device_type_1_1].copy()
    device["transport"] = "asyncssh"
    if auth_type == "key":
        device.pop("auth_password")
        device["auth_private_key"] = real_valid_ssh_key_path
    conn = AsyncNetconfDriver(**device)
    yield conn, device_type_1_1
    if conn.isalive():
        await conn.close()
        # slow down connections since the lab vms can be slow sometimes
        time.sleep(1)

        if "cisco_iosxr" in device_type_1_1:
            # doubly true for xr vm!
            time.sleep(2)


@pytest.fixture(scope="function")
def sync_conn(
    test_devices_dict,
    real_valid_ssh_key_path,
    device_type,
    auth_type,
    transport,
    use_compressed_parser,
):
    device = test_devices_dict[device_type].copy()
    if auth_type == "key":
        device.pop("auth_password")
        device["auth_private_key"] = real_valid_ssh_key_path
    conn = NetconfDriver(**device, transport=transport, use_compressed_parser=use_compressed_parser)
    yield conn, device_type
    if conn.isalive():
        conn.close()
        # slow down connections since the lab vms can be slow sometimes
        time.sleep(1)

        if "cisco_iosxr" in device_type:
            # doubly true for xr vm!
            time.sleep(2)


@pytest.fixture(scope="function")
async def async_conn(test_devices_dict, real_valid_ssh_key_path, device_type, auth_type):
    device = test_devices_dict[device_type].copy()
    device["transport"] = "asyncssh"
    if auth_type == "key":
        device.pop("auth_password")
        device["auth_private_key"] = real_valid_ssh_key_path
    conn = AsyncNetconfDriver(**device)
    yield conn, device_type
    if conn.isalive():
        await conn.close()
        # slow down connections since the lab vms can be slow sometimes
        time.sleep(1)

        if "cisco_iosxr" in device_type:
            # doubly true for xr vm!
            time.sleep(2)
