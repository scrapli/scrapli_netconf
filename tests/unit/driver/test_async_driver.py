import pytest

from scrapli_netconf.constants import NetconfVersion


@pytest.mark.asyncio
async def test_get(monkeypatch, dummy_async_conn):
    async def dummy_send_input_netconf(cls, channel_input):
        return b"<sent!>"

    monkeypatch.setattr(
        "scrapli_netconf.channel.async_channel.AsyncNetconfChannel.send_input_netconf",
        dummy_send_input_netconf,
    )
    filter_ = """
<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
    <interface-configuration>
        <active>act</active>
    </interface-configuration>
</interface-configurations>
"""
    dummy_async_conn.netconf_version = NetconfVersion.VERSION_1_0
    actual_response = await dummy_async_conn.get(filter_=filter_)
    assert actual_response.raw_result == b"<sent!>"
    assert (
        actual_response.channel_input
        == """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get><filter type="subtree"><interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg"><interface-configuration><active>act</active></interface-configuration></interface-configurations></filter></get></rpc>]]>]]>"""
    )


@pytest.mark.asyncio
async def test_get_config(monkeypatch, dummy_async_conn):
    async def dummy_send_input_netconf(cls, channel_input):
        return b"<sent!>"

    monkeypatch.setattr(
        "scrapli_netconf.channel.async_channel.AsyncNetconfChannel.send_input_netconf",
        dummy_send_input_netconf,
    )
    dummy_async_conn.netconf_version = NetconfVersion.VERSION_1_0
    dummy_async_conn.readable_datastores = ["running"]
    actual_response = await dummy_async_conn.get_config()
    assert actual_response.raw_result == b"<sent!>"
    assert (
        actual_response.channel_input
        == """<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><get-config><source><running/></source></get-config></rpc>]]>]]>"""
    )
