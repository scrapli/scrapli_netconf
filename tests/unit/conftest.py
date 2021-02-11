import pytest

from scrapli.channel.base_channel import BaseChannelArgs
from scrapli_netconf.channel.async_channel import AsyncNetconfChannel
from scrapli_netconf.channel.base_channel import NetconfBaseChannelArgs
from scrapli_netconf.channel.sync_channel import NetconfChannel
from scrapli_netconf.driver import AsyncNetconfDriver, NetconfDriver


@pytest.fixture(scope="function")
def dummy_conn():
    conn = NetconfDriver(host="localhost")
    return conn


@pytest.fixture(scope="function")
def dummy_async_conn():
    conn = AsyncNetconfDriver(host="localhost", transport="asyncssh")
    return conn


@pytest.fixture(scope="function")
def server_capabilities_1_0():
    SERVER_CAPABILITIES_1_0 = b"""<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <capabilities>
        <capability>urn:ietf:params:netconf:base:1.0</capability>
        <capability>urn:ietf:params:netconf:capability:writeable-running:1.0</capability>
        <capability>urn:ietf:params:netconf:capability:rollback-on-error:1.0</capability>
        <capability>urn:ietf:params:netconf:capability:startup:1.0</capability>
        <capability>urn:ietf:params:netconf:capability:url:1.0</capability>
        <capability>urn:cisco:params:netconf:capability:pi-data-model:1.0</capability>
        <capability>urn:cisco:params:netconf:capability:notification:1.0</capability>
    </capabilities>
    <session-id>151399960</session-id>
</hello>]]>]]>"""
    return SERVER_CAPABILITIES_1_0


@pytest.fixture(scope="function")
def parsed_server_capabilities_1_0():
    PARSED_CAPABILITIES_1_0 = [
        "urn:ietf:params:netconf:base:1.0",
        "urn:ietf:params:netconf:capability:writeable-running:1.0",
        "urn:ietf:params:netconf:capability:rollback-on-error:1.0",
        "urn:ietf:params:netconf:capability:startup:1.0",
        "urn:ietf:params:netconf:capability:url:1.0",
        "urn:cisco:params:netconf:capability:pi-data-model:1.0",
        "urn:cisco:params:netconf:capability:notification:1.0",
    ]
    return PARSED_CAPABILITIES_1_0


@pytest.fixture(scope="function")
def server_capabilities_1_1():
    SERVER_CAPABILITIES_1_1 = b"""<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
 <capabilities>
  <capability>urn:ietf:params:netconf:base:1.1</capability>
  <capability>urn:ietf:params:netconf:capability:candidate:1.0</capability>
  <capability>urn:ietf:params:netconf:capability:rollback-on-error:1.0</capability>
  <capability>urn:ietf:params:netconf:capability:validate:1.1</capability>
  <capability>urn:ietf:params:netconf:capability:confirmed-commit:1.1</capability>
  <capability>urn:ietf:params:netconf:capability:notification:1.0</capability>
  <capability>urn:ietf:params:netconf:capability:interleave:1.0</capability>
 </capabilities>
 <session-id>3671877071</session-id>
</hello>
]]>]]>"""
    return SERVER_CAPABILITIES_1_1


@pytest.fixture(scope="function")
def server_capabilities_1_1_namespace():
    SERVER_CAPABILITIES_1_1_NAMESPACE = b"""<nc:hello xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
 <capabilities>
  <capability>urn:ietf:params:netconf:base:1.1</capability>
  <capability>urn:ietf:params:netconf:capability:candidate:1.0</capability>
  <capability>urn:ietf:params:netconf:capability:rollback-on-error:1.0</capability>
  <capability>urn:ietf:params:netconf:capability:validate:1.1</capability>
  <capability>urn:ietf:params:netconf:capability:confirmed-commit:1.1</capability>
  <capability>urn:ietf:params:netconf:capability:notification:1.0</capability>
  <capability>urn:ietf:params:netconf:capability:interleave:1.0</capability>
 </capabilities>
 <session-id>3671877071</session-id>
</nc:hello>
]]>]]>"""
    return SERVER_CAPABILITIES_1_1_NAMESPACE


@pytest.fixture(scope="function")
def parsed_server_capabilities_1_1():
    PARSED_CAPABILITIES_1_1 = [
        "urn:ietf:params:netconf:base:1.1",
        "urn:ietf:params:netconf:capability:candidate:1.0",
        "urn:ietf:params:netconf:capability:rollback-on-error:1.0",
        "urn:ietf:params:netconf:capability:validate:1.1",
        "urn:ietf:params:netconf:capability:confirmed-commit:1.1",
        "urn:ietf:params:netconf:capability:notification:1.0",
        "urn:ietf:params:netconf:capability:interleave:1.0",
    ]
    return PARSED_CAPABILITIES_1_1


@pytest.fixture(scope="function")
def server_capabilities_both():
    SERVER_CAPABILITIES_1_0 = b"""<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <capabilities>
        <capability>urn:ietf:params:netconf:base:1.0</capability>
        <capability>urn:ietf:params:netconf:base:1.1</capability>
    </capabilities>
    <session-id>151399960</session-id>
</hello>]]>]]>"""
    return SERVER_CAPABILITIES_1_0


# Channel related fixtures


@pytest.fixture(scope="function")
def base_channel_args():
    base_channel_args = BaseChannelArgs()
    return base_channel_args


@pytest.fixture(scope="function")
def base_netconf_channel_args():
    base_channel_args = NetconfBaseChannelArgs()
    return base_channel_args


@pytest.fixture(scope="function")
def sync_channel(sync_transport_no_abc, base_channel_args):
    sync_channel = NetconfChannel(
        transport=sync_transport_no_abc, base_channel_args=base_channel_args
    )
    return sync_channel


@pytest.fixture(scope="function")
def async_channel(async_transport_no_abc, base_channel_args):
    async_channel = AsyncNetconfChannel(
        transport=async_transport_no_abc, base_channel_args=base_channel_args
    )
    return async_channel
