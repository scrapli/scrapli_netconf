import pytest

from scrapli_netconf.driver import NetconfScrape


@pytest.fixture(scope="function")
def dummy_conn():
    conn = NetconfScrape(host="localhost")
    return conn
