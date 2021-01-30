from scrapli_netconf.driver import AsyncNetconfScrape
from scrapli_netconf.transport.plugins.asyncssh.transport import NetconfAsyncsshTransport


def test_init():
    conn = AsyncNetconfScrape(host="localhost", transport="asyncssh")
    assert isinstance(conn.transport, NetconfAsyncsshTransport)
