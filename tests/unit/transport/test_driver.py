import pytest

from scrapli.exceptions import TransportPluginError
from scrapli_netconf.driver import NetconfScrape
from scrapli_netconf.transport.systemssh import NetconfSystemSSHTransport


def test_init_invalid_transport():
    with pytest.raises(TransportPluginError) as exc:
        NetconfScrape(host="localhost", transport="telnet")
    assert str(exc.value) == "`NetconfScrape` is only supported using the `system` transport plugin"


def test_init():
    conn = NetconfScrape(host="localhost")
    assert conn.transport_class == NetconfSystemSSHTransport
