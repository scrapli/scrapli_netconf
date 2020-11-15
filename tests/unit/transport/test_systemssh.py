import pytest

from scrapli.exceptions import TransportPluginError
from scrapli_netconf.driver import NetconfScrape
from scrapli_netconf.transport.systemssh import NetconfSystemSSHTransport


def test_init_invalid_transport():
    with pytest.raises(TransportPluginError) as exc:
        NetconfScrape(host="localhost", transport="telnet")
    assert str(exc.value) == "NETCONF does not support telnet!"


def test_init():
    conn = NetconfScrape(host="localhost")
    assert conn.transport_class == NetconfSystemSSHTransport


@pytest.mark.parametrize(
    "message_data",
    [
        (b"kasfalskjflkajfew", False),
        (b"<hello>", True),
        (b"<nc:hello>", True),
    ],
    ids=["no_hello", "hello", "hello_namespace"],
)
def test__authenticate_check_hello(message_data):
    output = message_data[0]
    expected = message_data[1]
    transport = NetconfSystemSSHTransport(host="localhost")
    assert transport._authenticate_check_hello(output=output) is expected
