"""scrapli_netconf.transport.plugins.ssh2.transport"""

from scrapli.exceptions import ScrapliConnectionNotOpened
from scrapli.transport.plugins.ssh2.transport import PluginTransportArgs, Ssh2Transport

# imported from base driver
_ = PluginTransportArgs


class NetconfSsh2Transport(Ssh2Transport):
    def open_netconf(self) -> bytes:
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

        return b""

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
        self.session_channel.subsystem("netconf")
