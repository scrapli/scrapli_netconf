"""scrapli_netconf.channel.channel"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from select import select
from typing import Any, Optional

from scrapli.channel import Channel
from scrapli.decorators import OperationTimeout
from scrapli.transport import Transport
from scrapli_netconf.channel.base_channel import NetconfChannelBase
from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.driver.base_driver import NetconfClientCapabilities
from scrapli_netconf.transport.systemssh import NetconfSystemSSHTransport


class NetconfChannel(Channel, NetconfChannelBase):
    def __init__(self, transport: Transport, **kwargs: Any):
        # pop the comms prompt pattern out; always use `]]>]]>` as the initial prompt to match
        kwargs.pop("comms_prompt_pattern")
        super().__init__(transport, comms_prompt_pattern="]]>]]>", **kwargs)

        self.netconf_version = NetconfVersion.VERSION_1_0
        self._server_echo: Optional[bool] = None

    def __check_echo(self, echo_timeout: float) -> None:
        """
        Function to drop into check echo thread

        In the case of asyncio we just have a coroutine on the loop to check if

        Args:
            echo_timeout: duration to check echo for

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        channel_fd = self.transport._get_channel_fd()  # pylint: disable=W0212
        start = datetime.now().timestamp()
        while True:
            fd_ready, _, _ = select([channel_fd], [], [], 0)
            if channel_fd in fd_ready:
                self._server_echo = True
                break
            interval_end = datetime.now().timestamp()
            if (interval_end - start) > echo_timeout:
                self._server_echo = False
                break

    def _check_echo(self, timeout_transport: float) -> None:
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
             timeout_transport: transport timeout value to modify to use as timeout to test echo

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        if isinstance(self.transport, NetconfSystemSSHTransport):
            self._server_echo = True
            return
        pool = ThreadPoolExecutor(max_workers=1)
        pool.submit(self.__check_echo, timeout_transport / 20)

    @OperationTimeout(
        "timeout_ops",
        "Timed out determining if session is authenticated/getting server capabilities",
    )
    def _get_server_capabilities(self, login_bytes: bytes) -> bytes:
        """
        Read until all server capabilities have been sent by server

        Args:
            login_bytes: bytes captured during authentication

        Returns:
            bytes: raw bytes containing server capabilities

        Raises:
            N/A

        """
        with self.session_lock:
            output = login_bytes
            while b"]]>]]>" not in output:
                output += self.transport.read()
            self.logger.debug(f"Received raw server capabilities: {repr(output)}")
        return output

    @OperationTimeout("timeout_ops", "Timed out sending client capabilities")
    def _send_client_capabilities(
        self,
        client_capabilities: NetconfClientCapabilities,
        capabilities_version: NetconfVersion = NetconfVersion.VERSION_1_1,
    ) -> None:
        """
        Send client capabilities to the netconf server

        Args:
            client_capabilities: string of client netconf capabilities to send to server
            capabilities_version: string of client netconf capabilities version, 1.0 or 1.1

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        with self.session_lock:
            bytes_client_capabilities = self._pre_send_client_capabilities(
                client_capabilities=client_capabilities
            )

            # in case of "system" transport we'll always want to read off the hello message inputs
            if self._server_echo is True:
                self._read_until_input(bytes_client_capabilities)

            self._send_return()
            self._post_send_client_capabilities(capabilities_version=capabilities_version)

            while self._server_echo is None:
                pass

    def _read_until_input(self, channel_input: bytes, auto_expand: Optional[bool] = None) -> bytes:
        """
        Async read until all input has been entered.

        Args:
            channel_input: string to write to channel
            auto_expand: bool to indicate if a device auto-expands commands, for example juniper
                devices without `cli complete-on-space` disabled will convert `config` to
                `configuration` after entering a space character after `config`; because scrapli
                reads the channel until each command is entered, the command changing from `config`
                to `configuration` will cause scrapli (by default) to never think the command has
                been entered.

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

        if auto_expand is None:
            auto_expand = self.comms_auto_expand

        while True:
            output += self._read_chunk()

            if not auto_expand and channel_input in output:
                break
            if auto_expand and self._process_auto_expand(
                output=output, channel_input=channel_input
            ):
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

        raw_result, _ = super().send_input(
            channel_input=final_channel_input, strip_prompt=False, eager=True
        )

        if bytes_final_channel_input in raw_result:
            raw_result = raw_result.split(bytes_final_channel_input)[1]

        raw_result = self._read_until_prompt(output=raw_result)

        if self.netconf_version == NetconfVersion.VERSION_1_1:
            # netconf 1.1 with "chunking" style message format needs an extra return char here
            self._send_return()

        return raw_result
