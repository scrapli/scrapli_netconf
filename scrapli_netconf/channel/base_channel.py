"""scrapli_netconf.channel.base_channel"""
import re
from dataclasses import dataclass
from typing import List, Optional

from lxml import etree

from scrapli.channel.base_channel import BaseChannel
from scrapli_netconf.constants import NetconfClientCapabilities, NetconfVersion
from scrapli_netconf.exceptions import CouldNotExchangeCapabilities


@dataclass()
class NetconfBaseChannelArgs:
    netconf_version: NetconfVersion
    server_capabilities: Optional[List[str]] = None
    client_capabilities: NetconfClientCapabilities = NetconfClientCapabilities.UNKNOWN


class BaseNetconfChannel(BaseChannel):
    _netconf_base_channel_args: NetconfBaseChannelArgs

    def _process_capabilities_exchange(self, raw_server_capabilities: bytes) -> None:
        """
        Process received capabilities; return client capabilities

        Args:
            raw_server_capabilities: raw bytes containing server capabilities

        Returns:
            None

        Raises:
            N/A

        """
        server_capabilities = self._parse_server_capabilities(
            raw_server_capabilities=raw_server_capabilities
        )

        if "urn:ietf:params:netconf:base:1.1" in server_capabilities:
            client_capabilities = NetconfClientCapabilities.CAPABILITIES_1_1
            self._netconf_base_channel_args.netconf_version = NetconfVersion.VERSION_1_1
            self._base_channel_args.comms_prompt_pattern = r"^##$"
        else:
            client_capabilities = NetconfClientCapabilities.CAPABILITIES_1_0
            self._netconf_base_channel_args.netconf_version = NetconfVersion.VERSION_1_0
            self._base_channel_args.comms_prompt_pattern = "]]>]]>"

        self._netconf_base_channel_args.server_capabilities = server_capabilities
        self._netconf_base_channel_args.client_capabilities = client_capabilities

    def _parse_server_capabilities(self, raw_server_capabilities: bytes) -> List[str]:
        """
        Parse netconf server capabilities

        Args:
            raw_server_capabilities: raw bytes containing server capabilities

        Returns:
            N/A  # noqa: DAR202

        Raises:
            CouldNotExchangeCapabilities: if server capabilities cannot be parsed

        """
        server_capabilities = []

        # matches hello with or without namespace
        filtered_raw_server_capabilities = re.search(
            pattern=rb"(<(\w+\:){0,1}hello.*<\/(\w+\:){0,1}hello>)",
            string=raw_server_capabilities,
            flags=re.I | re.S,
        )
        if filtered_raw_server_capabilities is None:
            msg = "failed to parse server capabilities"
            raise CouldNotExchangeCapabilities(msg)
        server_capabilities_xml = etree.fromstring(filtered_raw_server_capabilities.groups()[0])
        for elem in server_capabilities_xml.iter():
            if "capability" not in elem.tag:
                continue
            server_capabilities.append(elem.text.strip())
        self.logger.info(f"server capabilities received and parsed: {server_capabilities}")
        return server_capabilities

    def _process_output(self, buf: bytes, strip_prompt: bool) -> bytes:
        """
        Override scrapli _process_output as this is unnecessary for scrapli_netconf

        Args:
            buf: bytes output from the device
            strip_prompt: ignored in this base class; for LSP reasons for subclasses

        Returns:
            bytes: output of joined output lines optionally with prompt removed

        Raises:
            N/A

        """
        _ = strip_prompt
        return buf

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
        if self._netconf_base_channel_args.netconf_version == NetconfVersion.VERSION_1_0:
            return channel_input

        # format message for chunk (netconf 1.1) style message
        msg_template = "#{}\n{}\n##"
        final_channel_input = msg_template.format(len(channel_input), channel_input)
        return final_channel_input

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
        self.write(client_capabilities.value)
        self.logger.debug(f"Write: {repr(client_capabilities.value)}")
        return bytes_client_capabilities
