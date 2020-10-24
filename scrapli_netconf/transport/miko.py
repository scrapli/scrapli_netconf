"""scrapli_netconf.transport.miko"""
from typing import Any

from scrapli_paramiko.transport.miko import MikoTransport


# no stubs for scrapli_paramiko for now, ignore strict typing complains
class NetconfMikoTransport(MikoTransport):  # type: ignore
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def open_netconf(self) -> bytes:
        """
        TODO

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            X

        """
        super().open()

        return b""

    def _open_channel(self) -> None:
        """
        TODO

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            X

        """
        self.channel = self.session.open_session()
        # unlike "normal" paramiko -- we do *not* need to enable the "shell" on the channel...
        # we *do* still want it to be a pty though!
        self.channel.get_pty()
        self.channel.invoke_subsystem("netconf")

    def _get_channel_fd(self) -> int:
        """
        Function to get the fd to check for "echo" with

        Args:
             N/A

        Returns:
            int: fd of the channel

        Raises:
            N/A

        """
        channel_fd: int = self.channel.fileno()
        return channel_fd
