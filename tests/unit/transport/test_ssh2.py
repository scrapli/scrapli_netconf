from scrapli_netconf.driver import NetconfScrape
from scrapli_netconf.transport.plugins.ssh2.transport import NetconfSsh2Transport


def test_init():
    conn = NetconfScrape(host="localhost", transport="ssh2")
    assert isinstance(conn.transport, NetconfSsh2Transport)
