import time

import pytest

from scrapli_netconf.driver.async_driver import AsyncNetconfScrape
from scrapli_netconf.driver.driver import NetconfScrape

from ..test_data.devices import DEVICES, PRIVATE_KEY


@pytest.fixture(
    scope="session", params=["cisco_iosxe", "cisco_iosxr", "juniper_junos"],
)
def device_type(request):
    yield request.param


@pytest.fixture(scope="session", params=["password"])
def auth_type(request):
    yield request.param


@pytest.fixture(scope="function")
def sync_conn(device_type, auth_type):
    device = DEVICES[device_type].copy()
    device.pop("base_config")
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
    device.pop("base_config")
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
