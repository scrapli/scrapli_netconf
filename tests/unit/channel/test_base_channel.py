import pytest

from scrapli_netconf.constants import NetconfVersion


def test_restructure_output(dummy_conn):
    output = dummy_conn.channel._restructure_output(output=b"tacocat")
    assert output == b"tacocat"


@pytest.mark.parametrize(
    "capabilities",
    [
        (NetconfVersion.VERSION_1_0, "<tacocat/>", "<tacocat/>"),
        (NetconfVersion.VERSION_1_1, "<tacocat/>", "#10\n<tacocat/>\n##"),
    ],
    ids=["1.0", "1.1"],
)
def test_build_message(dummy_conn, capabilities):
    dummy_conn.channel.netconf_version = capabilities[0]
    channel_input = capabilities[1]
    expected_final_channel_input = capabilities[2]
    final_channel_input = dummy_conn.channel._build_message(channel_input=channel_input)
    assert final_channel_input == expected_final_channel_input


@pytest.mark.parametrize(
    "capabilities",
    [(NetconfVersion.VERSION_1_0, "]]>]]>"), (NetconfVersion.VERSION_1_1, r"^##$")],
    ids=["1.0", "1.1"],
)
def test_post_send_client_capabilities(dummy_conn, capabilities):
    netconf_version = capabilities[0]
    expected_prompt_pattern = capabilities[1]
    dummy_conn.channel._post_send_client_capabilities(capabilities_version=netconf_version)
    assert dummy_conn.channel.comms_prompt_pattern == expected_prompt_pattern
