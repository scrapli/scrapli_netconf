"""scrapli_netconf.channel.base_channel"""
from scrapli.channel.base_channel import ChannelBase
from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.driver.base_driver import NetconfClientCapabilities


class NetconfChannelBase(ChannelBase):
    netconf_version: NetconfVersion

    def _restructure_output(self, output: bytes, strip_prompt: bool = False) -> bytes:
        """
        Override scrapli _restructure_output as this is unnecessary for scrapli_netconf

        Args:
            output: bytes from channel
            strip_prompt: ignored in this base class; for LSP reasons for subclasses

        Returns:
            bytes: output of joined output lines optionally with prompt removed

        Raises:
            N/A

        """
        _ = strip_prompt
        return output

    def _build_message(self, channel_input: str) -> str:
        """
        Build formatted message to send to netconf server

        Args:
            channel_input: string of the base xml message to send to netconf server

        Returns:
            str: string of formatted message to send to netconf server

        Raises:
            N/A

        """
        if self.netconf_version == NetconfVersion.VERSION_1_1:
            msg_template = "#{}\n{}\n##"
            # format message for chunk message types
            final_channel_input = msg_template.format(len(channel_input), channel_input)
            return final_channel_input

        # some (vMX for some reason?) devices seem to get carried away if there are *any* returns in
        # the input... this causes the server to output the rpc result which breaks the normal
        # scrapli "read_until_input" behavior, so we'll simply remove new lines in channel inputs
        return channel_input.replace("\n", "")

    def _pre_send_client_capabilities(
        self, client_capabilities: NetconfClientCapabilities
    ) -> bytes:
        """
        Handle pre "_send_client_capabilities" tasks for consistency between sync/async versions

        Args:
            client_capabilities: string of client netconf capabilities to send to server

        Returns:
            bytes: bytes of client capabilities to send to the channel

        Raises:
            N/A

        """
        self.logger.info("Sending client capabilities")
        bytes_client_capabilities: bytes = client_capabilities.value.encode().strip()
        self.logger.debug(f"Attempting to send capabilities: {client_capabilities}")
        self.transport.write(client_capabilities.value)
        self.logger.debug(f"Write: {repr(client_capabilities.value)}")
        return bytes_client_capabilities

    def _post_send_client_capabilities(
        self, capabilities_version: NetconfVersion = NetconfVersion.VERSION_1_1
    ) -> None:
        """
        Handle pre "_send_client_capabilities" tasks for consistency between sync/async versions

        Args:
            capabilities_version: string of client netconf capabilities version, 1.0 or 1.1

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        if capabilities_version == NetconfVersion.VERSION_1_1:
            self.netconf_version = NetconfVersion.VERSION_1_1
            self.comms_prompt_pattern = r"^##$"
