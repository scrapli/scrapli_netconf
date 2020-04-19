"""scrapli_netconf.response"""
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Union

from lxml import etree
from lxml.etree import Element
from scrapli.response import Response

from scrapli_netconf.helper import remove_namespaces

LOG = logging.getLogger("response")

# "chunk match" matches two groups per section returned from the netconf server, first the length of
# the response, and second the response itself. we use the length of the response to validate the
# response is in fact X length
CHUNK_MATCH_1_1 = re.compile(pattern=r"^#(\d+)(?:\n*)(((?!#).)*)", flags=re.M | re.S)


class NetconfResponse(Response):
    def __init__(
        self, netconf_version: str, xml_input: Element, strip_namespaces: bool = True, **kwargs: Any
    ):
        """
        Scrapli Netconf NetconfResponse

        Store channel_input, resulting output, and start/end/elapsed time information. Attempt to
        determine if command was successful or not and reflect that in a failed attribute.

        Args:
            netconf_version: string of netconf version; `1.0`|`1.1`
            xml_input: lxml Element of input to be sent to device
            strip_namespaces: strip out all namespaces if True, otherwise ignore them
            kwargs: kwargs for instantiation of scrapli Response object supertype

        Returns:
            N/A  # noqa: DAR202

        Raises:
            ValueError: if invalid netconf_version string

        """
        if netconf_version not in ("1.0", "1.1"):
            raise ValueError(f"`netconf_version` should be one of 1.0|1.1, got `{netconf_version}`")

        self.netconf_version = netconf_version
        self.xml_input = xml_input
        self.strip_namespaces = strip_namespaces

        self.xml_result: Element

        super().__init__(**kwargs)

    def _record_response(self, result: str) -> None:
        """
        Record channel_input results and elapsed time of channel input/reading output

        Args:
            result: string result of channel_input

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        self.finish_time = datetime.now()
        self.elapsed_time = (self.finish_time - self.start_time).total_seconds()
        self.raw_result = result

        if self.netconf_version == "1.0":
            raise NotImplementedError("Only netconf 1.1 is currently supported")
        self._record_response_netconf_1_1()

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
        self.failed = False
        result_sections = re.findall(pattern=CHUNK_MATCH_1_1, string=self.raw_result)

        # validate all received data
        for result in result_sections:
            expected_len = int(result[0])
            result_value = result[1]
            # account for trailing newline char
            actual_len = len(result_value) - 1
            if expected_len != actual_len:
                LOG.critical(
                    f"Return element length invalid, expected {expected_len} got {actual_len} for "
                    f"element: {repr(result_value)}"
                )
                self.failed = True

        self.result = "\n".join([result[1].rstrip() for result in result_sections])
        self.xml_result = etree.fromstring(self.result)

        if self.strip_namespaces:
            xml_result = etree.fromstring(self.result)
            self.xml_result = remove_namespaces(xml_result)
            self.result = etree.tostring(self.xml_result)

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
            N/A

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
            N/A

        """
        raise NotImplementedError("No genie parsing for netconf output!")
