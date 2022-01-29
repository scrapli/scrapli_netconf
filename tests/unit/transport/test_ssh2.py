from scrapli_netconf.driver import NetconfDriver


def test_init():
    # importing in here for now to not break 3.10 tests
    from scrapli_netconf.transport.plugins.ssh2.transport import NetconfSsh2Transport

    conn = NetconfDriver(host="localhost", transport="ssh2")
    assert isinstance(conn.transport, NetconfSsh2Transport)
