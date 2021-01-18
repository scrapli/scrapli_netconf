import pytest

from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.exceptions import CouldNotExchangeCapabilities


def test_process_output(dummy_conn):
    output = dummy_conn.channel._process_output(buf=b"tacocat", strip_prompt=True)
    assert output == b"tacocat"


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


def test_process_server_capabilities_1_0(
    dummy_conn, server_capabilities_1_0, parsed_server_capabilities_1_0
):
    client_capabilities = dummy_conn.channel._parse_server_capabilities(
        raw_server_capabilities=server_capabilities_1_0
    )
    assert client_capabilities == parsed_server_capabilities_1_0


def test_process_server_capabilities_1_1(
    dummy_conn, server_capabilities_1_1, parsed_server_capabilities_1_1
):
    client_capabilities = dummy_conn.channel._parse_server_capabilities(
        raw_server_capabilities=server_capabilities_1_1
    )
    assert client_capabilities == parsed_server_capabilities_1_1


def test_process_server_capabilities_1_1_namespace(
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
        (b"kasfalskjflkajfew", False),
        (b"<hello>", True),
        (b"<nc:hello>", True),
    ],
    ids=["no_hello", "hello", "hello_namespace"],
)
def test__authenticate_check_hello(dummy_conn, test_data):
    output, expected = test_data
    assert dummy_conn.channel._authenticate_check_hello(buf=output) is expected
