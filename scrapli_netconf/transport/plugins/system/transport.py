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
