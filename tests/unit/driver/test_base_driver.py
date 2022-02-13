import pytest
from lxml import etree

from scrapli.exceptions import ScrapliTypeError, ScrapliValueError
from scrapli_netconf.constants import NetconfClientCapabilities, NetconfVersion, XmlParserVersion
from scrapli_netconf.exceptions import CapabilityNotSupported
from scrapli_netconf.response import NetconfResponse

GET_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get><filter type="subtree"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></filter></get></rpc>]]>]]>"""
GET_CHANNEL_INPUT_1_1 = """#235\n<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get><filter type="subtree"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></filter></get></rpc>\n##"""
GET_CONFIG_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get-config><source><running/></source><filter type="subtree"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></filter></get-config></rpc>]]>]]>"""
GET_CONFIG_CHANNEL_INPUT_1_1 = """#276\n<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get-config><source><running/></source><filter type="subtree"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></filter></get-config></rpc>\n##"""
GET_CONFIG_WITH_DEFAULT_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get-config><source><running/></source><filter type="subtree"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></filter><with-defaults xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-with-defaults">report-all</with-defaults></get-config></rpc>]]>]]>"""
GET_CONFIG_WITH_DEFAULT_CHANNEL_INPUT_1_1 = """#380\n<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get-config><source><running/></source><filter type="subtree"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></filter><with-defaults xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-with-defaults">report-all</with-defaults></get-config></rpc>\n##"""
EDIT_CONFIG_CHANNEL_INPUT_1_0 = """<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><edit-config><target><running/></target><config><cdp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-cdp-cfg"><timer>80</timer><enable>true</enable><log-adjacency/><hold-time>200</hold-time><advertise-v1-only/></cdp></config></edit-config></rpc>]]>]]>"""
EDIT_CONFIG_CHANNEL_INPUT_1_1 = """#351\n<?xml version='1.0' encoding='utf-8'?>
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><edit-config><target><running/></target><config><cdp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-cdp-cfg"><timer>80</timer><enable>true</enable><log-adjacency/><hold-time>200</hold-time><advertise-v1-only/></cdp></config></edit-config></rpc>\n##"""
DELETE_CONFIG_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><delete-config><target><candidate/></target></delete-config></rpc>]]>]]>"""
DELETE_CONFIG_CHANNEL_INPUT_1_1 = """#175\n<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><delete-config><target><candidate/></target></delete-config></rpc>\n##"""
COMMIT_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><commit/></rpc>]]>]]>"""
COMMIT_CHANNEL_INPUT_1_1 = """#124\n<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><commit/></rpc>\n##"""
DISCARD_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><discard-changes/></rpc>]]>]]>"""
DISCARD_CHANNEL_INPUT_1_1 = """#133\n<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><discard-changes/></rpc>\n##"""
LOCK_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><lock><target><running/></target></lock></rpc>]]>]]>"""
LOCK_CHANNEL_INPUT_1_1 = """#155\n<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><lock><target><running/></target></lock></rpc>\n##"""
UNLOCK_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><unlock><target><running/></target></unlock></rpc>]]>]]>"""
UNLOCK_CHANNEL_INPUT_1_1 = """#159\n<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><unlock><target><running/></target></unlock></rpc>\n##"""
RPC_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></rpc>]]>]]>"""
RPC_CHANNEL_INPUT_1_1 = """#192\n<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></rpc>\n##"""
VALIDATE_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><validate><source><candidate/></source></validate></rpc>]]>]]>"""
VALIDATE_CHANNEL_INPUT_1_1 = """#165\n<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><validate><source><candidate/></source></validate></rpc>\n##"""
COPY_CONFIG_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><copy-config><target><startup/></target><source><running/></source></copy-config></rpc>]]>]]>"""
COPY_CONFIG_CHANNEL_INPUT_1_1 = """#196\n<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><copy-config><target><startup/></target><source><running/></source></copy-config></rpc>\n##"""


def test_set_netconf_version_exception(dummy_conn):
    with pytest.raises(ScrapliTypeError):
        dummy_conn.netconf_version = "blah"


def test_client_capabilities(dummy_conn):
    assert dummy_conn.client_capabilities == NetconfClientCapabilities.UNKNOWN
    dummy_conn.client_capabilities = NetconfClientCapabilities.CAPABILITIES_1_0
    assert dummy_conn.client_capabilities == NetconfClientCapabilities.CAPABILITIES_1_0


