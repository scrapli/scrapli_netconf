"""scrapli_netconf.driver.base_driver"""
import re
import warnings
from enum import Enum
from typing import List, Optional, Union

from lxml import etree
from lxml.etree import Element

from scrapli.driver.base_driver import ScrapeBase
from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.exceptions import CapabilityNotSupported, CouldNotExchangeCapabilities
from scrapli_netconf.response import NetconfResponse


class NetconfClientCapabilities(Enum):
    CAPABILITIES_1_0 = """
<?xml version="1.0" encoding="utf-8"?>
    <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <capabilities>
            <capability>urn:ietf:params:netconf:base:1.0</capability>
        </capabilities>
</hello>]]>]]>"""
    CAPABILITIES_1_1 = """
<?xml version="1.0" encoding="utf-8"?>
    <hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <capabilities>
            <capability>urn:ietf:params:netconf:base:1.1</capability>
        </capabilities>
</hello>]]>]]>"""


class NetconfBaseOperations(Enum):
    FILTER_SUBTREE = "<filter type='{filter_type}'></filter>"
    FILTER_XPATH = "<filter type='{filter_type}' select='{xpath}'></filter>"
    GET = "<get></get>"
    GET_CONFIG = "<get-config><source><{source}/></source></get-config>"
    EDIT_CONFIG = "<edit-config><target><{target}/></target></edit-config>"
    DELETE_CONFIG = "<delete-config><target><{target}/></target></delete-config>"
    COMMIT = "<commit/>"
    DISCARD = "<discard-changes/>"
    LOCK = "<lock><target><{target}/></target></lock>"
    UNLOCK = "<unlock><target><{target}/></target></unlock>"
    RPC = "<rpc xmlns='urn:ietf:params:xml:ns:netconf:base:1.0' message-id='{message_id}'></rpc>"
    VALIDATE = "<validate><source><{source}/></source></validate>"


