"""scrapli_netconf.driver.sync_driver"""

from typing import Any, Callable, Dict, List, Optional, Union

from lxml.etree import _Element

from scrapli import Driver
from scrapli_netconf.channel.base_channel import NetconfBaseChannelArgs
from scrapli_netconf.channel.sync_channel import NetconfChannel
from scrapli_netconf.driver.base_driver import NetconfBaseDriver
from scrapli_netconf.response import NetconfResponse


class NetconfDriver(Driver, NetconfBaseDriver):
    # kinda hate this but need to tell mypy that channel in netconf land is in fact a channel of
    # type `NetconfChannel`
    channel: NetconfChannel

    def __init__(  # pylint: disable=R0917
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
        ssh_config_file: Union[str, bool] = False,
        ssh_known_hosts_file: Union[str, bool] = False,
        on_init: Optional[Callable[..., Any]] = None,
        on_open: Optional[Callable[..., Any]] = None,
        on_close: Optional[Callable[..., Any]] = None,
        transport: str = "system",
        transport_options: Optional[Dict[str, Any]] = None,
        channel_log: Union[str, bool] = False,
        channel_lock: bool = False,
        preferred_netconf_version: Optional[str] = None,
        use_compressed_parser: bool = True,
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

        _preferred_netconf_version = self._determine_preferred_netconf_version(
            preferred_netconf_version=preferred_netconf_version
        )
        _preferred_xml_parser = self._determine_preferred_xml_parser(
            use_compressed_parser=use_compressed_parser
        )
        self._netconf_base_channel_args = NetconfBaseChannelArgs(
            netconf_version=_preferred_netconf_version, xml_parser=_preferred_xml_parser
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
            filter_: filter to apply to the get
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
        filter_: Optional[str] = None,
        filter_type: str = "subtree",
        default_type: Optional[str] = None,
    ) -> NetconfResponse:
        """
        Netconf get-config operation

        Args:
            source: configuration source to get; typically one of running|startup|candidate
            filter_: string of filter(s) to apply to configuration
            filter_type: type of filter; subtree|xpath
            default_type: string of with-default mode to apply when retrieving configuration

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_get_config(
            source=source, filter_=filter_, filter_type=filter_type, default_type=default_type
        )
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

    def commit(
        self,
        confirmed: bool = False,
        timeout: Optional[int] = None,
        persist: Optional[Union[int, str]] = None,
        persist_id: Optional[Union[int, str]] = None,
    ) -> NetconfResponse:
        """
        Netconf commit config operation

        Args:
            confirmed: whether this is a confirmed commit
            timeout: specifies the confirm timeout in seconds
            persist: make the confirmed commit survive a session termination, and set a token on
                the ongoing confirmed commit
            persist_id: value must be equal to the value given in the <persist> parameter to the
                original <commit> operation.

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_commit(
            confirmed=confirmed,
            timeout=timeout,
            persist=persist,
            persist_id=persist_id,
        )
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

    def rpc(self, filter_: Union[str, _Element]) -> NetconfResponse:
        """
        Netconf "rpc" operation

        Typically used with juniper devices or if you want to build/send your own payload in a more
        manual fashion. You can provide a string that will be loaded as an lxml element, or you can
        provide an lxml element yourself.

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

    def copy_config(self, source: str, target: str) -> NetconfResponse:
        """
        Netconf "copy-config" operation

        Args:
            source: configuration, url, or datastore to copy into the target datastore
            target: destination to copy the source to

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        response = self._pre_copy_config(source=source, target=target)
        raw_response = self.channel.send_input_netconf(response.channel_input)
        response.record_response(raw_response)
        return response