def test_set_client_capabilities_exception(dummy_conn):
    with pytest.raises(ScrapliTypeError):
        dummy_conn.client_capabilities = "blah"


def test_server_capabilities(dummy_conn):
    assert dummy_conn.server_capabilities == []
    dummy_conn.server_capabilities = ["blah"]
    assert dummy_conn.server_capabilities == ["blah"]


def test_set_server_capabilities_exception(dummy_conn):
    with pytest.raises(ScrapliTypeError):
        dummy_conn.server_capabilities = "blah"


@pytest.mark.parametrize(
    "test_data",
    (
        (None, NetconfVersion.UNKNOWN),
        ("1.0", NetconfVersion.VERSION_1_0),
        ("1.1", NetconfVersion.VERSION_1_1),
    ),
    ids=(
        "none",
        "1.0",
        "1.1",
    ),
)
def test_determine_preferred_netconf_version(dummy_conn, test_data):
    preferred_version_input, preferred_version_output = test_data
    assert (
        dummy_conn._determine_preferred_netconf_version(
            preferred_netconf_version=preferred_version_input
        )
        == preferred_version_output
    )


def test_determine_preferred_netconf_version_exception(dummy_conn):
    with pytest.raises(ScrapliValueError):
        dummy_conn._determine_preferred_netconf_version(preferred_netconf_version="blah")


@pytest.mark.parametrize(
    "test_data",
    (
        (True, XmlParserVersion.COMPRESSED_PARSER),
        (False, XmlParserVersion.STANDARD_PARSER),
    ),
    ids=(
        "compressed",
        "standard",
    ),
)
def test_determine_preferred_xml_parser(dummy_conn, test_data):
    use_compressed_parser, preferred_parser_output = test_data
    assert (
        dummy_conn._determine_preferred_xml_parser(use_compressed_parser=use_compressed_parser)
        == preferred_parser_output
    )


def test_build_readable_datastores(dummy_conn, parsed_server_capabilities_1_1):
    dummy_conn.server_capabilities = parsed_server_capabilities_1_1
    dummy_conn._build_readable_datastores()
    assert dummy_conn.readable_datastores == ["running", "candidate"]


def test_build_writeable_datastores(dummy_conn, parsed_server_capabilities_1_1):
    dummy_conn.server_capabilities = parsed_server_capabilities_1_1
    dummy_conn._build_writeable_datastores()
    assert dummy_conn.writeable_datastores == ["candidate"]


@pytest.mark.parametrize(
    "capabilities",
    [
        ("running", []),
        ("candidate", ["urn:ietf:params:netconf:capability:candidate:1.0"]),
        ("startup", ["urn:ietf:params:netconf:capability:startup:1.0"]),
    ],
    ids=["running", "candidate", "startup"],
)
def test_validate_get_config_target(dummy_conn, capabilities):
    source = capabilities[0]
    server_capabilities = capabilities[1]
    dummy_conn.server_capabilities = server_capabilities
    dummy_conn._build_readable_datastores()
    dummy_conn._validate_get_config_target(source=source)


def test_validate_get_config_target_exception(dummy_conn):
    dummy_conn.strict_datastores = True
    with pytest.raises(ScrapliValueError) as exc:
        dummy_conn._build_readable_datastores()
        dummy_conn._validate_get_config_target(source="tacocat")
    assert str(exc.value) == "'source' should be one of ['running'], got 'tacocat'"


@pytest.mark.parametrize(
    "capabilities",
    [
        ("running", ["urn:ietf:params:netconf:capability:writeable-running:1.0"]),
        ("candidate", ["urn:ietf:params:netconf:capability:candidate:1.0"]),
        ("startup", ["urn:ietf:params:netconf:capability:startup:1.0"]),
    ],
    ids=["running", "candidate", "startup"],
)
def test_validate_edit_config_target(dummy_conn, capabilities):
    target = capabilities[0]
    server_capabilities = capabilities[1]
    dummy_conn.server_capabilities = server_capabilities
    dummy_conn._build_writeable_datastores()
    dummy_conn._validate_edit_config_target(target=target)


def test_validate_edit_config_target_exception(dummy_conn):
    dummy_conn.strict_datastores = True
    with pytest.raises(ScrapliValueError) as exc:
        dummy_conn._build_writeable_datastores()
        dummy_conn._validate_edit_config_target(target="tacocat")
    assert str(exc.value) == "'target' should be one of [], got 'tacocat'"


