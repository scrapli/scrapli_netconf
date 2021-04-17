<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_netconf.channel.sync_channel

scrapli_netconf.channel.sync_channel

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_netconf.channel.sync_channel"""
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from select import select
from typing import Optional

from scrapli.channel import Channel
from scrapli.channel.base_channel import BaseChannelArgs
from scrapli.decorators import ChannelTimeout
from scrapli.exceptions import ScrapliAuthenticationFailed
from scrapli.transport.base import Transport
from scrapli_netconf.channel.base_channel import BaseNetconfChannel, NetconfBaseChannelArgs
from scrapli_netconf.constants import NetconfVersion

HELLO_MATCH = re.compile(pattern=rb"<(\w+\:){0,1}hello", flags=re.I)


class NetconfChannel(Channel, BaseNetconfChannel):
    def __init__(
        self,
        transport: Transport,
        base_channel_args: BaseChannelArgs,
        netconf_base_channel_args: NetconfBaseChannelArgs,
    ):
        super().__init__(transport=transport, base_channel_args=base_channel_args)

        self._netconf_base_channel_args = netconf_base_channel_args

        # always use `]]>]]>` as the initial prompt to match
        self._base_channel_args.comms_prompt_pattern = "]]>]]>"
        self._server_echo: Optional[bool] = None
        self._capabilities_buf = b""

    def open_netconf(self) -> None:
        """
        Open the netconf channel

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        # open in scrapli core is where we open channel log (if applicable), do that
        self.open()

        raw_server_capabilities = self._get_server_capabilities()

        self._process_capabilities_exchange(raw_server_capabilities=raw_server_capabilities)

        self._check_echo()
        self._send_client_capabilities()

    @staticmethod
    def _authenticate_check_hello(buf: bytes) -> bool:
        """
        Check if "hello" message is in output

        Args:
            buf: bytes output from the channel

        Returns:
            bool: true if hello message is seen, otherwise false

        Raises:
            N/A

        """
        hello_match = re.search(pattern=HELLO_MATCH, string=buf)
        if hello_match:
            return True
        return False

    @ChannelTimeout("timed out during in channel netconf authentication")
    def channel_authenticate_netconf(
        self, auth_password: str, auth_private_key_passphrase: str
    ) -> None:
        """
        Handle SSH Authentication for transports that only operate "in the channel" (i.e. system)

        Args:
            auth_password: password to authenticate with
            auth_private_key_passphrase: passphrase for ssh key if necessary

        Returns:
            None

        Raises:
            ScrapliAuthenticationFailed: if password prompt seen more than twice
            ScrapliAuthenticationFailed: if passphrase prompt seen more than twice

        """
        self.logger.debug("attempting in channel netconf authentication")

        password_count = 0
        passphrase_count = 0
        authenticate_buf = b""

        with self._channel_lock():
            while True:
                buf = self.read()

                authenticate_buf += buf.lower()
                self._capabilities_buf += buf

                self._ssh_message_handler(output=authenticate_buf)

                if b"password" in authenticate_buf:
                    # clear the authentication buffer so we don't re-read the password prompt
                    authenticate_buf = b""
                    password_count += 1
                    if password_count > 2:
                        msg = "password prompt seen more than once, assuming auth failed"
                        self.logger.critical(msg)
                        raise ScrapliAuthenticationFailed(msg)
                    self.write(channel_input=auth_password, redacted=True)
                    self.send_return()

                if b"enter passphrase for key" in authenticate_buf:
                    # clear the authentication buffer so we don't re-read the passphrase prompt
                    authenticate_buf = b""
                    passphrase_count += 1
                    if passphrase_count > 2:
                        msg = "passphrase prompt seen more than once, assuming auth failed"
                        self.logger.critical(msg)
                        raise ScrapliAuthenticationFailed(msg)
                    self.write(channel_input=auth_private_key_passphrase, redacted=True)
                    self.send_return()

                if self._authenticate_check_hello(buf=authenticate_buf):
                    self.logger.info(
                        "found start of server capabilities, authentication successful"
                    )
                    return

    def __check_echo(self, echo_timeout: float) -> None:
        """
        Function to drop into check echo thread

        In the case of asyncio we just have a coroutine on the loop to check if the device echos
        the inputs back to us

        Args:
            echo_timeout: duration to check echo for

        Returns:
            None

        Raises:
            N/A

        """
        channel_fd = self.transport._get_channel_fd()  # type: ignore  # pylint: disable=W0212
        start = datetime.now().timestamp()
        while True:
            fd_ready, _, _ = select([channel_fd], [], [], 0)
            if channel_fd in fd_ready:
                self.logger.debug("setting _server_echo to true")
                self._server_echo = True
                break
            interval_end = datetime.now().timestamp()
            if (interval_end - start) > echo_timeout:
                self.logger.debug("setting _server_echo to false")
                self._server_echo = False
                break

    def _check_echo(self) -> None:
        """
        Determine if inputs are "echoed" back on stdout

        At least per early drafts of the netconf over ssh rfcs the netconf servers MUST NOT echo the
        input commands back to the client. In the case of "normal" scrapli netconf with the system
        transport this happens anyway because we combine the stdin and stdout fds into a single pty,
        however for other transports we have an actual stdin and stdout fd to read/write. It seems
        that at the very least IOSXE with NETCONF 1.1 seems to want to echo inputs back onto to the
        stdout for the channel. This is totally ok and we can deal with it, we just need to *know*
        that it is happening and that gives us somewhat of a dilemma... we want to give the device
        time to echo this data back to us, but we also dont want to just arbitrarily wait
        (especially in the more common case where the device is *not* echoing anything back). So we
        take 1/20th of the transport timeout and we wait that long to see -- if we get echo, we
        return immediately of course, otherwise there is an unfortunate slight delay here :(

        See: https://tools.ietf.org/html/draft-ietf-netconf-ssh-02 (search for "echo")

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        # for users who set timeout ops to 0 to avoid the overhead of the timeout threads we'll rely
        # on the default scrapli timeout ops here
        _timeout_ops = self._base_channel_args.timeout_ops or 30
        pool = ThreadPoolExecutor(max_workers=1)
        pool.submit(self.__check_echo, _timeout_ops / 20)

    @ChannelTimeout(
        "timed out determining if session is authenticated/getting server capabilities",
    )
    def _get_server_capabilities(self) -> bytes:
        """
        Read until all server capabilities have been sent by server

        Args:
            N/A

        Returns:
            bytes: raw bytes containing server capabilities

        Raises:
            N/A

        """
        capabilities_buf = self._capabilities_buf

        # reset this to empty to avoid any confusion now that we are moving on
        self._capabilities_buf = b""

        with self._channel_lock():
            while b"]]>]]>" not in capabilities_buf:
                capabilities_buf += self.read()
            self.logger.debug(f"received raw server capabilities: {repr(capabilities_buf)}")
        return capabilities_buf

    @ChannelTimeout("timed out sending client capabilities")
    def _send_client_capabilities(
        self,
    ) -> None:
        """
        Send client capabilities to the netconf server

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        with self._channel_lock():
            bytes_client_capabilities = self._pre_send_client_capabilities(
                client_capabilities=self._netconf_base_channel_args.client_capabilities
            )

            # in case of "system" transport we'll always want to read off the hello message inputs
            if self._server_echo is True:
                self._read_until_input(channel_input=bytes_client_capabilities)

            self.send_return()

            while self._server_echo is None:
                pass

    def _read_until_input(self, channel_input: bytes) -> bytes:
        """
        Async read until all input has been entered.

        Args:
            channel_input: string to write to channel

        Returns:
            bytes: output read from channel

        Raises:
            N/A

        """
        output = b""

        if self._server_echo is False:
            return output

        if not channel_input:
            self.logger.info(f"Read: {repr(output)}")
            return output

        while True:
            output += self.read()
            # if we have all the input *or* we see the closing rpc tag we know we are done here
            if channel_input in output or b"rpc>" in output:
                break

        self.logger.info(f"Read: {repr(output)}")
        return output

    def send_input_netconf(self, channel_input: str) -> bytes:
        """
        Send inputs to netconf server

        Args:
            channel_input: string of the base xml message to send to netconf server

        Returns:
            bytes: bytes result of message sent to netconf server

        Raises:
            N/A

        """
        final_channel_input = self._build_message(channel_input)
        bytes_final_channel_input = final_channel_input.encode()

        buf: bytes
        buf, _ = super().send_input(
            channel_input=final_channel_input, strip_prompt=False, eager=True
        )

        if bytes_final_channel_input in buf:
            # if we got the input AND the rpc-reply we can strip out our inputs so we just have the
            # reply remaining
            buf = buf.split(bytes_final_channel_input)[1]

        buf = self._read_until_prompt(buf=buf)

        if self._netconf_base_channel_args.netconf_version == NetconfVersion.VERSION_1_1:
            # netconf 1.1 with "chunking" style message format needs an extra return char here
            self.send_return()

        return buf
        </code>
    </pre>
