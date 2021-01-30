"""scrapli_netconf.driver.sync_driver"""
from typing import Any, Callable, Dict, List, Optional, Union
from warnings import warn

from scrapli import Driver
from scrapli_netconf.channel.base_channel import NetconfBaseChannelArgs
from scrapli_netconf.channel.sync_channel import NetconfChannel
from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.driver.base_driver import NetconfBaseDriver
from scrapli_netconf.response import NetconfResponse


class NetconfDriver(Driver, NetconfBaseDriver):
    def __init__(
        self,
        host: str,
        port: int = 830,
        strip_namespaces: bool = False,
        strict_datastores: bool = False,
        auth_username: str = "",
        auth_password: str = "",
        auth_private_key: str = "",
        auth_private_key_passphrase: str = "",
        auth_strict_key: bool = True,
        auth_bypass: bool = False,
        timeout_socket: float = 15.0,
        timeout_transport: float = 30.0,
        timeout_ops: float = 30.0,
        comms_prompt_pattern: str = r"^[a-z0-9.\-@()/:]{1,48}[#>$]\s*$",
        comms_return_char: str = "\n",
        comms_ansi: bool = False,
        ssh_config_file: Union[str, bool] = False,
        ssh_known_hosts_file: Union[str, bool] = False,
        on_init: Optional[Callable[..., Any]] = None,
        on_open: Optional[Callable[..., Any]] = None,
        on_close: Optional[Callable[..., Any]] = None,
        transport: str = "system",
        transport_options: Optional[Dict[str, Any]] = None,
        channel_log: Union[str, bool] = False,
        channel_lock: bool = False,
    ) -> None:
        super().__init__(
            host=host,
            port=port,
            auth_username=auth_username,
            auth_password=auth_password,
            auth_private_key=auth_private_key,
            auth_private_key_passphrase=auth_private_key_passphrase,
            auth_strict_key=auth_strict_key,
            auth_bypass=auth_bypass,
            timeout_socket=timeout_socket,
            timeout_transport=timeout_transport,
            timeout_ops=timeout_ops,
            comms_prompt_pattern=comms_prompt_pattern,
            comms_return_char=comms_return_char,
            comms_ansi=comms_ansi,
            ssh_config_file=ssh_config_file,
            ssh_known_hosts_file=ssh_known_hosts_file,
            on_init=on_init,
            on_open=on_open,
            on_close=on_close,
            transport=transport,
            transport_options=transport_options,
            channel_log=channel_log,
            channel_lock=channel_lock,
        )
        self._netconf_base_channel_args = NetconfBaseChannelArgs(
            netconf_version=NetconfVersion.UNKNOWN
        )
        self.channel = NetconfChannel(
            transport=self.transport,
            base_channel_args=self._base_channel_args,
            netconf_base_channel_args=self._netconf_base_channel_args,
        )

        self.strip_namespaces = strip_namespaces
        self.strict_datastores = strict_datastores
        self.server_capabilities: List[str] = []
        self.readable_datastores: List[str] = []
        self.writeable_datastores: List[str] = []
        self.message_id = 101

    def open(self) -> None:
        """
        Open netconf connection to server

        Args:
            N/A

        Returns:
            None

        Raises:
            N/A

        """
        self._pre_open_closing_log(closing=False)

        self.transport.open_netconf()

        # in the future this and scrapli core should just have a class attribute of the transports
        # that require this "in channel" auth so we can dynamically figure that out rather than
        # just look at the name of the transport
        if "system" in self.transport_name:
            self.channel.channel_authenticate_netconf(
                auth_password=self.auth_password,
                auth_private_key_passphrase=self.auth_private_key_passphrase,
            )

        self.channel.open_netconf()

        self._build_readable_datastores()
        self._build_writeable_datastores()

        self._post_open_closing_log(closing=False)

    def get(self, filter_: str, filter_type: str = "subtree") -> NetconfResponse:
        """
        Netconf get operation

        Args:
            filter_: string filter to apply to the get
            filter_type: type of filter; subtree|xpath

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_get(filter_=filter_, filter_type=filter_type)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def get_config(
        self,
        source: str = "running",
        filters: Optional[Union[str, List[str]]] = None,
        filter_type: str = "subtree",
    ) -> NetconfResponse:
        """
        Netconf get-config operation

        Args:
            source: configuration source to get; typically one of running|startup|candidate
            filters: string or list of strings of filters to apply to configuration
            filter_type: type of filter; subtree|xpath

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_get_config(source=source, filters=filters, filter_type=filter_type)
        raw_response = self.channel.send_input_netconf(response.channel_input)

        response.record_response(raw_response)
        return response

    def edit_config(self, config: str, target: str = "running") -> NetconfResponse:
        """
        Netconf get-config operation

        Args:
            config: configuration to send to device
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_edit_config(config=config, target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def delete_config(self, target: str = "candidate") -> NetconfResponse:
        """
        Netconf delete-config operation

        Args:
            target: configuration source to target; startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_delete_config(target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def commit(self) -> NetconfResponse:
        """
        Netconf commit config operation

        Args:
            N/A

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_commit()
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def discard(self) -> NetconfResponse:
        """
        Netconf discard config operation

        Args:
            N/A

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_discard()
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def lock(self, target: str) -> NetconfResponse:
        """
        Netconf lock operation

        Args:
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_lock(target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def unlock(self, target: str) -> NetconfResponse:
        """
        Netconf unlock operation

        Args:
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_unlock(target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def rpc(self, filter_: str) -> NetconfResponse:
        """
        Netconf "rpc" operation; typically only used with juniper devices

        You can also use this to build send your own payload in a more manual fashion

        Args:
            filter_: filter/rpc to execute

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_rpc(filter_=filter_)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response

    def validate(self, source: str) -> NetconfResponse:
        """
        Netconf "validate" operation

        Args:
            source: configuration source to validate; typically one of running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_validate(source=source)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response


# remove in future releases, retaining this to not break end user scripts for now
class NetconfScrape(NetconfDriver):
    warning = (
        "`NetconfScrape` has been renamed `NetconfDriver`, `NetconfScrape` will be deprecated in "
        "future releases!"
    )

    def __init_subclass__(cls):
        """Deprecate NetconfScrape"""
        warn(cls.warning, DeprecationWarning, 2)

    def __new__(cls, *args, **kwargs):
        warn(cls.warning, DeprecationWarning, 2)
        return NetconfDriver(*args, **kwargs)