def test_build_base_elem(dummy_conn):
    elem_one = dummy_conn._build_base_elem()
    elem_two = dummy_conn._build_base_elem()
    assert elem_one.values() == ["101"]
    assert elem_two.values() == ["102"]
    assert (
        etree.tostring(elem_one)
        == b"""<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"/>"""
    )


@pytest.mark.parametrize(
    "test_data",
    [
        (
            "<filterme></filterme>",
            b'<filter type="subtree"><filterme/></filter>',
        ),
        (
            "<filterme></filterme><filtermeagain></filtermeagain>",
            b'<filter type="subtree"><filterme/><filtermeagain/></filter>',
        ),
        (
            "<filter><filterme></filterme></filter>",
            b'<filter type="subtree"><filterme/></filter>',
        ),
    ],
    ids=["single_filter", "multi_filter", "with_filter_tags"],
)
def test_build_subtree_filters(dummy_conn, test_data):
    input_filter, expected_filter = test_data
    assert etree.tostring(dummy_conn._build_filter(filter_=input_filter)) == expected_filter


def test_build_with_defaults(dummy_conn):
    dummy_conn.server_capabilities = ["urn:ietf:params:netconf:capability:with-defaults:1.0"]
    report_all_elem = dummy_conn._build_with_defaults("report-all")
    trim_elem = dummy_conn._build_with_defaults("trim")
    explicit_elem = dummy_conn._build_with_defaults("explicit")
    tagged_elem = dummy_conn._build_with_defaults("report-all-tagged")
    assert (
        etree.tostring(report_all_elem)
        == b"""<with-defaults xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-with-defaults">report-all</with-defaults>"""
    )
    assert (
        etree.tostring(trim_elem)
        == b"""<with-defaults xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-with-defaults">trim</with-defaults>"""
    )
    assert (
        etree.tostring(explicit_elem)
        == b"""<with-defaults xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-with-defaults">explicit</with-defaults>"""
    )
    assert (
        etree.tostring(tagged_elem)
        == b"""<with-defaults xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-with-defaults">report-all-tagged</with-defaults>"""
    )


def test_build_with_defaults_exception_invalid_type(dummy_conn):
    with pytest.raises(ScrapliValueError) as exc:
        dummy_conn._build_with_defaults(default_type="sushicat")
    assert (
        str(exc.value)
        == "'default_type' should be one of report-all|trim|explicit|report-all-tagged, got 'sushicat'"
    )


def test_build_with_defaults_exception_unsupported(dummy_conn):
    dummy_conn.server_capabilities = []
    with pytest.raises(CapabilityNotSupported) as exc:
        dummy_conn._build_with_defaults(default_type="trim")
    assert str(exc.value) == "with-defaults requested, but is not supported by the server"


def test_finalize_channel_input(dummy_conn):
    # test ensures that there are *no* newline characters between end of message and 1.0 delim...
    # see #68 and the original issue #10... #30 is where i broke it again like a jerk, now we write
    # a test like an adult!
    dummy_conn.netconf_version = NetconfVersion.VERSION_1_0
    channel_input = etree.fromstring(b"<something>\navalue</something>")
    finalized_channel_input = dummy_conn._finalize_channel_input(channel_input)
    assert finalized_channel_input.endswith(b"</something>]]>]]>")


def test_build_filters_exception_invalid_type(dummy_conn):
    with pytest.raises(ScrapliValueError) as exc:
        dummy_conn._build_filter(filter_=[], filter_type="tacocat")
    assert str(exc.value) == "'filter_type' should be one of subtree|xpath, got 'tacocat'"