</details>



## Classes

### NetconfChannel


```text
BaseChannel Object -- provides convenience methods to both sync and async Channels

Args:
    transport: initialized scrapli Transport/AsyncTransport object
    base_channel_args: BaseChannelArgs object

Returns:
    None

Raises:
    N/A
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class NetconfChannel(Channel, BaseNetconfChannel):
    def __init__(
        self,
        transport: Transport,
        base_channel_args: BaseChannelArgs,
        netconf_base_channel_args: NetconfBaseChannelArgs,
    ):
        super().__init__(transport=transport, base_channel_args=base_channel_args)

        self._netconf_base_channel_args = netconf_base_channel_args

        # always use `]]>]]>` as the initial prompt to match
        self._base_channel_args.comms_prompt_pattern = "]]>]]>"
        self._server_echo: Optional[bool] = None
        self._capabilities_buf = b""

    def open_netconf(self) -> None:
        """
        Open the netconf channel

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        # open in scrapli core is where we open channel log (if applicable), do that
        self.open()

        raw_server_capabilities = self._get_server_capabilities()

        self._process_capabilities_exchange(raw_server_capabilities=raw_server_capabilities)

        self._check_echo()
        self._send_client_capabilities()

    @staticmethod
    def _authenticate_check_hello(buf: bytes) -> bool:
        """
        Check if "hello" message is in output

        Args:
            buf: bytes output from the channel

        Returns:
            bool: true if hello message is seen, otherwise false

        Raises:
            N/A

        """
        hello_match = re.search(pattern=HELLO_MATCH, string=buf)
        if hello_match:
            return True
        return False

    @ChannelTimeout("timed out during in channel netconf authentication")
    def channel_authenticate_netconf(
        self, auth_password: str, auth_private_key_passphrase: str
    ) -> None:
        """
        Handle SSH Authentication for transports that only operate "in the channel" (i.e. system)

        Args:
            auth_password: password to authenticate with
            auth_private_key_passphrase: passphrase for ssh key if necessary

        Returns:
            None

        Raises:
            ScrapliAuthenticationFailed: if password prompt seen more than twice
            ScrapliAuthenticationFailed: if passphrase prompt seen more than twice

        """
        self.logger.debug("attempting in channel netconf authentication")

        password_count = 0
        passphrase_count = 0
        authenticate_buf = b""

        with self._channel_lock():
            while True:
                buf = self.read()

                authenticate_buf += buf.lower()
                self._capabilities_buf += buf

                self._ssh_message_handler(output=authenticate_buf)

                if b"password" in authenticate_buf:
                    # clear the authentication buffer so we don't re-read the password prompt
                    authenticate_buf = b""
                    password_count += 1
                    if password_count > 2:
                        msg = "password prompt seen more than once, assuming auth failed"
                        self.logger.critical(msg)
                        raise ScrapliAuthenticationFailed(msg)
                    self.write(channel_input=auth_password, redacted=True)
                    self.send_return()

                if b"enter passphrase for key" in authenticate_buf:
                    # clear the authentication buffer so we don't re-read the passphrase prompt
                    authenticate_buf = b""
                    passphrase_count += 1
                    if passphrase_count > 2:
                        msg = "passphrase prompt seen more than once, assuming auth failed"
                        self.logger.critical(msg)
                        raise ScrapliAuthenticationFailed(msg)
                    self.write(channel_input=auth_private_key_passphrase, redacted=True)
                    self.send_return()

                if self._authenticate_check_hello(buf=authenticate_buf):
                    self.logger.info(
                        "found start of server capabilities, authentication successful"
                    )
                    return

    def __check_echo(self, echo_timeout: float) -> None:
        """
        Function to drop into check echo thread

        In the case of asyncio we just have a coroutine on the loop to check if the device echos
        the inputs back to us

        Args:
            echo_timeout: duration to check echo for

        Returns:
            None

        Raises:
            N/A

        """
        channel_fd = self.transport._get_channel_fd()  # type: ignore  # pylint: disable=W0212
        start = datetime.now().timestamp()
        while True:
            fd_ready, _, _ = select([channel_fd], [], [], 0)
            if channel_fd in fd_ready:
                self.logger.debug("setting _server_echo to true")
                self._server_echo = True
                break
            interval_end = datetime.now().timestamp()
            if (interval_end - start) > echo_timeout:
                self.logger.debug("setting _server_echo to false")
                self._server_echo = False
                break

    def _check_echo(self) -> None:
        """
        Determine if inputs are "echoed" back on stdout

        At least per early drafts of the netconf over ssh rfcs the netconf servers MUST NOT echo the
        input commands back to the client. In the case of "normal" scrapli netconf with the system
        transport this happens anyway because we combine the stdin and stdout fds into a single pty,
        however for other transports we have an actual stdin and stdout fd to read/write. It seems
        that at the very least IOSXE with NETCONF 1.1 seems to want to echo inputs back onto to the
        stdout for the channel. This is totally ok and we can deal with it, we just need to *know*
        that it is happening and that gives us somewhat of a dilemma... we want to give the device
        time to echo this data back to us, but we also dont want to just arbitrarily wait
        (especially in the more common case where the device is *not* echoing anything back). So we
        take 1/20th of the transport timeout and we wait that long to see -- if we get echo, we
        return immediately of course, otherwise there is an unfortunate slight delay here :(

        See: https://tools.ietf.org/html/draft-ietf-netconf-ssh-02 (search for "echo")

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        # for users who set timeout ops to 0 to avoid the overhead of the timeout threads we'll rely
        # on the default scrapli timeout ops here
        _timeout_ops = self._base_channel_args.timeout_ops or 30
        pool = ThreadPoolExecutor(max_workers=1)
        pool.submit(self.__check_echo, _timeout_ops / 20)

    @ChannelTimeout(
        "timed out determining if session is authenticated/getting server capabilities",
    )
    def _get_server_capabilities(self) -> bytes:
        """
        Read until all server capabilities have been sent by server

        Args:
            N/A

        Returns:
            bytes: raw bytes containing server capabilities

        Raises:
            N/A

        """
        capabilities_buf = self._capabilities_buf

        # reset this to empty to avoid any confusion now that we are moving on
        self._capabilities_buf = b""

        with self._channel_lock():
            while b"]]>]]>" not in capabilities_buf:
                capabilities_buf += self.read()
            self.logger.debug(f"received raw server capabilities: {repr(capabilities_buf)}")
        return capabilities_buf

    @ChannelTimeout("timed out sending client capabilities")
    def _send_client_capabilities(
        self,
    ) -> None:
        """
        Send client capabilities to the netconf server

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        with self._channel_lock():
            bytes_client_capabilities = self._pre_send_client_capabilities(
                client_capabilities=self._netconf_base_channel_args.client_capabilities
            )

            # in case of "system" transport we'll always want to read off the hello message inputs
            if self._server_echo is True:
                self._read_until_input(channel_input=bytes_client_capabilities)

            self.send_return()

            while self._server_echo is None:
                pass

    def _read_until_input(self, channel_input: bytes) -> bytes:
        """
        Async read until all input has been entered.

        Args:
            channel_input: string to write to channel

        Returns:
            bytes: output read from channel

        Raises:
            N/A

        """
        output = b""

        if self._server_echo is False:
            return output

        if not channel_input:
            self.logger.info(f"Read: {repr(output)}")
            return output

        while True:
            output += self.read()
            # if we have all the input *or* we see the closing rpc tag we know we are done here
            if channel_input in output or b"rpc>" in output:
                break

        self.logger.info(f"Read: {repr(output)}")
        return output

    def send_input_netconf(self, channel_input: str) -> bytes:
        """
        Send inputs to netconf server

        Args:
            channel_input: string of the base xml message to send to netconf server

        Returns:
            bytes: bytes result of message sent to netconf server

        Raises:
            N/A

        """
        final_channel_input = self._build_message(channel_input)
        bytes_final_channel_input = final_channel_input.encode()

        buf: bytes
        buf, _ = super().send_input(
            channel_input=final_channel_input, strip_prompt=False, eager=True
        )

        if bytes_final_channel_input in buf:
            # if we got the input AND the rpc-reply we can strip out our inputs so we just have the
            # reply remaining
            buf = buf.split(bytes_final_channel_input)[1]

        buf = self._read_until_prompt(buf=buf)

        if self._netconf_base_channel_args.netconf_version == NetconfVersion.VERSION_1_1:
            # netconf 1.1 with "chunking" style message format needs an extra return char here
            self.send_return()

        return buf
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli.channel.sync_channel.Channel
- scrapli_netconf.channel.base_channel.BaseNetconfChannel
- scrapli.channel.base_channel.BaseChannel
#### Methods

    

##### channel_authenticate_netconf
`channel_authenticate_netconf(self, auth_password: str, auth_private_key_passphrase: str) ‑> NoneType`

```text
Handle SSH Authentication for transports that only operate "in the channel" (i.e. system)

Args:
    auth_password: password to authenticate with
    auth_private_key_passphrase: passphrase for ssh key if necessary

Returns:
    None

Raises:
    ScrapliAuthenticationFailed: if password prompt seen more than twice
    ScrapliAuthenticationFailed: if passphrase prompt seen more than twice
```



    

##### open_netconf
`open_netconf(self) ‑> NoneType`

```text
Open the netconf channel

Args:
    N/A

Returns:
    None

Raises:
    N/A
```



    

##### send_input_netconf
`send_input_netconf(self, channel_input: str) ‑> bytes`

```text
Send inputs to netconf server

Args:
    channel_input: string of the base xml message to send to netconf server

Returns:
    bytes: bytes result of message sent to netconf server

Raises:
    N/A
```