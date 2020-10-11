"""scrapli_netconf.channel.channel"""
from typing import Any

from scrapli.channel import Channel
from scrapli.decorators import OperationTimeout
from scrapli.transport import Transport
from scrapli_netconf.channel.base_channel import NetconfChannelBase
from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.driver.base_driver import NetconfClientCapabilities


class NetconfChannel(Channel, NetconfChannelBase):
    def __init__(self, transport: Transport, **kwargs: Any):
        # pop the comms prompt pattern out; always use `]]>]]>` as the initial prompt to match
        kwargs.pop("comms_prompt_pattern")
        super().__init__(transport, comms_prompt_pattern="]]>]]>", **kwargs)

        self.netconf_version = NetconfVersion.VERSION_1_0

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
            self._read_until_input(bytes_client_capabilities)
            self._send_return()
            self._post_send_client_capabilities(capabilities_version=capabilities_version)

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

        raw_result, _ = super().send_input(channel_input=final_channel_input, strip_prompt=False)

        if self.netconf_version == NetconfVersion.VERSION_1_1:
            # netconf 1.1 with "chunking" style message format needs an extra return char here
            self._send_return()

        return raw_result
