"""scrapli_netconf.transport.plugins.system.transport"""

from io import BytesIO

from scrapli.exceptions import ScrapliConnectionNotOpened
from scrapli.transport.base import BaseTransportArgs
from scrapli.transport.plugins.system.transport import PluginTransportArgs, SystemTransport

# imported from base driver
_ = PluginTransportArgs


class NetconfSystemTransport(SystemTransport):
    def __init__(
        self, base_transport_args: BaseTransportArgs, plugin_transport_args: PluginTransportArgs
    ):
        self.write_chunk_size = 65535
        super().__init__(
            base_transport_args=base_transport_args, plugin_transport_args=plugin_transport_args
        )

    def _build_open_cmd(self) -> None:
        super()._build_open_cmd()

        # JunOS devices do not allocate pty on port 830 on some (all?) platforms, users can cause
        # system transport to *not* force the pty (forcing pty is *default behavior*) by setting the
        # transport arg `netconf_force_pty` to `False`. This defaults to `True` (forcing a pty) as
        # that has been the default behavior for a while and seems to work in almost all cases,
        # additionally without this -- in pytest (only in pytest for some reason?) output seems to
        # come from devices out of order causing all the echo check logic to break... with this pty
        # being forced that seems to never occur. Worth digging into more at some point...
        if self._base_transport_args.transport_options.get("netconf_force_pty", True) is True:
            self.open_cmd.append("-tt")

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

    def write(self, channel_input: bytes) -> None:
        if not self.session:
            raise ScrapliConnectionNotOpened

        if self.write_chunk_size <= 0:
            self.session.write(channel_input)
        else:
            bytes_to_send_len = len(channel_input)
            bytes_to_send = BytesIO(channel_input)
            bytes_sent = 0

            while bytes_sent < bytes_to_send_len:
                self.session.write(bytes_to_send.read(self.write_chunk_size))
                bytes_sent += self.write_chunk_size
