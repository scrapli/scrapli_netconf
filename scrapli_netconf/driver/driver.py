"""scrapli_netconf.driver.driver"""
from typing import Any, List, Optional, Union

from scrapli import Scrape
from scrapli.exceptions import TransportPluginError
from scrapli_netconf.channel.channel import NetconfChannel
from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.driver.base_driver import NetconfScrapeBase
from scrapli_netconf.response import NetconfResponse
from scrapli_netconf.transport.systemssh import NetconfSystemSSHTransport


class NetconfScrape(Scrape, NetconfScrapeBase):
    def __init__(
        self,
        port: int = 830,
        strip_namespaces: bool = False,
        strict_datastores: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(port=port, **kwargs)

        if self._transport != "system":
            msg = "`NetconfScrape` is only supported using the `system` transport plugin"
            self.logger.exception(msg)
            raise TransportPluginError(msg)

        self.transport_class = NetconfSystemSSHTransport
        self.transport = NetconfSystemSSHTransport(**self.transport_args)  # type: ignore
        self.channel = NetconfChannel(self.transport, **self.channel_args)

        self.strip_namespaces = strip_namespaces
        self.strict_datastores = strict_datastores
        self.server_capabilities: List[str] = []
        self.readable_datastores: List[str] = []
        self.writeable_datastores: List[str] = []
        self.netconf_version = NetconfVersion.VERSION_1_0
        self.message_id = 101

    def open(self) -> None:
        """
        Open netconf connection to server

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        self.logger.info(f"Opening connection to {self._initialization_args['host']}")
        login_bytes = self.transport.open_netconf()
        raw_server_capabilities = self.channel._get_server_capabilities(  # pylint: disable=W0212
            login_bytes
        )

        client_capabilities = self._process_open(raw_server_capabilities=raw_server_capabilities)

        self.channel._send_client_capabilities(  # pylint: disable=W0212
            client_capabilities=client_capabilities, capabilities_version=self.netconf_version
        )
        self.logger.info(f"Connection to {self._initialization_args['host']} opened successfully")

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
        response._record_response(raw_response)  # pylint: disable=W0212
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

        response._record_response(raw_response)  # pylint: disable=W0212
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
        response._record_response(raw_response)  # pylint: disable=W0212
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
        response._record_response(raw_response)  # pylint: disable=W0212
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
        response._record_response(raw_response)  # pylint: disable=W0212
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
        response._record_response(raw_response)  # pylint: disable=W0212
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
        response._record_response(raw_response)  # pylint: disable=W0212
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
        response._record_response(raw_response)  # pylint: disable=W0212
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
        response._record_response(raw_response)  # pylint: disable=W0212
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
        response._record_response(raw_response)  # pylint: disable=W0212
        return response
