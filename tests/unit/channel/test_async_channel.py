import pytest


@pytest.mark.asyncio
async def test_open_netconf():
    pass


@pytest.mark.asyncio
async def test_channel_authenticate_netconf():
    pass


@pytest.mark.asyncio
async def test__check_echo():
    pass


@pytest.mark.asyncio
async def test_check_echo():
    pass


@pytest.mark.asyncio
async def test_get_server_capabilities():
    pass


@pytest.mark.asyncio
async def test_send_client_capabilities():
    pass


@pytest.mark.asyncio
async def test_read_until_input():
    pass


@pytest.mark.asyncio
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