def test_build_filters_exception_unsupported(dummy_conn):
    dummy_conn.server_capabilities = []
    with pytest.raises(CapabilityNotSupported) as exc:
        dummy_conn._build_filter(filter_=[], filter_type="xpath")
    assert str(exc.value) == "xpath filter requested, but is not supported by the server"


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, GET_CHANNEL_INPUT_1_0),
        (NetconfVersion.VERSION_1_1, GET_CHANNEL_INPUT_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_get(dummy_conn, capabilities):
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.readable_datastores = ["running"]
    expected_channel_input = capabilities[1]
    filter_ = """<netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"></netconf-yang>"""
    response = dummy_conn._pre_get(filter_=filter_)
    assert isinstance(response, NetconfResponse)
    assert response.channel_input == expected_channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, GET_CONFIG_CHANNEL_INPUT_1_0),
        (NetconfVersion.VERSION_1_1, GET_CONFIG_CHANNEL_INPUT_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_get_config(dummy_conn, capabilities):
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.readable_datastores = ["running"]
    expected_channel_input = capabilities[1]
    filter_ = """<netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"></netconf-yang>"""
    response = dummy_conn._pre_get_config(filter_=filter_)
    assert isinstance(response, NetconfResponse)
    assert response.channel_input == expected_channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, GET_CONFIG_WITH_DEFAULT_CHANNEL_INPUT_1_0),
        (NetconfVersion.VERSION_1_1, GET_CONFIG_WITH_DEFAULT_CHANNEL_INPUT_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_get_config_with_default(dummy_conn, capabilities):
    dummy_conn.server_capabilities = ["urn:ietf:params:netconf:capability:with-defaults:1.0"]
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.readable_datastores = ["running"]
    expected_channel_input = capabilities[1]
    filter_ = """<netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"></netconf-yang>"""
    default_type_ = "report-all"
    response = dummy_conn._pre_get_config(filter_=filter_, default_type=default_type_)
    assert isinstance(response, NetconfResponse)
    assert response.channel_input == expected_channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, EDIT_CONFIG_CHANNEL_INPUT_1_0),
        (NetconfVersion.VERSION_1_1, EDIT_CONFIG_CHANNEL_INPUT_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_edit_config(dummy_conn, capabilities):
    dummy_conn.server_capabilities = ["urn:ietf:params:netconf:capability:writeable-running:1.0"]
    dummy_conn.writeable_datastores = ["running"]
    dummy_conn.netconf_version = capabilities[0]
    expected_channel_input = capabilities[1]
    config = """<config><cdp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-cdp-cfg">
    <timer>80</timer>
    <enable>true</enable>
    <log-adjacency></log-adjacency>
    <hold-time>200</hold-time>
    <advertise-v1-only></advertise-v1-only>
</cdp></config>"""
    response = dummy_conn._pre_edit_config(config=config)
    assert isinstance(response, NetconfResponse)
    assert response.channel_input == expected_channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, DELETE_CONFIG_CHANNEL_INPUT_1_0),
        (NetconfVersion.VERSION_1_1, DELETE_CONFIG_CHANNEL_INPUT_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_delete_config(dummy_conn, capabilities):
    dummy_conn.server_capabilities = ["urn:ietf:params:netconf:capability:writeable-running:1.0"]
    dummy_conn.writeable_datastores = ["running", "candidate"]
    dummy_conn.netconf_version = capabilities[0]
    expected_channel_input = capabilities[1]
    response = dummy_conn._pre_delete_config(target="candidate")
    assert isinstance(response, NetconfResponse)
    assert response.channel_input == expected_channel_input


def test_pre_delete_config_running(dummy_conn):
    dummy_conn.strict_datastores = True
    dummy_conn.server_capabilities = ["urn:ietf:params:netconf:capability:writeable-running:1.0"]
    dummy_conn.writeable_datastores = ["running", "candidate"]
    with pytest.raises(ScrapliValueError) as exc:
        dummy_conn._pre_delete_config(target="running")
    assert str(exc.value) == "delete-config 'target' may not be 'running'"


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, COMMIT_CHANNEL_INPUT_1_0),
        (NetconfVersion.VERSION_1_1, COMMIT_CHANNEL_INPUT_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_commit(dummy_conn, capabilities):
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.writeable_datastores = ["running"]
    expected_channel_input = capabilities[1]
    response = dummy_conn._pre_commit()
    assert isinstance(response, NetconfResponse)
    assert response.channel_input == expected_channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, ["urn:ietf:params:netconf:capability:confirmed-commit:1.0"]),
        (NetconfVersion.VERSION_1_1, ["urn:ietf:params:netconf:capability:confirmed-commit:1.1"]),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_commit_confirmed(dummy_conn, capabilities):
    """
    Refer to https://datatracker.ietf.org/doc/html/rfc6241#section-8.4.5.1
    for expected XML payload
    """
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.server_capabilities = capabilities[1]
    response = dummy_conn._pre_commit(confirmed=True)
    assert "<commit><confirmed/></commit>" in response.channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, ["urn:ietf:params:netconf:capability:confirmed-commit:1.0"]),
        (NetconfVersion.VERSION_1_1, ["urn:ietf:params:netconf:capability:confirmed-commit:1.1"]),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_commit_confirmed_timeout(dummy_conn, capabilities):
    """
    Refer to https://datatracker.ietf.org/doc/html/rfc6241#section-8.4.5.1
    for expected XML payload
    """
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.server_capabilities = capabilities[1]
    response = dummy_conn._pre_commit(confirmed=True, timeout=60)
    assert "<confirmed/>" in response.channel_input
    assert "<confirm-timeout>60</confirm-timeout>" in response.channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, ["urn:ietf:params:netconf:capability:confirmed-commit:1.0"]),
        (NetconfVersion.VERSION_1_1, ["urn:ietf:params:netconf:capability:confirmed-commit:1.1"]),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_commit_confirmed_timeout_persist(dummy_conn, capabilities):
    """
    Refer to https://datatracker.ietf.org/doc/html/rfc6241#section-8.4.5.1
    for expected XML payload
    """
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.server_capabilities = capabilities[1]
    response = dummy_conn._pre_commit(confirmed=True, timeout=60, persist="foobar1234")
    assert "<confirmed/>" in response.channel_input
    assert "<confirm-timeout>60</confirm-timeout>" in response.channel_input
    assert "<persist>foobar1234</persist>" in response.channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, ["urn:ietf:params:netconf:capability:confirmed-commit:1.0"]),
        (NetconfVersion.VERSION_1_1, ["urn:ietf:params:netconf:capability:confirmed-commit:1.1"]),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_commit_with_persist_id(dummy_conn, capabilities):
    """
    Refer to https://datatracker.ietf.org/doc/html/rfc6241#section-8.4.5.1
    for expected XML payload
    """
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.server_capabilities = capabilities[1]
    response = dummy_conn._pre_commit(persist_id="foobar1234")
    assert "<persist-id>foobar1234</persist-id>" in response.channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, ["urn:ietf:params:netconf:capability:confirmed-commit:1.0"]),
        (NetconfVersion.VERSION_1_1, ["urn:ietf:params:netconf:capability:confirmed-commit:1.1"]),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_commit_fail_persist_id_with_confirmed(dummy_conn, capabilities):
    """
    Refer to https://datatracker.ietf.org/doc/html/rfc6241#section-8.4.5.1
    for expected XML payload
    """
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.server_capabilities = capabilities[1]
    with pytest.raises(ScrapliValueError) as e:
        _ = dummy_conn._pre_commit(confirmed=True, persist_id="foobar1234")


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, ["urn:ietf:params:netconf:capability:confirmed-commit:1.0"]),
        (NetconfVersion.VERSION_1_1, ["urn:ietf:params:netconf:capability:confirmed-commit:1.1"]),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_commit_fail_persist_id_with_persist(dummy_conn, capabilities):
    """
    Refer to https://datatracker.ietf.org/doc/html/rfc6241#section-8.4.5.1
    for expected XML payload
    """
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.server_capabilities = capabilities[1]
    with pytest.raises(ScrapliValueError) as e:
        _ = dummy_conn._pre_commit(persist="foobar1234", persist_id="foobar1234")


