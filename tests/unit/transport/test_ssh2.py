import sys

import pytest

from scrapli_netconf.driver import NetconfDriver
from scrapli_netconf.transport.plugins.ssh2.transport import NetconfSsh2Transport


@pytest.mark.skipif(sys.version_info > (3, 9), reason="skipping ssh2 on 3.10")
def test_init():
    conn = NetconfDriver(host="localhost", transport="ssh2")
    assert isinstance(conn.transport, NetconfSsh2Transport)
