<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/sanitize.min.css" integrity="sha256-PK9q560IAAa6WVRRh76LtCaI8pjTJ2z11v0miyNNjrs=" crossorigin>
<link rel="preload stylesheet" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/10up-sanitize.css/11.0.1/typography.min.css" integrity="sha256-7l/o7C8jubJiy74VsKTidCy1yBkRtiUGbVkYBylBqUg=" crossorigin>
<link rel="stylesheet preload" as="style" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/styles/github.min.css" crossorigin>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/10.1.1/highlight.min.js" integrity="sha256-Uv3H6lx7dJmRfRvH8TH6kJD1TSK1aFcwgx+mdg3epi8=" crossorigin></script>
<script>window.addEventListener('DOMContentLoaded', () => hljs.initHighlighting())</script>















#Module scrapli_netconf.response

scrapli_netconf.response

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
"""scrapli_netconf.response"""
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from lxml import etree
from lxml.etree import Element

from scrapli.response import Response
from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.helper import remove_namespaces

LOG = logging.getLogger("response")

# "chunk match" matches two groups per section returned from the netconf server, first the length of
# the response, and second the response itself. we use the length of the response to validate the
# response is in fact X length. this regex is basically "start at line feed, and match "#123" where
# "123" is obviously any length of digits... then we don't capture zero or more newlines because we
# dont care about them. Next we have the main capture group -- this starts with a negative lookahead
# that says we want to stop matching as soon as we hit another "#123" *or* a "##" (end of message),
# after that we match anything "." and that is the "body" of the response
CHUNK_MATCH_1_1 = re.compile(pattern=rb"^#(\d+)(?:\n*)(((?!#\d+\n+|##).)*)", flags=re.M | re.S)

PARSER = etree.XMLParser(remove_blank_text=True, recover=True)


