import pytest
from lxml import etree

from scrapli_netconf.constants import NetconfVersion
from scrapli_netconf.driver.base_driver import NetconfClientCapabilities
from scrapli_netconf.exceptions import CapabilityNotSupported, CouldNotExchangeCapabilities
from scrapli_netconf.response import NetconfResponse

SERVER_CAPABILITIES_1_0 = b"""<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <capabilities>
        <capability>urn:ietf:params:netconf:base:1.0</capability>
        <capability>urn:ietf:params:netconf:capability:writeable-running:1.0</capability>
        <capability>urn:ietf:params:netconf:capability:rollback-on-error:1.0</capability>
        <capability>urn:ietf:params:netconf:capability:startup:1.0</capability>
        <capability>urn:ietf:params:netconf:capability:url:1.0</capability>
        <capability>urn:cisco:params:netconf:capability:pi-data-model:1.0</capability>
        <capability>urn:cisco:params:netconf:capability:notification:1.0</capability>
    </capabilities>
    <session-id>151399960</session-id>
</hello>]]>]]>"""
PARSED_CAPABILITIES_1_0 = [
    "urn:ietf:params:netconf:base:1.0",
    "urn:ietf:params:netconf:capability:writeable-running:1.0",
    "urn:ietf:params:netconf:capability:rollback-on-error:1.0",
    "urn:ietf:params:netconf:capability:startup:1.0",
    "urn:ietf:params:netconf:capability:url:1.0",
    "urn:cisco:params:netconf:capability:pi-data-model:1.0",
    "urn:cisco:params:netconf:capability:notification:1.0",
]
SERVER_CAPABILITIES_1_1 = b"""<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
 <capabilities>
  <capability>urn:ietf:params:netconf:base:1.1</capability>
  <capability>urn:ietf:params:netconf:capability:candidate:1.0</capability>
  <capability>urn:ietf:params:netconf:capability:rollback-on-error:1.0</capability>
  <capability>urn:ietf:params:netconf:capability:validate:1.1</capability>
  <capability>urn:ietf:params:netconf:capability:confirmed-commit:1.1</capability>
  <capability>urn:ietf:params:netconf:capability:notification:1.0</capability>
  <capability>urn:ietf:params:netconf:capability:interleave:1.0</capability>
 </capabilities>
 <session-id>3671877071</session-id>
</hello>
]]>]]>"""
PARSED_CAPABILITIES_1_1 = [
    "urn:ietf:params:netconf:base:1.1",
    "urn:ietf:params:netconf:capability:candidate:1.0",
    "urn:ietf:params:netconf:capability:rollback-on-error:1.0",
    "urn:ietf:params:netconf:capability:validate:1.1",
    "urn:ietf:params:netconf:capability:confirmed-commit:1.1",
    "urn:ietf:params:netconf:capability:notification:1.0",
    "urn:ietf:params:netconf:capability:interleave:1.0",
]
GET_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get><filter type="subtree"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></filter></get></rpc>\n]]>]]>"""
GET_CHANNEL_INPUT_1_1 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get><filter type="subtree"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></filter></get></rpc>"""
GET_CONFIG_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get-config><source><running/></source><filter type="subtree"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></filter></get-config></rpc>\n]]>]]>"""
GET_CONFIG_CHANNEL_INPUT_1_1 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get-config><source><running/></source><filter type="subtree"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></filter></get-config></rpc>"""
EDIT_CONFIG_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><edit-config><target><running/></target><config><cdp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-cdp-cfg">\n    <timer>80</timer>\n    <enable>true</enable>\n    <log-adjacency/>\n    <hold-time>200</hold-time>\n    <advertise-v1-only/>\n</cdp></config></edit-config></rpc>\n]]>]]>"""
EDIT_CONFIG_CHANNEL_INPUT_1_1 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><edit-config><target><running/></target><config><cdp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-cdp-cfg">\n    <timer>80</timer>\n    <enable>true</enable>\n    <log-adjacency/>\n    <hold-time>200</hold-time>\n    <advertise-v1-only/>\n</cdp></config></edit-config></rpc>"""
DELETE_CONFIG_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><delete-config><target><candidate/></target></delete-config></rpc>\n]]>]]>"""
DELETE_CONFIG_CHANNEL_INPUT_1_1 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><delete-config><target><candidate/></target></delete-config></rpc>"""
COMMIT_CHANNEL_INPUT_1_0 = """<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><commit/></rpc>\n]]>]]>"""
COMMIT_CHANNEL_INPUT_1_1 = (
    """<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><commit/></rpc>"""
)
DISCARD_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><discard-changes/></rpc>\n]]>]]>"""
DISCARD_CHANNEL_INPUT_1_1 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><discard-changes/></rpc>"""
LOCK_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><lock><target><running/></target></lock></rpc>\n]]>]]>"""
LOCK_CHANNEL_INPUT_1_1 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><lock><target><running/></target></lock></rpc>"""
UNLOCK_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><unlock><target><running/></target></unlock></rpc>\n]]>]]>"""
UNLOCK_CHANNEL_INPUT_1_1 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><unlock><target><running/></target></unlock></rpc>"""
RPC_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></rpc>\n]]>]]>"""
RPC_CHANNEL_INPUT_1_1 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg"/></rpc>"""
VALIDATE_CHANNEL_INPUT_1_0 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><validate><source><candidate/></source></validate></rpc>\n]]>]]>"""
VALIDATE_CHANNEL_INPUT_1_1 = """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><validate><source><candidate/></source></validate></rpc>"""


@pytest.mark.parametrize(
    "capabilities",
    [
        (
            SERVER_CAPABILITIES_1_0,
            NetconfVersion.VERSION_1_0,
            NetconfClientCapabilities.CAPABILITIES_1_0,
        ),
        (
            SERVER_CAPABILITIES_1_1,
            NetconfVersion.VERSION_1_1,
            NetconfClientCapabilities.CAPABILITIES_1_1,
        ),
    ],
    ids=["1.0", "1.1"],
)
def test_process_open(dummy_conn, capabilities):
    server_capabilities = capabilities[0]
    expected_netconf_version = capabilities[1]
    expected_client_capabilities = capabilities[2]
    client_capabilities = dummy_conn._process_open(raw_server_capabilities=server_capabilities)
    assert client_capabilities == expected_client_capabilities
    assert dummy_conn.netconf_version == expected_netconf_version


@pytest.mark.parametrize(
    "capabilities",
    [
        (SERVER_CAPABILITIES_1_0, PARSED_CAPABILITIES_1_0),
        (SERVER_CAPABILITIES_1_1, PARSED_CAPABILITIES_1_1),
    ],
    ids=["1.0", "1.1"],
)
def test_parse_server_capabilities(dummy_conn, capabilities):
    server_capabilities = capabilities[0]
    parsed_server_capabilities = capabilities[1]
    dummy_conn._parse_server_capabilities(raw_server_capabilities=server_capabilities)
    assert dummy_conn.server_capabilities == parsed_server_capabilities


def test_parse_server_capabilities_exception(dummy_conn):
    with pytest.raises(CouldNotExchangeCapabilities) as exc:
        dummy_conn._parse_server_capabilities(raw_server_capabilities=b"boo!")
    assert str(exc.value) == "Failed to parse server capabilities from host localhost"


def test_build_readable_datastores(dummy_conn):
    dummy_conn._parse_server_capabilities(raw_server_capabilities=SERVER_CAPABILITIES_1_1)
    dummy_conn._build_readable_datastores()
    assert dummy_conn.readable_datastores == ["running", "candidate"]


def test_build_writeable_datastores(dummy_conn):
    dummy_conn._parse_server_capabilities(raw_server_capabilities=SERVER_CAPABILITIES_1_1)
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
    with pytest.raises(ValueError) as exc:
        dummy_conn._build_readable_datastores()
        dummy_conn._validate_get_config_target(source="tacocat")
    assert str(exc.value) == "`source` should be one of ['running'], got `tacocat`"


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
    with pytest.raises(ValueError) as exc:
        dummy_conn._build_writeable_datastores()
        dummy_conn._validate_edit_config_target(target="tacocat")
    assert str(exc.value) == "`target` should be one of [], got `tacocat`"


def test_build_base_elem(dummy_conn):
    elem_one = dummy_conn._build_base_elem()
    elem_two = dummy_conn._build_base_elem()
    assert elem_one.values() == ["101"]
    assert elem_two.values() == ["102"]
    assert (
        etree.tostring(elem_one)
        == b"""<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"/>"""
    )


def test_build_filters():
    pass


def test_build_filters_exception_invalid_type(dummy_conn):
    with pytest.raises(ValueError) as exc:
        dummy_conn._build_filters(filters=[], filter_type="tacocat")
    assert str(exc.value) == "`filter_type` should be one of subtree|xpath, got `tacocat`"


def test_build_filters_exception_unsupported(dummy_conn):
    dummy_conn.server_capabilities = []
    with pytest.raises(CapabilityNotSupported) as exc:
        dummy_conn._build_filters(filters=[], filter_type="xpath")
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
    response = dummy_conn._pre_get_config(filters=[filter_])
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
    with pytest.raises(ValueError) as exc:
        dummy_conn._pre_delete_config(target="running")
    assert str(exc.value) == "delete-config `target` may not be `running`"


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
