"""scrapli_netconf.driver.base_driver"""
import importlib
import warnings
from dataclasses import fields
from enum import Enum
from typing import Any, Callable, List, Optional, Tuple, Union

from lxml import etree
from lxml.etree import Element

from scrapli.driver.base.base_driver import BaseDriver
from scrapli.exceptions import ScrapliTypeError
from scrapli_netconf.channel.base_channel import NetconfBaseChannelArgs
from scrapli_netconf.constants import NetconfClientCapabilities, NetconfVersion
from scrapli_netconf.exceptions import CapabilityNotSupported
from scrapli_netconf.response import NetconfResponse

PARSER = etree.XMLParser(remove_blank_text=True, recover=True)


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


class NetconfBaseDriver(BaseDriver):
    host: str
    readable_datastores: List[str]
    writeable_datastores: List[str]
    strip_namespaces: bool
    strict_datastores: bool
    _netconf_base_channel_args: NetconfBaseChannelArgs

    @property
    def netconf_version(self) -> NetconfVersion:
        """
        Getter for `netconf_version` attribute

        Args:
            N/A

        Returns:
            NetconfVersion: netconf_version enum

        Raises:
            N/A

        """
        return self._netconf_base_channel_args.netconf_version

    @netconf_version.setter
    def netconf_version(self, value: NetconfVersion) -> None:
        """
        Setter for `netconf_version` attribute

        Args:
            value: NetconfVersion

        Returns:
            None

        Raises:
            ScrapliTypeError: if value is not of type NetconfVersion

        """
        self.logger.debug(f"setting 'netconf_version' value to '{value.value}'")

        if not isinstance(value, NetconfVersion):
            raise ScrapliTypeError

        self._netconf_base_channel_args.netconf_version = value

        if self._netconf_base_channel_args.netconf_version == NetconfVersion.VERSION_1_0:
            self._base_channel_args.comms_prompt_pattern = "]]>]]>"
        else:
            self._base_channel_args.comms_prompt_pattern = r"^##$"

    @property
    def client_capabilities(self) -> NetconfClientCapabilities:
        """
        Getter for `client_capabilities` attribute

        Args:
            N/A

        Returns:
            NetconfClientCapabilities: netconf client capabilities enum

        Raises:
            N/A

        """
        return self._netconf_base_channel_args.client_capabilities

    @client_capabilities.setter
    def client_capabilities(self, value: NetconfClientCapabilities) -> None:
        """
        Setter for `client_capabilities` attribute

        Args:
            value: NetconfClientCapabilities value for client_capabilities

        Returns:
            None

        Raises:
            ScrapliTypeError: if value is not of type NetconfClientCapabilities

        """
        self.logger.debug(f"setting 'client_capabilities' value to '{value.value}'")

        if not isinstance(value, NetconfClientCapabilities):
            raise ScrapliTypeError

        self._netconf_base_channel_args.client_capabilities = value

    @property
    def server_capabilities(self) -> List[str]:
        """
        Getter for `server_capabilities` attribute

        Args:
            N/A

        Returns:
            list: list of strings of server capabilities

        Raises:
            N/A

        """
        return self._netconf_base_channel_args.server_capabilities or []

    @server_capabilities.setter
    def server_capabilities(self, value: NetconfClientCapabilities) -> None:
        """
        Setter for `server_capabilities` attribute

        Args:
            value: list of strings of netconf server capabilities

        Returns:
            None

        Raises:
            ScrapliTypeError: if value is not of type list

        """
        self.logger.debug(f"setting 'server_capabilities' value to '{value}'")

        if not isinstance(value, list):
            raise ScrapliTypeError

        self._netconf_base_channel_args.server_capabilities = value

    def _transport_factory(self) -> Tuple[Callable[..., Any], object]:
        """
        Determine proper transport class and necessary arguments to initialize that class

        Args:
            N/A

        Returns:
            Tuple[Callable[..., Any], object]: tuple of transport class and dataclass of transport
                class specific arguments

        Raises:
            N/A

        """
        transport_plugin_module = importlib.import_module(
            f"scrapli_netconf.transport.plugins.{self.transport_name}.transport"
        )

        transport_class = getattr(
            transport_plugin_module, f"Netconf{self.transport_name.capitalize()}Transport"
        )
        plugin_transport_args_class = getattr(transport_plugin_module, "PluginTransportArgs")

        _plugin_transport_args = {
            field.name: getattr(self, field.name) for field in fields(plugin_transport_args_class)
        }

        plugin_transport_args = plugin_transport_args_class(**_plugin_transport_args)

        return transport_class, plugin_transport_args

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
        # pylint did not seem to want to be ok with assigning this as a class attribute... and its
        # only used here so... here we are
        self.message_id: int  # pylint: disable=W0201
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
                NetconfBaseOperations.FILTER_SUBTREE.value.format(filter_type=filter_type),
            )
            for filter_ in filters:
                # "validate" subtree filter by forcing it into xml, parser "flattens" it as well
                xml_filter_element = etree.fromstring(filter_, parser=PARSER)
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
                ),
                parser=PARSER,
            )
        else:
            raise ValueError(f"`filter_type` should be one of subtree|xpath, got `{filter_type}`")
        return xml_filter_elem

    def _pre_get(self, filter_: str, filter_type: str = "subtree") -> NetconfResponse:
        """
        Handle pre "get" tasks for consistency between sync/async versions

        *NOTE*
        The channel input (filter_) is loaded up as an lxml etree element here, this is done with a
        parser that removes whitespace. This has a somewhat undesirable effect of making any
        "pretty" input not pretty, however... after we load the xml object (which we do to validate
        that it is valid xml) we dump that xml object back to a string to be used as the actual
        raw payload we send down the channel, which means we are sending "flattened" (not pretty/
        indented xml) to the device. This is important it seems! Some devices seme to not mind
        having the "nicely" formatted input (pretty xml). But! On devices that "echo" the inputs
        back -- sometimes the device will respond to our rpc without "finishing" echoing our inputs
        to the device, this breaks the core "read until input" processing that scrapli always does.
        For whatever reason if there are no line breaks this does not seem to happen? /shrug. Note
        that this comment applies to all of the "pre" methods that we parse a filter/payload!

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
            host=self.host,
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
            NetconfBaseOperations.GET_CONFIG.value.format(source=source), parser=PARSER
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
            host=self.host,
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
            f"Building payload for `edit-config` operation. target: {target}, config: {config}"
        )
        self._validate_edit_config_target(target=target)

        xml_config = etree.fromstring(config, parser=PARSER)

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
            host=self.host,
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
            NetconfBaseOperations.DELETE_CONFIG.value.format(target=target), parser=PARSER
        )
        xml_request.insert(0, xml_validate_element)
        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.host,
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
        xml_commit_element = etree.fromstring(NetconfBaseOperations.COMMIT.value, parser=PARSER)
        xml_request.insert(0, xml_commit_element)
        channel_input = etree.tostring(xml_request)

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.host,
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
        xml_commit_element = etree.fromstring(NetconfBaseOperations.DISCARD.value, parser=PARSER)
        xml_request.insert(0, xml_commit_element)
        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.host,
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
        xml_lock_element = etree.fromstring(
            NetconfBaseOperations.LOCK.value.format(target=target), parser=PARSER
        )
        xml_request.insert(0, xml_lock_element)
        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.host,
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
            NetconfBaseOperations.UNLOCK.value.format(target=target, parser=PARSER)
        )
        xml_request.insert(0, xml_lock_element)
        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.host,
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
        xml_filter_elem = etree.fromstring(filter_, parser=PARSER)

        # insert filter element
        xml_request.insert(0, xml_filter_elem)

        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.host,
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
            CapabilityNotSupported: if `validate` capability does not exist

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
            NetconfBaseOperations.VALIDATE.value.format(source=source), parser=PARSER
        )
        xml_request.insert(0, xml_validate_element)
        channel_input = etree.tostring(
            element_or_tree=xml_request, xml_declaration=True, encoding="utf-8"
        )

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            channel_input = channel_input + b"\n]]>]]>"

        response = NetconfResponse(
            host=self.host,
            channel_input=channel_input.decode(),
            xml_input=xml_request,
            netconf_version=self.netconf_version,
            strip_namespaces=self.strip_namespaces,
        )
        self.logger.debug(
            f"Built payload for `validate` operation. Payload: {channel_input.decode()}"
        )
        return response
