import pytest

from scrapli_netconf.constants import NetconfClientCapabilities, NetconfVersion
from scrapli_netconf.exceptions import CapabilityNotSupported, CouldNotExchangeCapabilities

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


@pytest.mark.parametrize(
    "test_data",
    (
        (
            NetconfVersion.VERSION_1_0,
            SERVER_CAPABILITIES_1_0,
        ),
        (
            NetconfVersion.VERSION_1_1,
            SERVER_CAPABILITIES_1_1,
        ),
    ),
    ids=(
        "prefer_1_0",
        "prefer_1_1",
    ),
)
def test_process_capabilities_exchange_user_preference(dummy_conn, test_data):
    preferred_version, raw_capabilities = test_data
    dummy_conn._netconf_base_channel_args.netconf_version = preferred_version
    dummy_conn.channel._process_capabilities_exchange(raw_server_capabilities=raw_capabilities)
    assert dummy_conn.netconf_version == preferred_version


@pytest.mark.parametrize(
    "test_data",
    (
        (
            NetconfVersion.VERSION_1_0,
            SERVER_CAPABILITIES_1_1,
        ),
        (
            NetconfVersion.VERSION_1_1,
            SERVER_CAPABILITIES_1_0,
        ),
    ),
    ids=(
        "prefer_1_0",
        "prefer_1_1",
    ),
)
def test_process_capabilities_exchange_user_preference_exception(
    dummy_conn, server_capabilities_both, test_data
):
    preferred_version, raw_capabilities = test_data

    with pytest.raises(CapabilityNotSupported):
        dummy_conn._netconf_base_channel_args.netconf_version = preferred_version
        dummy_conn.channel._process_capabilities_exchange(raw_server_capabilities=raw_capabilities)


def test_parse_server_capabilities_1_0(
    dummy_conn, server_capabilities_1_0, parsed_server_capabilities_1_0
):
    client_capabilities = dummy_conn.channel._parse_server_capabilities(
        raw_server_capabilities=server_capabilities_1_0
    )
    assert client_capabilities == parsed_server_capabilities_1_0


def test_parse_server_capabilities_1_1(
    dummy_conn, server_capabilities_1_1, parsed_server_capabilities_1_1
):
    client_capabilities = dummy_conn.channel._parse_server_capabilities(
        raw_server_capabilities=server_capabilities_1_1
    )
    assert client_capabilities == parsed_server_capabilities_1_1


def test_parse_server_capabilities_1_1_namespace(
    dummy_conn, server_capabilities_1_1_namespace, parsed_server_capabilities_1_1
):
    client_capabilities = dummy_conn.channel._parse_server_capabilities(
        raw_server_capabilities=server_capabilities_1_1_namespace
    )
    assert client_capabilities == parsed_server_capabilities_1_1


def test_parse_server_capabilities_exception(dummy_conn):
    with pytest.raises(CouldNotExchangeCapabilities) as exc:
        dummy_conn.channel._parse_server_capabilities(raw_server_capabilities=b"boo!")
    assert "failed to parse server capabilities" in str(exc.value)


@pytest.mark.parametrize(
    "test_data",
    [
        (NetconfVersion.VERSION_1_0, "<tacocat/>", "<tacocat/>"),
        (NetconfVersion.VERSION_1_1, "<tacocat/>", "#10\n<tacocat/>\n##"),
    ],
    ids=["1.0", "1.1"],
)
def test_build_message(dummy_conn, test_data):
    dummy_conn.netconf_version, channel_input, expected_final_channel_input = test_data
    final_channel_input = dummy_conn.channel._build_message(channel_input=channel_input)
    assert final_channel_input == expected_final_channel_input


def test_process_output(dummy_conn):
    output = dummy_conn.channel._process_output(buf=b"tacocat", strip_prompt=True)
    assert output == b"tacocat"


def test_pre_send_client_capabilities(monkeypatch, dummy_conn):
    def _write(cls, channel_input):
        assert (
            channel_input
            == b"""\n<?xml version="1.0" encoding="utf-8"?>
    <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <capabilities>
            <capability>urn:ietf:params:netconf:base:1.0</capability>
        </capabilities>
</hello>]]>]]>"""
        )

    monkeypatch.setattr(
        "scrapli_netconf.transport.plugins.system.transport.NetconfSystemTransport.write", _write
    )

    dummy_conn.channel._pre_send_client_capabilities(
        client_capabilities=NetconfClientCapabilities.CAPABILITIES_1_0
    )
