import sys

import pytest

from scrapli_netconf.driver import NetconfDriver


@pytest.mark.skipif(sys.version_info > (3, 9), reason="skipping ssh2 on 3.10")
def test_init():
    # importing in here for now to not break 3.10 tests
    from scrapli_netconf.transport.plugins.ssh2.transport import NetconfSsh2Transport

    conn = NetconfDriver(host="localhost", transport="ssh2")
    assert isinstance(conn.transport, NetconfSsh2Transport)
