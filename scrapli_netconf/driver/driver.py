"""scrapli_netconf.driver.driver"""
import logging
import re
from typing import Any, List, Optional, Union

from lxml import etree
from lxml.etree import Element
from scrapli import Scrape

from scrapli_netconf.channel.channel import NetconfChannel
from scrapli_netconf.exceptions import CouldNotExchangeCapabilities
from scrapli_netconf.response import NetconfResponse
from scrapli_netconf.transport.netconf import NetconfTransport

LOG = logging.getLogger("driver")

CLIENT_CAPABILITIES_1_0 = """
<?xml version="1.0" encoding="utf-8"?>
    <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <capabilities>
            <capability>urn:ietf:params:netconf:base:1.0</capability>
        </capabilities>
</hello>]]>]]>"""
CLIENT_CAPABILITIES_1_1 = """
<?xml version="1.0" encoding="utf-8"?>
    <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <capabilities>
            <capability>urn:ietf:params:netconf:base:1.1</capability>
        </capabilities>
</hello>]]>]]>"""

BASE_RPC_1_0 = (
    "<rpc xmlns='urn:ietf:params:xml:ns:netconf:base:1.0' message-id='{message_id}'></rpc>"
)
BASE_GET = "<get></get>"
BASE_GET_CONFIG = "<get-config><source><{source}/></source></get-config>"
BASE_EDIT_CONFIG = "<edit-config><target><{target}/></target><config></config></edit-config>"
BASE_FILTER = "<filter type='{filter_type}'></filter>"
BASE_COMMIT = "<commit/>"
BASE_DISCARD = "<discard-changes/>"
BASE_LOCK = "<lock><target><{target}/></target></lock>"
BASE_UNLOCK = "<unlock><target><{target}/></target></unlock>"


