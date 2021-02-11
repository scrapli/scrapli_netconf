<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_netconf.channel.base_channel

scrapli_netconf.channel.base_channel

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_netconf.channel.base_channel"""
import re
from dataclasses import dataclass
from typing import List, Optional

from lxml import etree

from scrapli.channel.base_channel import BaseChannel
from scrapli_netconf.constants import NetconfClientCapabilities, NetconfVersion
from scrapli_netconf.exceptions import CapabilityNotSupported, CouldNotExchangeCapabilities


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
            CapabilityNotSupported: if user has provided a preferred netconf version but it is not
                available in servers offered capabilites

        """
        server_capabilities = self._parse_server_capabilities(
            raw_server_capabilities=raw_server_capabilities
        )
        self._netconf_base_channel_args.server_capabilities = server_capabilities

        if "urn:ietf:params:netconf:base:1.1" in server_capabilities:
            final_channel_version = NetconfVersion.VERSION_1_1
        else:
            final_channel_version = NetconfVersion.VERSION_1_0

        if self._netconf_base_channel_args.netconf_version != NetconfVersion.UNKNOWN:
            if self._netconf_base_channel_args.netconf_version == NetconfVersion.VERSION_1_0:
                if "urn:ietf:params:netconf:base:1.0" not in server_capabilities:
                    raise CapabilityNotSupported(
                        "user requested netconf version 1.0 but capability not offered"
                    )
                final_channel_version = NetconfVersion.VERSION_1_0
            elif self._netconf_base_channel_args.netconf_version == NetconfVersion.VERSION_1_1:
                if "urn:ietf:params:netconf:base:1.1" not in server_capabilities:
                    raise CapabilityNotSupported(
                        "user requested netconf version 1.1 but capability not offered"
                    )
                final_channel_version = NetconfVersion.VERSION_1_1

        if final_channel_version == NetconfVersion.VERSION_1_0:
            self._netconf_base_channel_args.netconf_version = NetconfVersion.VERSION_1_0
            self._base_channel_args.comms_prompt_pattern = "]]>]]>"
            self._netconf_base_channel_args.client_capabilities = (
                NetconfClientCapabilities.CAPABILITIES_1_0
            )
        else:
            self._netconf_base_channel_args.netconf_version = NetconfVersion.VERSION_1_1
            self._base_channel_args.comms_prompt_pattern = r"^##$"
            self._netconf_base_channel_args.client_capabilities = (
                NetconfClientCapabilities.CAPABILITIES_1_1
            )

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
        </code>
    </pre>
</details>



## Classes

### BaseNetconfChannel


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
            CapabilityNotSupported: if user has provided a preferred netconf version but it is not
                available in servers offered capabilites

        """
        server_capabilities = self._parse_server_capabilities(
            raw_server_capabilities=raw_server_capabilities
        )
        self._netconf_base_channel_args.server_capabilities = server_capabilities

        if "urn:ietf:params:netconf:base:1.1" in server_capabilities:
            final_channel_version = NetconfVersion.VERSION_1_1
        else:
            final_channel_version = NetconfVersion.VERSION_1_0

        if self._netconf_base_channel_args.netconf_version != NetconfVersion.UNKNOWN:
            if self._netconf_base_channel_args.netconf_version == NetconfVersion.VERSION_1_0:
                if "urn:ietf:params:netconf:base:1.0" not in server_capabilities:
                    raise CapabilityNotSupported(
                        "user requested netconf version 1.0 but capability not offered"
                    )
                final_channel_version = NetconfVersion.VERSION_1_0
            elif self._netconf_base_channel_args.netconf_version == NetconfVersion.VERSION_1_1:
                if "urn:ietf:params:netconf:base:1.1" not in server_capabilities:
                    raise CapabilityNotSupported(
                        "user requested netconf version 1.1 but capability not offered"
                    )
                final_channel_version = NetconfVersion.VERSION_1_1

        if final_channel_version == NetconfVersion.VERSION_1_0:
            self._netconf_base_channel_args.netconf_version = NetconfVersion.VERSION_1_0
            self._base_channel_args.comms_prompt_pattern = "]]>]]>"
            self._netconf_base_channel_args.client_capabilities = (
                NetconfClientCapabilities.CAPABILITIES_1_0
            )
        else:
            self._netconf_base_channel_args.netconf_version = NetconfVersion.VERSION_1_1
            self._base_channel_args.comms_prompt_pattern = r"^##$"
            self._netconf_base_channel_args.client_capabilities = (
                NetconfClientCapabilities.CAPABILITIES_1_1
            )

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
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli.channel.base_channel.BaseChannel
#### Descendants
- scrapli_netconf.channel.async_channel.AsyncNetconfChannel
- scrapli_netconf.channel.sync_channel.NetconfChannel



### NetconfBaseChannelArgs


```text
NetconfBaseChannelArgs(netconf_version: scrapli_netconf.constants.NetconfVersion, server_capabilities: Union[List[str], NoneType] = None, client_capabilities: scrapli_netconf.constants.NetconfClientCapabilities = <NetconfClientCapabilities.UNKNOWN: 'unknown'>)
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class NetconfBaseChannelArgs:
    netconf_version: NetconfVersion
    server_capabilities: Optional[List[str]] = None
    client_capabilities: NetconfClientCapabilities = NetconfClientCapabilities.UNKNOWN
        </code>
    </pre>
</details>


#### Class variables

    
`client_capabilities: scrapli_netconf.constants.NetconfClientCapabilities`




    
`netconf_version: scrapli_netconf.constants.NetconfVersion`




    
`server_capabilities: Union[List[str], NoneType]`