class NetconfScrapeBase(ScrapeBase):
    server_capabilities: List[str]
    readable_datastores: List[str]
    writeable_datastores: List[str]
    netconf_version: NetconfVersion
    strip_namespaces: bool
    strict_datastores: bool
    message_id: int

    def _process_open(self, raw_server_capabilities: bytes) -> NetconfClientCapabilities:
        """
        Process received capabilities; return client capabilities

        Args:
            raw_server_capabilities: raw bytes containing server capabilities

        Returns:
            NetconfClientCapabilities: NetconfClientCapabilities enum of appropriate type

        Raises:
            N/A

        """
        self._parse_server_capabilities(raw_server_capabilities=raw_server_capabilities)

        client_capabilities = NetconfClientCapabilities.CAPABILITIES_1_0
        if "urn:ietf:params:netconf:base:1.1" in self.server_capabilities:
            client_capabilities = NetconfClientCapabilities.CAPABILITIES_1_1
            self.netconf_version = NetconfVersion.VERSION_1_1

        return client_capabilities

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
            self.server_capabilities.append(elem.text.strip())
        self._build_readable_datastores()
        self._build_writeable_datastores()
        self.logger.info(f"Server capabilities received and parsed: {self.server_capabilities}")

    def _build_readable_datastores(self) -> None:
        """
        Build a list of readable datastores based on server's advertised capabilities

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        self.readable_datastores = []
        self.readable_datastores.append("running")
        if "urn:ietf:params:netconf:capability:candidate:1.0" in self.server_capabilities:
            self.readable_datastores.append("candidate")
        if "urn:ietf:params:netconf:capability:startup:1.0" in self.server_capabilities:
            self.readable_datastores.append("startup")

    def _build_writeable_datastores(self) -> None:
        """
        Build a list of writeable/editable datastores based on server's advertised capabilities

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        self.writeable_datastores = []
        if "urn:ietf:params:netconf:capability:writeable-running:1.0" in self.server_capabilities:
            self.writeable_datastores.append("running")
        if "urn:ietf:params:netconf:capability:writable-running:1.0" in self.server_capabilities:
            # NOTE: iosxe shows "writable" (as of 2020.07.01) despite RFC being "writeable"
            self.writeable_datastores.append("running")
        if "urn:ietf:params:netconf:capability:candidate:1.0" in self.server_capabilities:
            self.writeable_datastores.append("candidate")
        if "urn:ietf:params:netconf:capability:startup:1.0" in self.server_capabilities:
            self.writeable_datastores.append("startup")

    def _validate_get_config_target(self, source: str) -> None:
        """
        Validate get-config source is acceptable

        Args:
            source: configuration source to get; typically one of running|startup|candidate

        Returns:
            N/A  # noqa: DAR202

        Raises:
            ValueError: if an invalid source was selected and strict_datastores is True

        """
        if source not in self.readable_datastores:
            msg = f"`source` should be one of {self.readable_datastores}, got `{source}`"
            self.logger.warning(msg)
            if self.strict_datastores is True:
                raise ValueError(msg)
            warnings.warn(msg)

    def _validate_edit_config_target(self, target: str) -> None:
        """
        Validate edit-config/lock/unlock target is acceptable

        Args:
            target: configuration source to edit/lock; typically one of running|startup|candidate

        Returns:
            N/A  # noqa: DAR202

        Raises:
            ValueError: if an invalid source was selected

        """
        if target not in self.writeable_datastores:
            msg = f"`target` should be one of {self.writeable_datastores}, got `{target}`"
            self.logger.warning(msg)
            if self.strict_datastores is True:
                raise ValueError(msg)
            warnings.warn(msg)

    def _validate_delete_config_target(self, target: str) -> None:
        """
        Validate delete-config/lock/unlock target is acceptable

        Args:
            target: configuration source to delete; typically one of startup|candidate

        Returns:
            N/A  # noqa: DAR202

        Raises:
            ValueError: if an invalid target was selected

        """
        if target == "running" or target not in self.writeable_datastores:
            msg = f"`target` should be one of {self.writeable_datastores}, got `{target}`"
            if target == "running":
                msg = "delete-config `target` may not be `running`"
            self.logger.warning(msg)
            if self.strict_datastores is True:
                raise ValueError(msg)
            warnings.warn(msg)

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
        self.logger.debug(f"Building base element for message id {self.message_id}")
        base_xml_str = NetconfBaseOperations.RPC.value.format(message_id=self.message_id)
        self.message_id += 1
        base_elem = etree.fromstring(text=base_xml_str)
        return base_elem

    def _build_filters(self, filters: List[str], filter_type: str = "subtree") -> Element:
        """
        Create filter element for a given rpc

        Args:
            filters: list of strings of filters to build into a filter element
            filter_type: type of filter; subtree|xpath

        Returns:
            Element: lxml filter element to use for netconf operation

        Raises:
            CapabilityNotSupported: if xpath selected and not supported on server
            ValueError: if filter_type is not one of subtree|xpath

        """
        if filter_type == "subtree":
            xml_filter_elem = etree.fromstring(
                NetconfBaseOperations.FILTER_SUBTREE.value.format(filter_type=filter_type)
            )
            for filter_ in filters:
                # "validate" subtree filter by forcing it into xml
                xml_filter_element = etree.fromstring(filter_)
                # insert the subtree filter into the parent filter element
                xml_filter_elem.insert(1, xml_filter_element)
        elif filter_type == "xpath":
            if "urn:ietf:params:netconf:capability:xpath:1.0" not in self.server_capabilities:
                msg = "xpath filter requested, but is not supported by the server"
                self.logger.exception(msg)
                raise CapabilityNotSupported(msg)
            # assuming for now that there will only ever be a single xpath string/filter... this may
            # end up being a shitty assumption!
            filter_ = filters[0]
            xml_filter_elem = etree.fromstring(
                NetconfBaseOperations.FILTER_XPATH.value.format(
                    filter_type=filter_type, xpath=filter_
                )
            )
        else:
            raise ValueError(f"`filter_type` should be one of subtree|xpath, got `{filter_type}`")
        return xml_filter_elem

    def _pre_get(self, filter_: str, filter_type: str = "subtree") -> NetconfResponse:
        """
        Handle pre "get" tasks for consistency between sync/async versions

        Args:
            filter_: string filter to apply to the get
            filter_type: type of filter; subtree|xpath

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object containing all the necessary
                channel inputs (string and xml)

        Raises:
            N/A

        """
        self.logger.debug(
            f"Building payload for `get` operation. filter_type: {filter_type}, filter_: {filter_}"
        )

        # build base request and insert the get element
        xml_request = self._build_base_elem()
        xml_get_element = etree.fromstring(NetconfBaseOperations.GET.value)
        xml_request.insert(0, xml_get_element)

        xml_filter_elem = self._build_filters(filters=[filter_], filter_type=filter_type)

        # insert filter element into parent get element
        get_element = xml_request.find("get")
        get_element.insert(0, xml_filter_elem)

        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        self.logger.debug(f"Built payload for `get` operation. Payload: {channel_input.decode()}")
        return response

    def _pre_get_config(
        self,
        source: str = "running",
        filters: Optional[Union[str, List[str]]] = None,
        filter_type: str = "subtree",
    ) -> NetconfResponse:
        """
        Handle pre "get_config" tasks for consistency between sync/async versions

        Args:
            source: configuration source to get; typically one of running|startup|candidate
            filters: string or list of strings of filters to apply to configuration
            filter_type: type of filter; subtree|xpath

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object containing all the necessary
                channel inputs (string and xml)

        Raises:
            N/A

        """
        self.logger.debug(
            f"Building payload for `get-config` operation. source: {source}, filter_type: "
            f"{filter_type}, filters: {filters}"
        )
        self._validate_get_config_target(source=source)

        # build base request and insert the get-config element
        xml_request = self._build_base_elem()
        xml_get_config_element = etree.fromstring(
            NetconfBaseOperations.GET_CONFIG.value.format(source=source)
        )
        xml_request.insert(0, xml_get_config_element)

        if filters is not None:
            if isinstance(filters, str):
                filters = [filters]
            xml_filter_elem = self._build_filters(filters=filters, filter_type=filter_type)
            # insert filter element into parent get element
            get_element = xml_request.find("get-config")
            # insert *after* source, otherwise juniper seems to gripe, maybe/probably others as well
            get_element.insert(1, xml_filter_elem)

        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        self.logger.debug(
            f"Built payload for `get-config` operation. Payload: {channel_input.decode()}"
        )
        return response

    def _pre_edit_config(
        self, config: Union[str, List[str]], target: str = "running"
    ) -> NetconfResponse:
        """
        Handle pre "edit_config" tasks for consistency between sync/async versions

        Args:
            config: configuration to send to device
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object containing all the necessary
                channel inputs (string and xml)

        Raises:
            N/A

        """
        self.logger.debug(
            f"Building payload for `get-config` operation. target: {target}, config: {config}"
        )
        self._validate_edit_config_target(target=target)

        # build config first to ensure valid xml
        xml_config = etree.fromstring(config)

        # build base request and insert the edit-config element
        xml_request = self._build_base_elem()
        xml_edit_config_element = etree.fromstring(
            NetconfBaseOperations.EDIT_CONFIG.value.format(target=target)
        )
        xml_request.insert(0, xml_edit_config_element)

        # insert parent filter element to first position so that target stays first just for nice
        # output/readability
        edit_config_element = xml_request.find("edit-config")
        edit_config_element.insert(1, xml_config)

        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        self.logger.debug(
            f"Built payload for `edit-config` operation. Payload: {channel_input.decode()}"
        )
        return response

    def _pre_delete_config(self, target: str = "running") -> NetconfResponse:
        """
        Handle pre "edit_config" tasks for consistency between sync/async versions

        Args:
            target: configuration source to target; startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object containing all the necessary
                channel inputs (string and xml)

        Raises:
            N/A

        """
        self.logger.debug(f"Building payload for `delete-config` operation. target: {target}")
        self._validate_delete_config_target(target=target)

        xml_request = self._build_base_elem()
        xml_validate_element = etree.fromstring(
            NetconfBaseOperations.DELETE_CONFIG.value.format(target=target)
        )
        xml_request.insert(0, xml_validate_element)
        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        self.logger.debug(
            f"Built payload for `delete-config` operation. Payload: {channel_input.decode()}"
        )
        return response

    def _pre_commit(self) -> NetconfResponse:
        """
        Handle pre "commit" tasks for consistency between sync/async versions

        Args:
            N/A

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object containing all the necessary
                channel inputs (string and xml)

        Raises:
            N/A

        """
        self.logger.debug("Building payload for `commit` operation")
        xml_request = self._build_base_elem()
        xml_commit_element = etree.fromstring(NetconfBaseOperations.COMMIT.value)
        xml_request.insert(0, xml_commit_element)
        channel_input = etree.tostring(xml_request)

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        self.logger.debug(
            f"Built payload for `commit` operation. Payload: {channel_input.decode()}"
        )
        return response

    def _pre_discard(self) -> NetconfResponse:
        """
        Handle pre "discard" tasks for consistency between sync/async versions

        Args:
            N/A

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object containing all the necessary
                channel inputs (string and xml)

        Raises:
            N/A

        """
        self.logger.debug("Building payload for `discard` operation.")
        xml_request = self._build_base_elem()
        xml_commit_element = etree.fromstring(NetconfBaseOperations.DISCARD.value)
        xml_request.insert(0, xml_commit_element)
        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        self.logger.debug(
            f"Built payload for `discard` operation. Payload: {channel_input.decode()}"
        )
        return response

    def _pre_lock(self, target: str) -> NetconfResponse:
        """
        Handle pre "lock" tasks for consistency between sync/async versions

        Args:
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object containing all the necessary
                channel inputs (string and xml)

        Raises:
            N/A

        """
        self.logger.debug("Building payload for `lock` operation.")
        self._validate_edit_config_target(target=target)

        xml_request = self._build_base_elem()
        xml_lock_element = etree.fromstring(NetconfBaseOperations.LOCK.value.format(target=target))
        xml_request.insert(0, xml_lock_element)
        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        self.logger.debug(f"Built payload for `lock` operation. Payload: {channel_input.decode()}")
        return response

    def _pre_unlock(self, target: str) -> NetconfResponse:
        """
        Handle pre "unlock" tasks for consistency between sync/async versions

        Args:
            target: configuration source to target; running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object containing all the necessary
                channel inputs (string and xml)

        Raises:
            N/A

        """
        self.logger.debug("Building payload for `unlock` operation.")
        self._validate_edit_config_target(target=target)

        xml_request = self._build_base_elem()
        xml_lock_element = etree.fromstring(
            NetconfBaseOperations.UNLOCK.value.format(target=target)
        )
        xml_request.insert(0, xml_lock_element)
        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        self.logger.debug(
            f"Built payload for `unlock` operation. Payload: {channel_input.decode()}"
        )
        return response

    def _pre_rpc(self, filter_: str) -> NetconfResponse:
        """
        Handle pre "rpc" tasks for consistency between sync/async versions

        Args:
            filter_: filter/rpc to execute

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object containing all the necessary
                channel inputs (string and xml)

        Raises:
            N/A

        """
        self.logger.debug("Building payload for `rpc` operation.")
        xml_request = self._build_base_elem()

        # build filter element
        xml_filter_elem = etree.fromstring(filter_)

        # insert filter element
        xml_request.insert(0, xml_filter_elem)

        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        self.logger.debug(f"Built payload for `rpc` operation. Payload: {channel_input.decode()}")
        return response

    def _pre_validate(self, source: str) -> NetconfResponse:
        """
        Handle pre "validate" tasks for consistency between sync/async versions

        Args:
            source: configuration source to validate; typically one of running|startup|candidate

        Returns:
            NetconfResponse: scrapli_netconf NetconfResponse object containing all the necessary
                channel inputs (string and xml)

        Raises:
            CapabilityNotSupported: if `validate` ca

        """
        self.logger.debug("Building payload for `validate` operation.")

        if not any(
            cap in self.server_capabilities
            for cap in (
                "urn:ietf:params:netconf:capability:validate:1.0",
                "urn:ietf:params:netconf:capability:validate:1.1",
            )
        ):
            msg = "validate requested, but is not supported by the server"
            self.logger.exception(msg)
            raise CapabilityNotSupported(msg)

        self._validate_edit_config_target(target=source)

        xml_request = self._build_base_elem()
        xml_validate_element = etree.fromstring(
            NetconfBaseOperations.VALIDATE.value.format(source=source)
        )
        xml_request.insert(0, xml_validate_element)
        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.transport.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        self.logger.debug(
            f"Built payload for `validate` operation. Payload: {channel_input.decode()}"
        )
        return response
