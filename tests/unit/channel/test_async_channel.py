import pytest


async def test_open_netconf():
    pass


async def test_check_echo():
    pass


async def test_get_server_capabilities(monkeypatch, dummy_async_conn):
    read_counter = 0

    async def _read(cls):
        nonlocal read_counter

        if read_counter == 0:
            read_counter += 1
            return b"lasjdfkldsjaflkdjf"
        return b"]]>]]>"

    monkeypatch.setattr(
        "scrapli.transport.plugins.asyncssh.transport.AsyncsshTransport.read", _read
    )

    assert await dummy_async_conn.channel._get_server_capabilities() == b"lasjdfkldsjaflkdjf]]>]]>"


async def test_send_client_capabilities():
    pass


@pytest.mark.parametrize(
    "test_data",
    ((b"blah", b"blah"), (b"", b""), (b"blah", b"rpc>")),
    ids=("some_input", "no_input", "rpc_in_output"),
)
async def test_read_until_input(monkeypatch, dummy_async_conn, test_data):
    channel_input, expected_read_input = test_data
    dummy_async_conn.channel._server_echo = True

    async def _read(cls):
        nonlocal expected_read_input

        return expected_read_input

    monkeypatch.setattr(
        "scrapli.transport.plugins.asyncssh.transport.AsyncsshTransport.read", _read
    )

    assert (
        await dummy_async_conn.channel._read_until_input(channel_input=channel_input)
        == expected_read_input
    )


async def test_read_until_input_no_echo(dummy_async_conn):
    dummy_async_conn.channel._server_echo = False
    assert await dummy_async_conn.channel._read_until_input(channel_input=b"blah") == b""


async def test_send_input_netconf(monkeypatch, dummy_async_conn):
    _read_counter = 0

    channel_input = "show version"
    expected_buf = b"output from show version!\n]]>]]>"

    async def _read(cls):
        nonlocal _read_counter

        if _read_counter == 0:
            # echo the input back
            _read_counter += 1
            return b"#12\nshow version\n##"
        elif _read_counter == 1:
            _read_counter += 1
            return b"output from show version!\n"
        return b"]]>]]>"

    def _write(cls, channel_input):
        pass

    monkeypatch.setattr(
        "scrapli.transport.plugins.asyncssh.transport.AsyncsshTransport.read", _read
    )
    monkeypatch.setattr(
        "scrapli.transport.plugins.asyncssh.transport.AsyncsshTransport.write", _write
    )

    # even though it doesnt really echo w/ asyncssh we'll set it to true so the test is easier to
    # grock as it will be same/same as the sync one
    dummy_async_conn.channel._server_echo = True
    actual_buf = await dummy_async_conn.channel.send_input_netconf(channel_input=channel_input)
    assert actual_buf == expected_buf
