import pytest


def test_open_netconf():
    pass


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


def test_channel_authenticate_netconf(monkeypatch, dummy_conn):
    dummy_conn.channel._base_channel_args.comms_ansi = True

    _read_counter = 0
    _write_counter = 0

    def _read(cls):
        nonlocal _read_counter

        if _read_counter == 0:
            _read_counter += 1
            return b"blah blah blah"

        elif _read_counter == 1:
            _read_counter += 1
            return b"enter passphrase for key"

        elif _read_counter == 2:
            _read_counter += 1
            return b"blah blah blah"

        elif _read_counter == 3:
            _read_counter += 1
            return b"password"

        elif _read_counter == 4:
            _read_counter += 1
            return b"blah blah blah"

        return b"<hello>"

    def _write(cls, channel_input):
        # just making this a non-op
        pass

    monkeypatch.setattr("scrapli.transport.plugins.system.transport.SystemTransport.read", _read)
    monkeypatch.setattr("scrapli.transport.plugins.system.transport.SystemTransport.write", _write)

    dummy_conn.channel.channel_authenticate_netconf(
        auth_password="scrapli", auth_private_key_passphrase="scrapli_key"
    )


def test__check_echo():
    pass


def test_check_echo():
    pass


def test_get_server_capabilities():
    pass


def test_send_client_capabilities():
    pass


def test_read_until_input():
    pass


def test_send_input_netconf(monkeypatch, dummy_conn):
    _read_counter = 0

    channel_input = "show version"
    expected_buf = b"output from show version!\n]]>]]>"

    def _read(cls):
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

    monkeypatch.setattr("scrapli.transport.plugins.system.transport.SystemTransport.read", _read)
    monkeypatch.setattr("scrapli.transport.plugins.system.transport.SystemTransport.write", _write)

    actual_buf = dummy_conn.channel.send_input_netconf(channel_input=channel_input)
    assert actual_buf == expected_buf
