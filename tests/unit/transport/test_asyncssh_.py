from scrapli_netconf.driver import AsyncNetconfDriver
from scrapli_netconf.transport.plugins.asyncssh.transport import NetconfAsyncsshTransport


def test_init():
    conn = AsyncNetconfDriver(host="localhost", transport="asyncssh")
    assert isinstance(conn.transport, NetconfAsyncsshTransport)
