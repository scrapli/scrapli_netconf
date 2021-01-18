"""scrapli_netconf.transport.plugins.paramiko.transport"""
from scrapli.exceptions import ScrapliConnectionNotOpened
from scrapli.transport.plugins.paramiko.transport import ParamikoTransport, PluginTransportArgs

# imported from base driver
_ = PluginTransportArgs


class NetconfParamikoTransport(ParamikoTransport):
    def open_netconf(self) -> None:
        """
        Netconf open method

        Simply calls the "normal" open method, but retaining an explicit "netconf" open for sanity

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        super().open()

    def _open_channel(self) -> None:
        """
        Overriding the base open_channel to invoke netconf subsystem

        Args:
            N/A

        Returns:
            None

        Raises:
            ScrapliConnectionNotOpened: if session is unopened/None

        """
        if not self.session:
            raise ScrapliConnectionNotOpened

        self.session_channel = self.session.open_session()
        self._set_timeout(self._base_transport_args.timeout_transport)
        # unlike "normal" paramiko -- we do *not* need to enable the "shell" on the channel...
        # we *do* still want it to be a pty though!
        self.session_channel.get_pty()
        self.session_channel.invoke_subsystem("netconf")

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
        channel_fd: int = self.session_channel.fileno()
        return channel_fd
