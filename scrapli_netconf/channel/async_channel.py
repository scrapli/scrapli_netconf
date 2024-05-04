"""scrapli_netconf.channel.async_channel"""

from scrapli.channel import AsyncChannel
from scrapli.channel.base_channel import BaseChannelArgs
from scrapli.decorators import timeout_wrapper
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
        self._establishing_server_echo = False
        self._capabilities_buf = b""
        self._read_buf = b""

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
        # open in scrapli core is where we open channel log (if applicable), do that
        self.open()

        raw_server_capabilities = await self._get_server_capabilities()
        self._process_capabilities_exchange(raw_server_capabilities=raw_server_capabilities)
        await self._send_client_capabilities()

    @timeout_wrapper
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

        async with self._channel_lock():
            while b"]]>]]>" not in capabilities_buf:
                capabilities_buf += await self.read()
            self.logger.debug(f"received raw server capabilities: {repr(capabilities_buf)}")
        return capabilities_buf

    @timeout_wrapper
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
        async with self._channel_lock():
            _ = self._pre_send_client_capabilities(
                client_capabilities=self._netconf_base_channel_args.client_capabilities
            )
            self.send_return()

    async def read(self) -> bytes:
        """
        Read chunks of output from the channels

        Prior to doing "normal" scrapli read things (*), check if there is anything on our read_buf,
        if there is, return that first. Historically this actually did do "normal" scrapli read
        things by super-ing read, but, "normal" scrapli replaces \r it finds in output which can
        cause nc1.1 chunk parsing to fail since we've removed some chars that were counted as part
        of the chunk. so, now we just copypasta the normal read things here without that .replace,
        and no longer super.

        Note that to *not* have the \r in output from system transport you will need >=2024.07.30
        scrapli version, but replacing the super-ing with this sorts out other transports!

        Args:
            N/A

        Returns:
            bytes: output read from channel

        Raises:
            N/A

        """
        if self._read_buf:
            read_buf = self._read_buf
            self._read_buf = b""
            return read_buf

        buf = await self.transport.read()

        self.logger.debug(f"read: {buf!r}")

        if self.channel_log:
            self.channel_log.write(buf)

        if b"\x1b" in buf.lower():
            buf = self._strip_ansi(buf=buf)

        return buf

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

        if self._server_echo is None or self._server_echo is False:
            # if server_echo is `None` we dont know if the server echoes yet, so just return nothing
            # if its False we know it doesnt echo and we can return empty byte string anyway
            return output

        if not channel_input:
            self.logger.info(f"Read: {repr(output)}")
            return output

        while True:
            output += await self.read()

            if self._establishing_server_echo:
                output, partition, new_buf = output.partition(b"]]>]]>")
                self._read_buf += new_buf
                output += partition
                break

            # if we have all the input *or* we see the closing rpc tag we know we are done here
            if channel_input in output or b"rpc>" in output:
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
        bytes_final_channel_input = channel_input.encode()

        buf: bytes
        buf, _ = await super().send_input(
            channel_input=channel_input, strip_prompt=False, eager=True
        )

        if bytes_final_channel_input in buf:
            buf = buf.split(bytes_final_channel_input)[1]

        buf = await self._read_until_prompt(buf=buf)

        if self._server_echo is None:
            # At least per early drafts of the netconf over ssh rfcs the netconf servers MUST NOT
            # echo the input commands back to the client. In the case of "normal" scrapli netconf
            # with the system transport this happens anyway because we combine the stdin and stdout
            # fds into a single pty, however for other transports we have an actual stdin and
            # stdout fd to read/write. It seems that at the very least IOSXE with NETCONF 1.1 seems
            # to want to echo inputs back onto to the stdout for the channel. This is totally ok
            # and we can deal with it, we just need to *know* that it is happening, so while the
            # _server_echo attribute is still `None`, we can go ahead and see if the input we sent
            # is in the output we read off the channel. If it is *not* we know the server does *not*
            # echo and we can move on. If it *is* in the output, we know the server echoes, and we
            # also have one additional step in that we need to read "until prompt" again in order to
            # capture the reply to our rpc.
            #
            # See: https://tools.ietf.org/html/draft-ietf-netconf-ssh-02 (search for "echo")

            self.logger.debug("server echo is unset, determining if server echoes inputs now")

            # we may be reading the remainder of the echo from our capabilities message -- if we see
            # that we know the server echoes, but we still need to read until our latest input.
            if b"</hello>]]>]]>" in buf:
                self.logger.debug("server echoes inputs, setting _server_echo to 'true'")
                self._server_echo = True

                _, _, buf = buf.partition(b"</hello>]]>]]>")
                if buf:
                    # if we read past the end of the
                    self._read_buf += buf

                # read up till our new input now to consume it from the channel
                self._establishing_server_echo = True
                await self._read_until_input(bytes_final_channel_input)
            elif bytes_final_channel_input in buf:
                self.logger.debug("server echoes inputs, setting _server_echo to 'true'")
                self._server_echo = True
            else:
                self.logger.debug("server does *not* echo inputs, setting _server_echo to 'false'")
                self._server_echo = False

            if self._server_echo:
                # done with the establishment process
                self._establishing_server_echo = False

                # since echo is True and we only read until our input (because our inputs always end
                # with a "prompt" that we read until) we need to once again read until prompt, this
                # read will read all the way up through the *reply* to the prompt at end of the
                # reply message
                buf = await self._read_until_prompt(buf=b"")

        if self._netconf_base_channel_args.netconf_version == NetconfVersion.VERSION_1_1:
            # netconf 1.1 with "chunking" style message format needs an extra return char here
            self.send_return()

        # we should be able to simply partition here and put any "over reads" back into the read buf

        return buf
