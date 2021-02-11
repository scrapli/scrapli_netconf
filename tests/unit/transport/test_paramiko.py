from scrapli_netconf.driver import NetconfDriver
from scrapli_netconf.transport.plugins.paramiko.transport import NetconfParamikoTransport


def test_init():
    conn = NetconfDriver(host="localhost", transport="paramiko")
    assert isinstance(conn.transport, NetconfParamikoTransport)
