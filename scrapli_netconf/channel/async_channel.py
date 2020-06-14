"""scrapli_netconf.channel.async_channel"""
from typing import Any, Optional

from scrapli.channel import AsyncChannel
from scrapli.decorators import operation_timeout
from scrapli.transport.async_transport import AsyncTransport
from scrapli_netconf.channel.base_channel import NetconfChannelBase
from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.driver.base_driver import NetconfClientCapabilities


class AsyncNetconfChannel(AsyncChannel, NetconfChannelBase):
    def __init__(self, transport: AsyncTransport, **kwargs: Any):
        # pop the comms prompt pattern out; always use `]]>]]>` as the initial prompt to match
        kwargs.pop("comms_prompt_pattern")
        super().__init__(transport=transport, comms_prompt_pattern="]]>]]>", **kwargs)

        self.netconf_version = NetconfVersion.VERSION_1_0

    @operation_timeout(
        "timeout_ops",
        "Timed out determining if session is authenticated/getting server capabilities",
    )
    async def _get_server_capabilities(self, login_bytes: bytes) -> bytes:
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
        while b"]]>]]>" not in output:
            output += await self.transport.read()
        self.logger.debug(f"Received raw server capabilities: {repr(output)}")
        self.transport.session_lock.release()
        return output

    @operation_timeout("timeout_ops", "Timed out sending client capabilities")
    async def _send_client_capabilities(
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
        bytes_client_capabilities = self._pre_send_client_capabilities(
            client_capabilities=client_capabilities
        )
        await self._read_until_input(bytes_client_capabilities)
        self._send_return()
        self._post_send_client_capabilities(capabilities_version=capabilities_version)

    async def _read_until_input(
        self, channel_input: bytes, auto_expand: Optional[bool] = None
    ) -> bytes:
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
        #
        # if not channel_input:
        #     self.logger.info(f"Read: {repr(output)}")
        #     return output
        #
        # if auto_expand is None:
        #     auto_expand = self.comms_auto_expand
        #
        # while True:
        #     output += await self._read_chunk()
        #
        #     if not auto_expand and channel_input in output:
        #         break
        #     if auto_expand and self._process_auto_expand(
        #         output=output, channel_input=channel_input
        #     ):
        #         break
        #
        # self.logger.info(f"Read: {repr(output)}")
        return output

    async def send_input_netconf(self, channel_input: str) -> str:
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

        raw_result, _ = await super().send_input(
            channel_input=final_channel_input, strip_prompt=False
        )

        if self.netconf_version == NetconfVersion.VERSION_1_1:
            # netconf 1.1 with "chunking" style message format needs an extra return char here
            self._send_return()

        return raw_result
