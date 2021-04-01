"""scrapli_netconf.transport.plugins.system.transport"""
from scrapli.transport.plugins.system.transport import PluginTransportArgs, SystemTransport

# imported from base driver
_ = PluginTransportArgs


class NetconfSystemTransport(SystemTransport):
    def _build_open_cmd(self) -> None:
        super()._build_open_cmd()
        # adding `-tt` forces tty allocation which lets us send a string greater than 1024 chars;
        # without this we are basically capped at 1024 chars and scrapli will/the connection will
        # die. it *may* be possible to alter ptyprocess vendor'd code to add `stty -icanon` which
        # should also have a similar affect, though this seems simpler.
        self.open_cmd.extend(["-tt"])
        self.open_cmd.extend(["-s", "netconf"])
        self.logger.debug(f"final open_cmd: {self.open_cmd}")

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
        self.open()

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
        channel_fd: int = self.session.fd
        return channel_fd
