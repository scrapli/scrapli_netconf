from scrapli_netconf.driver import NetconfScrape
from scrapli_netconf.transport.plugins.system.transport import NetconfSystemTransport


def test_init():
    conn = NetconfScrape(host="localhost")
    assert isinstance(conn.transport, NetconfSystemTransport)
