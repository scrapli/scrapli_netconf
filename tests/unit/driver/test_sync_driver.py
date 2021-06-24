from scrapli_netconf.constants import NetconfVersion


def test_get(monkeypatch, dummy_conn):
    monkeypatch.setattr(
        "scrapli_netconf.channel.sync_channel.NetconfChannel.send_input_netconf",
        lambda cls, channel_input: b"<sent!>",
    )
    filter_ = """
<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
    <interface-configuration>
        <active>act</active>
    </interface-configuration>
</interface-configurations>
"""
    dummy_conn.netconf_version = NetconfVersion.VERSION_1_0
    actual_response = dummy_conn.get(filter_=filter_)
    assert actual_response.raw_result == b"<sent!>"
    assert (
        actual_response.channel_input
        == """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get><filter type="subtree"><interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg"><interface-configuration><active>act</active></interface-configuration></interface-configurations></filter></get></rpc>]]>]]>"""
    )


def test_get_config(monkeypatch, dummy_conn):
    monkeypatch.setattr(
        "scrapli_netconf.channel.sync_channel.NetconfChannel.send_input_netconf",
        lambda cls, channel_input: b"<sent!>",
    )
    dummy_conn.netconf_version = NetconfVersion.VERSION_1_0
    dummy_conn.readable_datastores = ["running"]
    actual_response = dummy_conn.get_config()
    assert actual_response.raw_result == b"<sent!>"
    assert (
        actual_response.channel_input
        == """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get-config><source><running/></source></get-config></rpc>]]>]]>"""
    )
