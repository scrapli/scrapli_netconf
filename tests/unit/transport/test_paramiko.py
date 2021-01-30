from scrapli_netconf.driver import NetconfScrape
from scrapli_netconf.transport.plugins.paramiko.transport import NetconfParamikoTransport


def test_init():
    conn = NetconfScrape(host="localhost", transport="paramiko")
    assert isinstance(conn.transport, NetconfParamikoTransport)
