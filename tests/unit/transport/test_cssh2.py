import pytest

from scrapli.exceptions import TransportPluginError
from scrapli_netconf.driver import NetconfScrape
from scrapli_netconf.transport.cssh2 import NetconfSSH2Transport


def test_init_invalid_transport():
    with pytest.raises(TransportPluginError) as exc:
        NetconfScrape(host="localhost", transport="telnet")
    assert str(exc.value) == "NETCONF does not support telnet!"


def test_init():
    conn = NetconfScrape(host="localhost", transport="ssh2")
    assert conn.transport_class == NetconfSSH2Transport
