"""scrapli_netconf.transport.plugins.system.transport"""
from scrapli.transport.plugins.system.transport import PluginTransportArgs, SystemTransport

# imported from base driver
_ = PluginTransportArgs


class NetconfSystemTransport(SystemTransport):
    def _build_open_cmd(self) -> None:
        super()._build_open_cmd()
        self.open_cmd.extend(["-s", "netconf"])

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
