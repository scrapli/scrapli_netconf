import pytest


@pytest.mark.parametrize(
    "test_data",
    [
        (b"kasfalskjflkajfew", False),
        (b"<hello>", True),
        (b"<nc:hello>", True),
    ],
    ids=["no_hello", "hello", "hello_namespace"],
)
def test__authenticate_check_hello(dummy_conn, test_data):
    output, expected = test_data
    assert dummy_conn.channel._authenticate_check_hello(buf=output) is expected
