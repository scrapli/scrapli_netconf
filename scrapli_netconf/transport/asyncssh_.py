"""scrapli_netconf.transport.asyncssh_"""
from typing import Any

from scrapli_asyncssh.transport.asyncssh_ import AsyncSSHTransport

from scrapli.exceptions import ConnectionNotOpened


# no stubs for scrapli_asyncssh for now, ignore strict typing complains
class NetconfAsyncSSHTransport(AsyncSSHTransport):  # type: ignore
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    async def open_netconf(self) -> bytes:
        """
        Netconf open method

        Args:
            N/A

        Returns:
            bytes: bytes output from server captured while opening the connection

        Raises:
            N/A

        """
        from asyncssh.misc import ChannelOpenError  # pylint: disable=C0415

        if self.auth_strict_key:
            self.logger.debug(f"Attempting to validate {self.host} public key is in known hosts")
            self._verify_key()

        await self._authenticate()

        if self.auth_strict_key:
            self.logger.debug(
                f"Attempting to validate {self.host} public key is in known hosts and is valid"
            )
            self._verify_key_value()

        # it seems we must pass a terminal type to force a pty(?) which i think we want in like...
        # every case?? https://invisible-island.net/ncurses/ncurses.faq.html#xterm_color
        # set encoding to None so we get bytes for consistency w/ other scrapli transports
        # request_pty seems to be safe to set to "false" but leaving it at auto which seems closer
        # to the default behavior. With this omitted (as was previously) connecting to junos devices
        # on port 830 worked w/ system transport but *not* asyncssh because the pty request failed
        try:
            self.stdin, self.stdout, self.stderr = await self.session.open_session(
                term_type="xterm", encoding=None, subsystem="netconf", request_pty="auto"
            )
        except ChannelOpenError as exc:
            msg = (
                "Failed to open Channel -- do you have the right port? Most often the netconf "
                "port is 22 or 830!"
            )
            self.logger.critical(msg)
            raise ConnectionNotOpened(msg) from exc

        return b""

    def _keepalive_network(self) -> None:
        """
        Override _keepalive_network from scrapli; not supported with netconf

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            NotImplementedError: always for now...

        """
        raise NotImplementedError("`network` style keepalives not supported with netconf")

    def _keepalive_standard(self) -> None:
        """
        Send "out of band" (protocol level) keepalives to devices.

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            NotImplementedError: always for now...

        """
        raise NotImplementedError("keepalives not yet implemented")
