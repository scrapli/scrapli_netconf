import time

import pytest

from scrapli_netconf.driver.async_driver import AsyncNetconfScrape
from scrapli_netconf.driver.driver import NetconfScrape

from ..test_data.devices import DEVICES, PRIVATE_KEY

NETCONF_1_0_DEVICE_TYPES = ["cisco_iosxe_1_0", "juniper_junos_1_0"]
NETCONF_1_1_DEVICE_TYPES = ["cisco_iosxe_1_1", "cisco_iosxr_1_1"]
NETCONF_ALL_VERSIONS_DEVICE_TYPES = NETCONF_1_0_DEVICE_TYPES + NETCONF_1_1_DEVICE_TYPES


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


@pytest.fixture(scope="session", params=["password"])
def auth_type(request):
    yield request.param


@pytest.fixture(scope="function")
def sync_conn_1_0(device_type_1_0, auth_type):
    device = DEVICES[device_type_1_0].copy()
    if auth_type == "key":
        device.pop("auth_password")
        device["auth_private_key"] = PRIVATE_KEY
    conn = NetconfScrape(**device)
    yield conn, device_type_1_0
    if conn.isalive():
        conn.close()
        # at the very least iosxr vm seems to not handle back to back to back connections very well
        # a small sleep seems to appease it
        time.sleep(1)


@pytest.fixture(scope="function")
async def async_conn_1_0(device_type_1_0, auth_type):
    device = DEVICES[device_type_1_0].copy()
    device["transport"] = "asyncssh"
    if auth_type == "key":
        device.pop("auth_password")
        device["auth_private_key"] = PRIVATE_KEY
    conn = AsyncNetconfScrape(**device)
    yield conn, device_type_1_0
    if conn.isalive():
        await conn.close()
        # at the very least iosxr vm seems to not handle back to back to back connections very well
        # a small sleep seems to appease it
        time.sleep(1)


@pytest.fixture(scope="function")
def sync_conn_1_1(device_type_1_1, auth_type):
    device = DEVICES[device_type_1_1].copy()
    if auth_type == "key":
        device.pop("auth_password")
        device["auth_private_key"] = PRIVATE_KEY
    conn = NetconfScrape(**device)
    yield conn, device_type_1_1
    if conn.isalive():
        conn.close()
        # at the very least iosxr vm seems to not handle back to back to back connections very well
        # a small sleep seems to appease it
        time.sleep(1)


@pytest.fixture(scope="function")
async def async_conn_1_1(device_type_1_1, auth_type):
    device = DEVICES[device_type_1_1].copy()
    device["transport"] = "asyncssh"
    if auth_type == "key":
        device.pop("auth_password")
        device["auth_private_key"] = PRIVATE_KEY
    conn = AsyncNetconfScrape(**device)
    yield conn, device_type_1_1
    if conn.isalive():
        await conn.close()
        # at the very least iosxr vm seems to not handle back to back to back connections very well
        # a small sleep seems to appease it
        time.sleep(1)


@pytest.fixture(scope="function")
def sync_conn(device_type, auth_type):
    device = DEVICES[device_type].copy()
    if auth_type == "key":
        device.pop("auth_password")
        device["auth_private_key"] = PRIVATE_KEY
    conn = NetconfScrape(**device)
    yield conn, device_type
    if conn.isalive():
        conn.close()
        # at the very least iosxr vm seems to not handle back to back to back connections very well
        # a small sleep seems to appease it
        time.sleep(1)


@pytest.fixture(scope="function")
async def async_conn(device_type, auth_type):
    device = DEVICES[device_type].copy()
    device["transport"] = "asyncssh"
    if auth_type == "key":
        device.pop("auth_password")
        device["auth_private_key"] = PRIVATE_KEY
    conn = AsyncNetconfScrape(**device)
    yield conn, device_type
    if conn.isalive():
        await conn.close()
        # at the very least iosxr vm seems to not handle back to back to back connections very well
        # a small sleep seems to appease it
        time.sleep(1)
