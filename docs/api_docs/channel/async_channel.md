<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_netconf.channel.async_channel

scrapli_netconf.channel.async_channel

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_netconf.channel.async_channel"""
import asyncio

from scrapli.channel import AsyncChannel
from scrapli.channel.base_channel import BaseChannelArgs
from scrapli.decorators import ChannelTimeout
from scrapli.transport.base.async_transport import AsyncTransport
from scrapli_netconf.channel.base_channel import BaseNetconfChannel, NetconfBaseChannelArgs
from scrapli_netconf.constants import NetconfVersion


class AsyncNetconfChannel(AsyncChannel, BaseNetconfChannel):
    def __init__(
        self,
        transport: AsyncTransport,
        base_channel_args: BaseChannelArgs,
        netconf_base_channel_args: NetconfBaseChannelArgs,
    ):
        super().__init__(transport=transport, base_channel_args=base_channel_args)

        self._netconf_base_channel_args = netconf_base_channel_args

        # always use `]]>]]>` as the initial prompt to match
        self._base_channel_args.comms_prompt_pattern = "]]>]]>"
        self._server_echo = False
        self._capabilities_buf = b""

    async def open_netconf(self) -> None:
        """
        Open the netconf channel

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        raw_server_capabilities = await self._get_server_capabilities()

        self._process_capabilities_exchange(raw_server_capabilities=raw_server_capabilities)

        await self._check_echo()
        await self._send_client_capabilities()

    async def _check_echo(self) -> None:
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
        try:
            await asyncio.wait_for(self.read(), timeout=self._base_channel_args.timeout_ops / 20)
            self.logger.info(
                "Determined that server echoes inputs on stdout, setting `_server_echo` to `True`"
            )
            self._server_echo = True
        except asyncio.exceptions.TimeoutError:
            pass
        return

    @ChannelTimeout(
        "timed out determining if session is authenticated/getting server capabilities",
    )
    async def _get_server_capabilities(self) -> bytes:
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

        # not sure why scrapli core is happy w/ the type stubs for all this but scrapli netconf
        # is furious... fix this at some point!
        async with self._channel_lock():  # type: ignore
            while b"]]>]]>" not in capabilities_buf:
                capabilities_buf += await self.read()
            self.logger.debug(f"received raw server capabilities: {repr(capabilities_buf)}")
        return capabilities_buf

    @ChannelTimeout("timed out sending client capabilities")
    async def _send_client_capabilities(
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
        # not sure why scrapli core is happy w/ the type stubs for all this but scrapli netconf
        # is furious... fix this at some point!
        async with self._channel_lock():  # type: ignore
            _ = self._pre_send_client_capabilities(
                client_capabilities=self._netconf_base_channel_args.client_capabilities
            )
            self.send_return()

    async def _read_until_input(self, channel_input: bytes) -> bytes:
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
            output += await self.read()

            if channel_input in output:
                break

        self.logger.info(f"Read: {repr(output)}")
        return output

    async def send_input_netconf(self, channel_input: str) -> bytes:
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

        buf, _ = await super().send_input(
            channel_input=final_channel_input, strip_prompt=False, eager=True
        )

        if bytes_final_channel_input in buf:
            buf = buf.split(bytes_final_channel_input)[1]

        buf = await self._read_until_prompt(buf=buf)

        if self._netconf_base_channel_args.netconf_version == NetconfVersion.VERSION_1_1:
            # netconf 1.1 with "chunking" style message format needs an extra return char here
            self.send_return()

        return buf
        </code>
    </pre>
</details>



## Classes

### AsyncNetconfChannel


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
class AsyncNetconfChannel(AsyncChannel, BaseNetconfChannel):
    def __init__(
        self,
        transport: AsyncTransport,
        base_channel_args: BaseChannelArgs,
        netconf_base_channel_args: NetconfBaseChannelArgs,
    ):
        super().__init__(transport=transport, base_channel_args=base_channel_args)

        self._netconf_base_channel_args = netconf_base_channel_args

        # always use `]]>]]>` as the initial prompt to match
        self._base_channel_args.comms_prompt_pattern = "]]>]]>"
        self._server_echo = False
        self._capabilities_buf = b""

    async def open_netconf(self) -> None:
        """
        Open the netconf channel

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        raw_server_capabilities = await self._get_server_capabilities()

        self._process_capabilities_exchange(raw_server_capabilities=raw_server_capabilities)

        await self._check_echo()
        await self._send_client_capabilities()

    async def _check_echo(self) -> None:
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
        try:
            await asyncio.wait_for(self.read(), timeout=self._base_channel_args.timeout_ops / 20)
            self.logger.info(
                "Determined that server echoes inputs on stdout, setting `_server_echo` to `True`"
            )
            self._server_echo = True
        except asyncio.exceptions.TimeoutError:
            pass
        return

    @ChannelTimeout(
        "timed out determining if session is authenticated/getting server capabilities",
    )
    async def _get_server_capabilities(self) -> bytes:
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

        # not sure why scrapli core is happy w/ the type stubs for all this but scrapli netconf
        # is furious... fix this at some point!
        async with self._channel_lock():  # type: ignore
            while b"]]>]]>" not in capabilities_buf:
                capabilities_buf += await self.read()
            self.logger.debug(f"received raw server capabilities: {repr(capabilities_buf)}")
        return capabilities_buf

    @ChannelTimeout("timed out sending client capabilities")
    async def _send_client_capabilities(
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
        # not sure why scrapli core is happy w/ the type stubs for all this but scrapli netconf
        # is furious... fix this at some point!
        async with self._channel_lock():  # type: ignore
            _ = self._pre_send_client_capabilities(
                client_capabilities=self._netconf_base_channel_args.client_capabilities
            )
            self.send_return()

    async def _read_until_input(self, channel_input: bytes) -> bytes:
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
            output += await self.read()

            if channel_input in output:
                break

        self.logger.info(f"Read: {repr(output)}")
        return output

    async def send_input_netconf(self, channel_input: str) -> bytes:
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

        buf, _ = await super().send_input(
            channel_input=final_channel_input, strip_prompt=False, eager=True
        )

        if bytes_final_channel_input in buf:
            buf = buf.split(bytes_final_channel_input)[1]

        buf = await self._read_until_prompt(buf=buf)

        if self._netconf_base_channel_args.netconf_version == NetconfVersion.VERSION_1_1:
            # netconf 1.1 with "chunking" style message format needs an extra return char here
            self.send_return()

        return buf
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli.channel.async_channel.AsyncChannel
- scrapli_netconf.channel.base_channel.BaseNetconfChannel
- scrapli.channel.base_channel.BaseChannel
#### Methods

    

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