class NetconfResponse(Response):
    # intentionally overriding base class' list of strings for failed when contains
    failed_when_contains: List[bytes]  # type: ignore[assignment]

    def __init__(
        self,
        netconf_version: NetconfVersion,
        xml_input: Element,
        strip_namespaces: bool = True,
        failed_when_contains: Optional[Union[bytes, List[bytes]]] = None,
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

        if failed_when_contains is None:
            # match on both opening and closing tags too so we never have to think about/compare
            # things with namespaces (the closing tags wont have namespaces)
            failed_when_contains = [
                b"</rpc-error>",
                b"</rpc-errors>",
                b"<rpc-error>",
                b"<rpc-errors>",
            ]
        if isinstance(failed_when_contains, bytes):
            failed_when_contains = [failed_when_contains]
        self.failed_when_contains = failed_when_contains

        self.error_messages: List[str] = []

    def record_response(self, result: bytes) -> None:
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

        if not self.failed_when_contains:
            self.failed = False
        elif not any(err in self.raw_result for err in self.failed_when_contains):
            self.failed = False

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            self._record_response_netconf_1_0()
        else:
            self._record_response_netconf_1_1()

        if self.failed:
            self._fetch_error_messages()

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

    def _validate_chunk_size_netconf_1_1(self, result: Tuple[str, bytes]) -> None:
        """
        Validate individual chunk size; handle parsing trailing new lines for chunk sizes

        It seems that some platforms behave slightly differently than others (looking at you IOSXE)
        in the way they count chunk sizes with respect to trailing whitespace. Per my reading of the
        RFC, the response for a netconf 1.1 response should look like this:

        ```
        ##XYZ
        <somexml>
        ##
        ```

        Where "XYZ" is an integer number of the count of chars in the following chunk (the chars up
        to the next "##" symbols), then the actual XML response, then a new line(!!!!) and a pair of
        hash symbols to indicate the chunk is complete.

        IOSXE seems to *not* want to see the newline between the XML payload and the double hash
        symbols... instead when it sees that newline it immediately returns the response. This
        breaks the core behavior of scrapli in that scrapli always writes the input, then reads the
        written inputs off the channel *before* sending a return character. This ensures that we
        never have to deal with stripping out the inputs and such because it has already been read.
        With IOSXE Behaving this way, we have to instead use `send_input` with the `eager` flag set
        -- this means that we do *not* read the inputs, we simply send a return. We then have to do
        a little extra parsing to strip out the inputs, but thats no big deal...

        Where this finally gets to "spacing" -- IOSXE seems to include trailing newlines *sometimes*
        but not other times, whereas IOSXR (for example) *always* counts a single trailing newline
        (after the XML). SO.... long story long... (the above chunk stuff doesn't necessarily matter
        for this, but felt like as good a place to document it as any...) this method deals w/
        newline counts -- we check the expected chunk length against the actual char count, the char
        count with all trailing whitespace stripped, and the count of the chunk + a *single*
        trailing newline character...

        FIN

        Args:
            result: Tuple from re.findall parsing the full response object

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        expected_len = int(result[0])
        result_value = result[1]

        actual_len = len(result_value)
        rstripped_len = len(result_value.rstrip())

        trailing_newline_count = actual_len - rstripped_len
        if trailing_newline_count > 1:
            extraneous_trailing_newline_count = trailing_newline_count - 1
        else:
            extraneous_trailing_newline_count = 1
        trimmed_newline_len = actual_len - extraneous_trailing_newline_count

        if rstripped_len == 0:
            # at least nokia tends to have itty bitty chunks of one element, and/or chunks that have
            # *only* whitespace and our regex ignores this, so if there was/is nothing in the result
            # section we can assume it was just whitespace and move on w/our lives
            actual_len = expected_len

        if expected_len == actual_len:
            return
        if expected_len == rstripped_len:
            return
        if expected_len == trimmed_newline_len:
            return

        LOG.critical(
            f"Return element length invalid, expected {expected_len} got {actual_len} for "
            f"element: {repr(result_value)}"
        )
        self.failed = True

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
        result_sections = re.findall(pattern=CHUNK_MATCH_1_1, string=self.raw_result)

        # validate all received data
        for result in result_sections:
            self._validate_chunk_size_netconf_1_1(result=result)

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

    def _fetch_error_messages(self) -> None:
        """
        Fetch all error messages (if any)

        RFC states that there MAY be more than one rpc-error so we just xpath for all
        "error-message" tags and pull out the text of those elements. The strip is just to remove
        leading/trailing white space to make things look a bit nicer.

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        err_messages = self.xml_result.xpath("//rpc-error/error-message")
        self.error_messages = [err.text.strip() for err in err_messages]

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
        </code>
    </pre>
</details>




## Classes

### NetconfResponse


```text
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
```

<details class="source">
    <summary>
        <span>Expand source code</span>
    </summary>
    <pre>
        <code class="python">
class NetconfResponse(Response):
    # intentionally overriding base class' list of strings for failed when contains
    failed_when_contains: List[bytes]  # type: ignore[assignment]

    def __init__(
        self,
        netconf_version: NetconfVersion,
        xml_input: Element,
        strip_namespaces: bool = True,
        failed_when_contains: Optional[Union[bytes, List[bytes]]] = None,
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

        if failed_when_contains is None:
            # match on both opening and closing tags too so we never have to think about/compare
            # things with namespaces (the closing tags wont have namespaces)
            failed_when_contains = [
                b"</rpc-error>",
                b"</rpc-errors>",
                b"<rpc-error>",
                b"<rpc-errors>",
            ]
        if isinstance(failed_when_contains, bytes):
            failed_when_contains = [failed_when_contains]
        self.failed_when_contains = failed_when_contains

        self.error_messages: List[str] = []

    def record_response(self, result: bytes) -> None:
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

        if not self.failed_when_contains:
            self.failed = False
        elif not any(err in self.raw_result for err in self.failed_when_contains):
            self.failed = False

        if self.netconf_version == NetconfVersion.VERSION_1_0:
            self._record_response_netconf_1_0()
        else:
            self._record_response_netconf_1_1()

        if self.failed:
            self._fetch_error_messages()

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

    def _validate_chunk_size_netconf_1_1(self, result: Tuple[str, bytes]) -> None:
        """
        Validate individual chunk size; handle parsing trailing new lines for chunk sizes

        It seems that some platforms behave slightly differently than others (looking at you IOSXE)
        in the way they count chunk sizes with respect to trailing whitespace. Per my reading of the
        RFC, the response for a netconf 1.1 response should look like this:

        ```
        ##XYZ
        <somexml>
        ##
        ```

        Where "XYZ" is an integer number of the count of chars in the following chunk (the chars up
        to the next "##" symbols), then the actual XML response, then a new line(!!!!) and a pair of
        hash symbols to indicate the chunk is complete.

        IOSXE seems to *not* want to see the newline between the XML payload and the double hash
        symbols... instead when it sees that newline it immediately returns the response. This
        breaks the core behavior of scrapli in that scrapli always writes the input, then reads the
        written inputs off the channel *before* sending a return character. This ensures that we
        never have to deal with stripping out the inputs and such because it has already been read.
        With IOSXE Behaving this way, we have to instead use `send_input` with the `eager` flag set
        -- this means that we do *not* read the inputs, we simply send a return. We then have to do
        a little extra parsing to strip out the inputs, but thats no big deal...

        Where this finally gets to "spacing" -- IOSXE seems to include trailing newlines *sometimes*
        but not other times, whereas IOSXR (for example) *always* counts a single trailing newline
        (after the XML). SO.... long story long... (the above chunk stuff doesn't necessarily matter
        for this, but felt like as good a place to document it as any...) this method deals w/
        newline counts -- we check the expected chunk length against the actual char count, the char
        count with all trailing whitespace stripped, and the count of the chunk + a *single*
        trailing newline character...

        FIN

        Args:
            result: Tuple from re.findall parsing the full response object

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        expected_len = int(result[0])
        result_value = result[1]

        actual_len = len(result_value)
        rstripped_len = len(result_value.rstrip())

        trailing_newline_count = actual_len - rstripped_len
        if trailing_newline_count > 1:
            extraneous_trailing_newline_count = trailing_newline_count - 1
        else:
            extraneous_trailing_newline_count = 1
        trimmed_newline_len = actual_len - extraneous_trailing_newline_count

        if rstripped_len == 0:
            # at least nokia tends to have itty bitty chunks of one element, and/or chunks that have
            # *only* whitespace and our regex ignores this, so if there was/is nothing in the result
            # section we can assume it was just whitespace and move on w/our lives
            actual_len = expected_len

        if expected_len == actual_len:
            return
        if expected_len == rstripped_len:
            return
        if expected_len == trimmed_newline_len:
            return

        LOG.critical(
            f"Return element length invalid, expected {expected_len} got {actual_len} for "
            f"element: {repr(result_value)}"
        )
        self.failed = True

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
        result_sections = re.findall(pattern=CHUNK_MATCH_1_1, string=self.raw_result)

        # validate all received data
        for result in result_sections:
            self._validate_chunk_size_netconf_1_1(result=result)

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

    def _fetch_error_messages(self) -> None:
        """
        Fetch all error messages (if any)

        RFC states that there MAY be more than one rpc-error so we just xpath for all
        "error-message" tags and pull out the text of those elements. The strip is just to remove
        leading/trailing white space to make things look a bit nicer.

        Args:
            N/A

        Returns:
            N/A  # noqa: DAR202

        Raises:
            N/A

        """
        err_messages = self.xml_result.xpath("//rpc-error/error-message")
        self.error_messages = [err.text.strip() for err in err_messages]

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
        </code>
    </pre>
</details>


#### Ancestors (in MRO)
- scrapli.response.Response
#### Class variables

    
`failed_when_contains: List[bytes]`



#### Methods

    

##### genie_parse_output
`genie_parse_output(self) ‑> Union[Dict[str, Any], List[Any]]`

```text
Override scrapli Response `genie_parse_output` method; not applicable for netconf

Args:
    N/A

Returns:
    N/A  # noqa: DAR202

Raises:
    NotImplementedError: always
```



    

##### get_xml_elements
`get_xml_elements(self) ‑> Dict[str, <cyfunction Element at 0x7fb238ace790>]`

```text
Parse each section under "data" into a dict of {tag: Element} for easy viewing/parsing

Args:
    N/A

Returns:
    xml_elements: dictionary of tag: Element

Raises:
    N/A
```



    

##### record_response
`record_response(self, result: bytes) ‑> NoneType`

```text
Record channel_input results and elapsed time of channel input/reading output

Args:
    result: bytes result of channel_input

Returns:
    N/A  # noqa: DAR202

Raises:
    N/A
```



    

##### textfsm_parse_output
`textfsm_parse_output(self, to_dict: bool = True) ‑> Union[Dict[str, Any], List[Any]]`

```text
Override scrapli Response `textfsm_parse_output` method; not applicable for netconf

Args:
    to_dict: ignore, only here to ensure compliance with supertype method

Returns:
    N/A  # noqa: DAR202

Raises:
    NotImplementedError: always
```