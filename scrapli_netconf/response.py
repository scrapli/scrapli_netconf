"""scrapli_netconf.response"""
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from lxml import etree
from lxml.etree import Element

from scrapli.response import Response
from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.helper import remove_namespaces

LOG = logging.getLogger("response")

# "chunk match" matches two groups per section returned from the netconf server, first the length of
# the response, and second the response itself. we use the length of the response to validate the
# response is in fact X length
CHUNK_MATCH_1_1 = re.compile(pattern=rb"^#(\d+)(?:\n*)(((?!#).)*)", flags=re.M | re.S)

PARSER = etree.XMLParser(remove_blank_text=True)


class NetconfResponse(Response):
    def __init__(
        self,
        netconf_version: NetconfVersion,
        xml_input: Element,
        strip_namespaces: bool = True,
        failed_when_contains: Optional[Union[bytes, List[bytes]]] = b"<rpc-error>",
        **kwargs: Any,
    ):
        """
        Scrapli Netconf NetconfResponse

        Store channel_input, resulting output, and start/end/elapsed time information. Attempt to
        determine if command was successful or not and reflect that in a failed attribute.

        Args:
            netconf_version: string of netconf version; `1.0`|`1.1`
            xml_input: lxml Element of input to be sent to device
            strip_namespaces: strip out all namespaces if True, otherwise ignore them
            failed_when_contains: list of bytes that, if present in final output, represent a
                failed command/interaction -- should generally be left alone for netconf. Note that
                this differs from the base scrapli Response object as we want to be parsing/checking
                for these strings in raw byte strings we get back from the device
            kwargs: kwargs for instantiation of scrapli Response object supertype

        Returns:
            N/A  # noqa: DAR202

        Raises:
            ValueError: if invalid netconf_version string

        """
        if netconf_version not in (NetconfVersion.VERSION_1_0, NetconfVersion.VERSION_1_1):
            raise ValueError(f"`netconf_version` should be one of 1.0|1.1, got `{netconf_version}`")

        self.netconf_version = netconf_version
        self.xml_input = xml_input
        self.strip_namespaces = strip_namespaces
        self.xml_result: Element

        super().__init__(**kwargs)

        if isinstance(failed_when_contains, bytes):
            failed_when_contains = [failed_when_contains]
        self.failed_when_contains = failed_when_contains

    def _record_response(self, result: bytes) -> None:
        """
        Record channel_input results and elapsed time of channel input/reading output

        Args:
            result: bytes result of channel_input

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        self.finish_time = datetime.now()
        self.elapsed_time = (self.finish_time - self.start_time).total_seconds()
        self.raw_result = result

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            self._record_response_netconf_1_0()
        else:
            self._record_response_netconf_1_1()

    def _record_response_netconf_1_0(self) -> None:
        """
        Record response for netconf version 1.0

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        if not self.failed_when_contains:
            self.failed = False
        elif not any(err in self.raw_result for err in self.failed_when_contains):
            self.failed = False

        # remove the message end characters and xml document header see:
        # https://github.com/scrapli/scrapli_netconf/issues/1
        self.xml_result = etree.fromstring(
            self.raw_result.replace(b"]]>]]>", b"").replace(
                b'<?xml version="1.0" encoding="UTF-8"?>', b""
            ),
            parser=PARSER,
        )

        if self.strip_namespaces:
            self.xml_result = remove_namespaces(self.xml_result)
            self.result = etree.tostring(self.xml_result, pretty_print=True).decode()
        else:
            self.result = etree.tostring(self.xml_result, pretty_print=True).decode()

    def _record_response_netconf_1_1(self) -> None:
        """
        Record response for netconf version 1.1

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        if not self.failed_when_contains:
            self.failed = False
        elif not any(err in self.raw_result for err in self.failed_when_contains):
            self.failed = False

        result_sections = re.findall(pattern=CHUNK_MATCH_1_1, string=self.raw_result)

        # validate all received data
        for result in result_sections:
            expected_len = int(result[0])
            result_value = result[1]
            # account for trailing newline char
            actual_len = len(result_value) - 1
            if expected_len == 1:
                # at least nokia tends to have itty bitty chunks of one element, deal w/ that
                actual_len = 1
            if expected_len != actual_len:
                LOG.critical(
                    f"Return element length invalid, expected {expected_len} got {actual_len} for "
                    f"element: {repr(result_value)}"
                )
                self.failed = True

        self.xml_result = etree.fromstring(
            b"\n".join(
                [
                    # remove the message end characters and xml document header see:
                    # https://github.com/scrapli/scrapli_netconf/issues/1
                    result[1].replace(b'<?xml version="1.0" encoding="UTF-8"?>', b"")
                    for result in result_sections
                ]
            ),
            parser=PARSER,
        )

        if self.strip_namespaces:
            self.xml_result = remove_namespaces(self.xml_result)
            self.result = etree.tostring(self.xml_result, pretty_print=True).decode()
        else:
            self.result = etree.tostring(self.xml_result, pretty_print=True).decode()

    def get_xml_elements(self) -> Dict[str, Element]:
        """
        Parse each section under "data" into a dict of {tag: Element} for easy viewing/parsing

        Args:
            N/A

        Returns:
            xml_elements: dictionary of tag: Element

        Raises:
            N/A

        """
        xml_elements = {}
        data_element = self.xml_result.find("data", namespaces=self.xml_result.nsmap)

        # juniper doesn't return data in a "data" element for bare rpc calls, guard against that
        # breaking the iterchildren()
        if data_element is not None:
            for child in data_element.iterchildren():
                _tag = etree.QName(child.tag).localname
                xml_elements[_tag] = child
        return xml_elements

    def textfsm_parse_output(self, to_dict: bool = True) -> Union[Dict[str, Any], List[Any]]:
        """
        Override scrapli Response `textfsm_parse_output` method; not applicable for netconf

        Args:
            to_dict: ignore, only here to ensure compliance with supertype method

        Returns:
            N/A  # noqa: DAR202

        Raises:
            NotImplementedError: always

        """
        raise NotImplementedError("No textfsm parsing for netconf output!")

    def genie_parse_output(self) -> Union[Dict[str, Any], List[Any]]:
        """
        Override scrapli Response `genie_parse_output` method; not applicable for netconf

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            NotImplementedError: always

        """
        raise NotImplementedError("No genie parsing for netconf output!")
