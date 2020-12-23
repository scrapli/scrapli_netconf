import pytest

from scrapli.exceptions import TransportPluginError
from scrapli_netconf.driver import AsyncNetconfScrape
from scrapli_netconf.transport.asyncssh_ import NetconfAsyncSSHTransport


def test_init_invalid_transport():
    with pytest.raises(TransportPluginError) as exc:
        AsyncNetconfScrape(host="localhost")
    assert (
        "Attempting to use transport type system with an asyncio driver, must use one of "
        in str(exc.value)
    )


def test_init():
    conn = AsyncNetconfScrape(host="localhost", transport="asyncssh")
    assert conn.transport_class == NetconfAsyncSSHTransport