class NetconfScrape(Scrape):
    def __init__(self, port: int = 830, strip_namespaces: bool = True, **kwargs: Any) -> None:
        super().__init__(port=port, **kwargs)

        self.transport_class = NetconfTransport
        self.transport = NetconfTransport(**self.transport_args)
        self.channel = NetconfChannel(self.transport, **self.channel_args)

        self.strip_namespaces = strip_namespaces
        self.server_capabilities: List[str] = []
        self.netconf_version = "1.0"
        self.message_id = 101

    def _parse_server_capabilities(self, raw_server_capabilities: bytes) -> None:
        """
        Parse netconf server capabilities

        Args:
            raw_server_capabilities: raw bytes containing server capabilities

        Returns:
            N/A  # noqa: DAR202

        Raises:
            CouldNotExchangeCapabilities: if server capabilities cannot be parsed

        """
        filtered_raw_server_capabilities = re.search(
            pattern=rb"(<hello.*<\/hello>)", string=raw_server_capabilities, flags=re.I | re.S
        )
        if filtered_raw_server_capabilities is None:
            msg = f"Failed to parse server capabilities from host {self._host}"
            raise CouldNotExchangeCapabilities(msg)
        server_capabilities_xml = etree.fromstring(filtered_raw_server_capabilities.groups()[0])
        for elem in server_capabilities_xml.iter():
            if "capability" not in elem.tag:
                continue
            self.server_capabilities.append(elem.text)
        LOG.info(f"Server capabilities received and parsed: {self.server_capabilities}")

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
        LOG.info(f"Opening connection to {self._initialization_args['host']}")
        login_bytes = self.transport.open_netconf()
        raw_server_capabilities = self.channel._get_server_capabilities(  # pylint: disable=W0212
            login_bytes
        )
        self._parse_server_capabilities(  # pylint: disable=W0212
            raw_server_capabilities=raw_server_capabilities
        )

        client_capabilities = CLIENT_CAPABILITIES_1_0
        if "urn:ietf:params:netconf:base:1.1" in self.server_capabilities:
            client_capabilities = CLIENT_CAPABILITIES_1_1
            self.netconf_version = "1.1"

        self.channel._send_client_capabilities(  # pylint: disable=W0212
            client_capabilities=client_capabilities, capabilities_version=self.netconf_version
        )
        LOG.info(f"Connection to {self._initialization_args['host']} opened successfully")

    def _build_base_elem(self) -> Element:
        """
        Create base element for netconf operations

        Args:
            N/A

        Returns:
            Element: lxml base element to use for netconf operation

        Raises:
            N/A

        """
        base_xml_str = BASE_RPC_1_0.format(message_id=self.message_id)
        self.message_id += 1
        base_elem = etree.fromstring(base_xml_str)
        return base_elem

    def get(self, filter_: str, filter_type: str = "subtree") -> NetconfResponse:
        """
        Netconf get operation

        Args:
            filter_: string filter to apply to the get
            filter_type: type of filter; subtree|xpath

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            ValueError: if invalid filter value

        """
        if filter_type not in ("subtree", "xpath"):
            raise ValueError(f"`filter_type` should be one of subtree|xpath, got `{filter_type}`")
        # build filter(s) first to ensure valid xml
        xml_filter_element = etree.fromstring(filter_)

        # build base request and insert the get element
        xml_request = self._build_base_elem()
        xml_get_element = etree.fromstring(BASE_GET)
        xml_request.insert(0, xml_get_element)

        # build filter element
        xml_filter_elem = etree.fromstring(BASE_FILTER.format(filter_type=filter_type))

        # insert parent filter element
        get_element = xml_request.find("get")
        get_element.insert(0, xml_filter_elem)

        # insert filter element
        get_filter = xml_request.find("get/filter")
        get_filter.insert(1, xml_filter_element)

        channel_input = etree.tostring(xml_request)

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        raw_response = self.channel.send_input_netconf(channel_input)
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
            source: configuration source to get; running|startup|candidate
            filters: string or list of strings of filters to apply to configuration
            filter_type: type of filter; subtree|xpath

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            ValueError: if invalid filter value
            ValueError: if invalid configuration source value

        """
        if filter_type not in ("subtree", "xpath"):
            raise ValueError(f"`filter_type` should be one of subtree|xpath, got `{filter_type}`")
        if source not in ("running", "startup", "candidate"):
            raise ValueError(f"`source` should be one of running|startup|candidate, got `{source}`")
        if isinstance(filters, str):
            filters = [filters]

        # build filter(s) first to ensure valid xml
        xml_filters = []
        if filters:
            xml_filters = [etree.fromstring(filter_) for filter_ in filters]

        # build base request and insert the get-config element
        xml_request = self._build_base_elem()
        xml_get_config_element = etree.fromstring(BASE_GET_CONFIG.format(source=source))
        xml_request.insert(0, xml_get_config_element)

        if filters:
            # build filter element
            xml_filter_element = etree.fromstring(BASE_FILTER.format(filter_type=filter_type))

            # insert parent filter element
            get_config_element = xml_request.find("get-config")
            get_config_element.insert(1, xml_filter_element)

            # insert filter element(s)
            get_config_filter_element = xml_request.find("get-config/filter")
            for xml_filter_ in xml_filters:
                get_config_filter_element.insert(0, xml_filter_)

        channel_input = etree.tostring(xml_request)

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        raw_response = self.channel.send_input_netconf(channel_input)
        response._record_response(raw_response)  # pylint: disable=W0212
        return response

    def edit_config(
        self, configs: Union[str, List[str]], target: str = "running"
    ) -> NetconfResponse:
        """
        Netconf get-config operation

        Args:
            configs: configuration(s) to send to device
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            ValueError: if invalid configuration target value

        """
        if target not in ("running", "startup", "candidate"):
            raise ValueError(f"`target` should be one of running|startup|candidate, got `{target}`")
        if isinstance(configs, str):
            configs = [configs]

        # build config(s) first to ensure valid xml
        xml_configs = [etree.fromstring(config) for config in configs]

        # build base request and insert the edit-config element
        xml_request = self._build_base_elem()
        xml_edit_config_element = etree.fromstring(BASE_EDIT_CONFIG.format(target=target))
        xml_request.insert(0, xml_edit_config_element)

        # insert parent filter element
        edit_config_element = xml_request.find("edit-config/config")
        for xml_config in xml_configs:
            edit_config_element.insert(0, xml_config)

        channel_input = etree.tostring(xml_request)

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        raw_response = self.channel.send_input_netconf(channel_input)
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
        xml_request = self._build_base_elem()
        xml_commit_element = etree.fromstring(BASE_COMMIT)
        xml_request.insert(0, xml_commit_element)
        channel_input = etree.tostring(xml_request)

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        raw_response = self.channel.send_input_netconf(channel_input)
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
        xml_request = self._build_base_elem()
        xml_discard_element = etree.fromstring(BASE_DISCARD)
        xml_request.insert(0, xml_discard_element)
        channel_input = etree.tostring(xml_request)

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        raw_response = self.channel.send_input_netconf(channel_input)
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
            ValueError: if invalid configuration source

        """
        if target not in ("running", "startup", "candidate"):
            raise ValueError(f"`target` should be one of running|startup|candidate, got `{target}`")
        xml_request = self._build_base_elem()
        xml_lock_element = etree.fromstring(BASE_LOCK.format(target=target))
        xml_request.insert(0, xml_lock_element)
        channel_input = etree.tostring(xml_request)

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        raw_response = self.channel.send_input_netconf(channel_input)
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
            ValueError: if invalid configuration source

        """
        if target not in ("running", "startup", "candidate"):
            raise ValueError(f"`target` should be one of running|startup|candidate, got `{target}`")
        xml_request = self._build_base_elem()
        xml_unlock_element = etree.fromstring(BASE_UNLOCK.format(target=target))
        xml_request.insert(0, xml_unlock_element)
        channel_input = etree.tostring(xml_request)

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        raw_response = self.channel.send_input_netconf(channel_input)
        response._record_response(raw_response)  # pylint: disable=W0212
        return response

    def bare_rpc(self, filter_: str) -> NetconfResponse:
        """
        Netconf "bare_rpc" operation; typically only used with juniper devices

        Args:
            filter_: filter/rpc to execute

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object

        Raises:
            N/A

        """
        # build base request
        xml_request = self._build_base_elem()

        # build filter element
        xml_filter_elem = etree.fromstring(filter_)

        # insert filter element
        xml_request.insert(0, xml_filter_elem)

        channel_input = etree.tostring(xml_request)

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        raw_response = self.channel.send_input_netconf(channel_input)
        response._record_response(raw_response)  # pylint: disable=W0212
        return response
