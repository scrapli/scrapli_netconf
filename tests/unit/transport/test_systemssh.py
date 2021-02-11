from scrapli_netconf.driver import NetconfDriver
from scrapli_netconf.transport.plugins.system.transport import NetconfSystemTransport


def test_init():
    conn = NetconfDriver(host="localhost")
    assert isinstance(conn.transport, NetconfSystemTransport)
