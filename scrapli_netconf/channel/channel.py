"""scrapli_netconf.channel.channel"""
from logging import getLogger
from typing import Any

from scrapli.channel import Channel
from scrapli.decorators import operation_timeout
from scrapli.transport import Transport

LOG = getLogger("channel")


class NetconfChannel(Channel):
    def __init__(self, transport: Transport, **kwargs: Any):
        # pop the comms prompt pattern out; always use `]]>]]>` as the initial prompt to match
        kwargs.pop("comms_prompt_pattern")
        super().__init__(transport, comms_prompt_pattern="]]>]]>", **kwargs)

        self.netconf_version = "1.0"

    def _restructure_output(self, output: bytes, strip_prompt: bool = False) -> bytes:
        """
        Override scrapli _restructure_output as this is unnecessary for scrapli_netconf

        Args:
            output: bytes from channel
            strip_prompt: bool True/False whether to strip prompt or not

        Returns:
            bytes: output of joined output lines optionally with prompt removed

        Raises:
            N/A

        """
        return output

    @operation_timeout(
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
        self.transport.session_lock.acquire()
        output = login_bytes
        while True:
            output += self.transport.read()
            if b"]]>]]>" in output:
                LOG.debug(f"Received raw server capabilities: {repr(output)}")
                self.transport.session_lock.release()
                return output

    @operation_timeout("timeout_ops", "Timed out sending client capabilities")
    def _send_client_capabilities(
        self, client_capabilities: str, capabilities_version: str = "1.1"
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
        LOG.info("Sending client capabilities")
        self.transport.session_lock.acquire()
        bytes_client_capabilities = client_capabilities.encode().strip()
        LOG.debug(f"Attempting to send capabilities: {client_capabilities}")
        self.transport.write(client_capabilities)
        LOG.debug(f"Write: {repr(client_capabilities)}")
        self._read_until_input(bytes_client_capabilities)
        self._send_return()

        if capabilities_version == "1.1":
            self.netconf_version = "1.1"
            self.comms_prompt_pattern = r"^##$"

        self.transport.session_lock.release()

    def _build_message(self, channel_input: bytes) -> str:
        """
        Build formatted message to send to netconf server

        Args:
            channel_input: string of the base xml message to send to netconf server

        Returns:
            str: string of formatted message to send to netconf server

        Raises:
            N/A

        """
        if self.netconf_version == "1.1":
            msg_template = "#{}\n{}\n##"
            # format message for chunk message types
            final_channel_input = msg_template.format(len(channel_input), channel_input.decode())
            return final_channel_input
        return channel_input.decode()

    def send_input_netconf(self, channel_input: bytes) -> str:
        """
        Send inputs to netconf server

        Args:
            channel_input: string of the base xml message to send to netconf server

        Returns:
            str: string result of message sent to netconf server

        Raises:
            N/A

        """
        final_channel_input = self._build_message(channel_input)

        raw_result, _ = super().send_input(channel_input=final_channel_input, strip_prompt=False)

        if self.netconf_version == "1.1":
            # netconf 1.1 with "chunking" style message format needs an extra return char here
            self._send_return()

        return raw_result