@pytest.mark.parametrize(
    "capabilities",
    [
        (
            NetconfVersion.VERSION_1_0,
            ["urn:ietf:params:netconf:capability:confirmed-foo-commit:1.0"],
        ),
        (
            NetconfVersion.VERSION_1_1,
            ["urn:ietf:params:netconf:capability:confirmed-foo-commit:1.1"],
        ),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_commit_fail_confirmed_unsupported_capability(dummy_conn, capabilities):
    """
    Refer to https://datatracker.ietf.org/doc/html/rfc6241#section-8.4.5.1
    for required capabilities
    """
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.server_capabilities = capabilities[1]
    with pytest.raises(CapabilityNotSupported) as e:
        _ = dummy_conn._pre_commit(confirmed=True)


@pytest.mark.parametrize(
    "capabilities",
    [
        (
            NetconfVersion.VERSION_1_0,
            ["urn:ietf:params:netconf:capability:confirmed-foo-commit:1.0"],
        ),
        (
            NetconfVersion.VERSION_1_1,
            ["urn:ietf:params:netconf:capability:confirmed-foo-commit:1.1"],
        ),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_commit_fail_persist_id_unsupported_capability(dummy_conn, capabilities):
    """
    Refer to https://datatracker.ietf.org/doc/html/rfc6241#section-8.4.5.1
    for required capabilities
    """
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.server_capabilities = capabilities[1]
    with pytest.raises(CapabilityNotSupported) as e:
        _ = dummy_conn._pre_commit(persist_id="foobar1234")


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, DISCARD_CHANNEL_INPUT_1_0),
        (NetconfVersion.VERSION_1_1, DISCARD_CHANNEL_INPUT_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_discard(dummy_conn, capabilities):
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.writeable_datastores = ["running"]
    expected_channel_input = capabilities[1]
    response = dummy_conn._pre_discard()
    assert isinstance(response, NetconfResponse)
    assert response.channel_input == expected_channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, LOCK_CHANNEL_INPUT_1_0),
        (NetconfVersion.VERSION_1_1, LOCK_CHANNEL_INPUT_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_lock(dummy_conn, capabilities):
    dummy_conn.server_capabilities = ["urn:ietf:params:netconf:capability:writeable-running:1.0"]
    dummy_conn.writeable_datastores = ["running"]
    dummy_conn.netconf_version = capabilities[0]
    expected_channel_input = capabilities[1]
    response = dummy_conn._pre_lock(target="running")
    assert isinstance(response, NetconfResponse)
    assert response.channel_input == expected_channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, UNLOCK_CHANNEL_INPUT_1_0),
        (NetconfVersion.VERSION_1_1, UNLOCK_CHANNEL_INPUT_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_unlock(dummy_conn, capabilities):
    dummy_conn.server_capabilities = ["urn:ietf:params:netconf:capability:writeable-running:1.0"]
    dummy_conn.writeable_datastores = ["running"]
    dummy_conn.netconf_version = capabilities[0]
    expected_channel_input = capabilities[1]
    response = dummy_conn._pre_unlock(target="running")
    assert isinstance(response, NetconfResponse)
    assert response.channel_input == expected_channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, RPC_CHANNEL_INPUT_1_0),
        (NetconfVersion.VERSION_1_1, RPC_CHANNEL_INPUT_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_rpc(dummy_conn, capabilities):
    dummy_conn.netconf_version = capabilities[0]
    dummy_conn.writeable_datastores = ["running"]
    expected_channel_input = capabilities[1]
    filter_ = """<netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"></netconf-yang>"""
    response = dummy_conn._pre_rpc(filter_=filter_)
    assert isinstance(response, NetconfResponse)
    assert response.channel_input == expected_channel_input


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, VALIDATE_CHANNEL_INPUT_1_0),
        (NetconfVersion.VERSION_1_1, VALIDATE_CHANNEL_INPUT_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_validate(dummy_conn, capabilities):
    dummy_conn.server_capabilities = ["urn:ietf:params:netconf:capability:validate:1.0"]
    dummy_conn.writeable_datastores = ["candidate"]
    dummy_conn.netconf_version = capabilities[0]
    expected_channel_input = capabilities[1]
    response = dummy_conn._pre_validate(source="candidate")
    assert isinstance(response, NetconfResponse)
    assert response.channel_input == expected_channel_input


def test_pre_validate_no_capability(dummy_conn):
    with pytest.raises(CapabilityNotSupported) as exc:
        dummy_conn._pre_validate(source="candidate")
    assert str(exc.value) == "validate requested, but is not supported by the server"


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, COPY_CONFIG_CHANNEL_INPUT_1_0),
        (NetconfVersion.VERSION_1_1, COPY_CONFIG_CHANNEL_INPUT_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_pre_copy_config(dummy_conn, capabilities):
    dummy_conn.server_capabilities = ["urn:ietf:params:netconf:capability:validate:1.0"]
    dummy_conn.writeable_datastores = ["startup"]
    dummy_conn.readable_datastores = ["running"]
    dummy_conn.netconf_version = capabilities[0]
    expected_channel_input = capabilities[1]
    response = dummy_conn._pre_copy_config(source="running", target="startup")
    assert isinstance(response, NetconfResponse)
    assert response.channel_input == expected_channel_input
