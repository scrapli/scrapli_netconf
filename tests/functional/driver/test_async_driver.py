from pathlib import Path

import pytest

import scrapli_netconf
from scrapli_netconf.response import NetconfResponse

from ...helper import xmldiffs
from ...test_data.devices import CONFIG_REPLACER, INPUTS_OUTPUTS

TEST_DATA_DIR = f"{Path(scrapli_netconf.__file__).parents[1]}/tests/test_data"


@pytest.mark.asyncio
async def test_get_filter_subtree(async_conn):
    conn = async_conn[0]
    device_type = async_conn[1]

    if device_type == "juniper_junos_1_0":
        pytest.skip("juniper get data is retrieved with the 'bare' rpc call")

    await conn.open()

    expected_config_elements = INPUTS_OUTPUTS[device_type].GET_SUBTREE_ELEMENTS
    expected_result = INPUTS_OUTPUTS[device_type].GET_SUBTREE_RESULT
    filter_ = INPUTS_OUTPUTS[device_type].GET_SUBTREE_FILTER

    response = await conn.get(filter_=filter_, filter_type="subtree")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False

    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffs(response.result, expected_result)


@pytest.mark.asyncio
async def test_get_filter_xpath(async_conn):
    conn = async_conn[0]
    device_type = async_conn[1]

    if device_type != "cisco_iosxe_1_1":
        pytest.skip(
            "iosxe with netconf 1.1 is the only test device type supporting xpath filtering"
        )

    await conn.open()

    expected_config_elements = INPUTS_OUTPUTS[device_type].GET_XPATH_ELEMENTS
    expected_result = INPUTS_OUTPUTS[device_type].GET_XPATH_RESULT
    filter_ = INPUTS_OUTPUTS[device_type].GET_XPATH_FILTER

    response = await conn.get(filter_=filter_, filter_type="xpath")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffs(response.result, expected_result)


@pytest.mark.asyncio
async def test_get_config(async_conn):
    conn = async_conn[0]
    device_type = async_conn[1]
    await conn.open()

    config_replacer = CONFIG_REPLACER[device_type]
    expected_config_elements = INPUTS_OUTPUTS[device_type].FULL_GET_CONFIG_ELEMENTS
    expected_config = INPUTS_OUTPUTS[device_type].FULL_GET_CONFIG_RESULT

    response = await conn.get_config()

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffs(config_replacer(response.result), expected_config)


@pytest.mark.asyncio
async def test_get_config_filtered_single_filter_subtree(async_conn):
    conn = async_conn[0]
    device_type = async_conn[1]
    await conn.open()

    config_replacer = CONFIG_REPLACER[device_type]
    expected_config_elements = INPUTS_OUTPUTS[device_type].CONFIG_FILTER_SINGLE_GET_CONFIG_ELEMENTS
    filters = INPUTS_OUTPUTS[device_type].CONFIG_FILTER_SINGLE
    expected_config = INPUTS_OUTPUTS[device_type].CONFIG_FILTER_SINGLE_GET_CONFIG_RESULT

    response = await conn.get_config(filters=filters, filter_type="subtree")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffs(config_replacer(response.result), expected_config)


@pytest.mark.asyncio
async def test_get_config_filtered_multi_filter_subtree(async_conn_1_1):
    # only testing the "multi" filter on 1.1 devices
    conn = async_conn_1_1[0]
    device_type = async_conn_1_1[1]

    await conn.open()

    config_replacer = CONFIG_REPLACER[device_type]
    expected_config_elements = INPUTS_OUTPUTS[device_type].CONFIG_FILTER_MULTI_GET_CONFIG_ELEMENTS
    filters = INPUTS_OUTPUTS[device_type].CONFIG_FILTER_MULTI
    expected_result = INPUTS_OUTPUTS[device_type].CONFIG_FILTER_MULTI_GET_CONFIG_RESULT

    response = await conn.get_config(filters=filters, filter_type="subtree")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffs(config_replacer(response.result), expected_result)


@pytest.mark.asyncio
async def test_get_config_filter_single_filter_xpath(async_conn_1_1):
    conn = async_conn_1_1[0]
    device_type = async_conn_1_1[1]

    if device_type != "cisco_iosxe_1_1":
        pytest.skip(
            "iosxe with netconf 1.1 is the only test device type supporting xpath filtering"
        )

    await conn.open()

    expected_config_elements = INPUTS_OUTPUTS[device_type].GET_CONFIG_XPATH_ELEMENTS
    expected_result = INPUTS_OUTPUTS[device_type].GET_CONFIG_XPATH_RESULT
    filter_ = INPUTS_OUTPUTS[device_type].GET_CONFIG_XPATH_FILTER

    response = await conn.get_config(filters=filter_, filter_type="xpath")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffs(response.result, expected_result)


@pytest.mark.asyncio
async def test_edit_config_and_discard(async_conn):
    conn = async_conn[0]
    device_type = async_conn[1]

    if device_type in ["cisco_iosxe_1_0", "cisco_iosxe_1_1"]:
        pytest.skip("skipping for platforms with no candidate config")

    config_replacer = CONFIG_REPLACER[device_type]
    config = INPUTS_OUTPUTS[device_type].EDIT_CONFIG
    validate_filter = INPUTS_OUTPUTS[device_type].EDIT_CONFIG_VALIDATE_FILTER
    expected_result = INPUTS_OUTPUTS[device_type].EDIT_CONFIG_VALIDATE_EXPECTED

    await conn.open()

    target = "candidate"
    response = await conn.edit_config(config=config, target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert not xmldiffs(
        config_replacer(response.result),
        """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">\n <ok/>\n</rpc-reply>""",
    )

    validation_response = await conn.get_config(
        source=target, filter_type="subtree", filters=validate_filter
    )
    assert isinstance(validation_response, NetconfResponse)
    assert validation_response.failed is False
    assert not xmldiffs(config_replacer(validation_response.result), expected_result)

    discard_response = await conn.discard()
    assert isinstance(discard_response, NetconfResponse)
    assert discard_response.failed is False


@pytest.mark.asyncio
async def test_edit_config_and_commit(async_conn):
    conn = async_conn[0]
    device_type = async_conn[1]

    config_replacer = CONFIG_REPLACER[device_type]
    config = INPUTS_OUTPUTS[device_type].EDIT_CONFIG
    remove_config = INPUTS_OUTPUTS[device_type].REMOVE_EDIT_CONFIG
    validate_filter = INPUTS_OUTPUTS[device_type].EDIT_CONFIG_VALIDATE_FILTER
    expected_result = INPUTS_OUTPUTS[device_type].EDIT_CONFIG_VALIDATE_EXPECTED

    await conn.open()

    target = "running"
    if device_type not in ["cisco_iosxe_1_0", "cisco_iosxe_1_1"]:
        target = "candidate"

    response = await conn.edit_config(config=config, target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert not xmldiffs(
        config_replacer(response.result),
        """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">\n <ok/>\n</rpc-reply>""",
    )

    if device_type not in ["cisco_iosxe_1_0", "cisco_iosxe_1_1"]:
        # no commit for iosxe!
        commit_response = await conn.commit()
        assert isinstance(commit_response, NetconfResponse)
        assert commit_response.failed is False

    validation_response = await conn.get_config(
        source=target, filter_type="subtree", filters=validate_filter
    )
    assert isinstance(validation_response, NetconfResponse)
    assert validation_response.failed is False
    assert not xmldiffs(config_replacer(validation_response.result), expected_result)

    response = await conn.edit_config(config=remove_config, target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False

    if device_type not in ["cisco_iosxe_1_0", "cisco_iosxe_1_1"]:
        # no commit for iosxe!
        commit_response = await conn.commit()
        assert isinstance(commit_response, NetconfResponse)
        assert commit_response.failed is False


@pytest.mark.asyncio
async def test_delete_config(async_conn):
    conn = async_conn[0]
    device_type = async_conn[1]

    if device_type in ["cisco_iosxe_1_0", "cisco_iosxe_1_1", "cisco_iosxr_1_1"]:
        pytest.skip(
            "skipping `delete_config` for iosxe as there is no candidate data store, and "
            "iosxr version used in vrnetlab test environment does not support delete-config"
        )

    config_replacer = CONFIG_REPLACER[device_type]
    config = INPUTS_OUTPUTS[device_type].EDIT_CONFIG

    conn.strip_namespaces = True
    await conn.open()

    target = "candidate"

    _ = await conn.get_config(source=target)

    edit_response = await conn.edit_config(config=config, target=target)
    assert isinstance(edit_response, NetconfResponse)
    assert edit_response.failed is False
    assert not xmldiffs(
        config_replacer(edit_response.result),
        """<rpc-reply message-id="101">\n <ok/>\n</rpc-reply>""",
    )

    response = await conn.delete_config(target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False

    post_delete_config = await conn.get_config(source=target)
    # confirm that the config we got back is empty (since we deleted it!)
    assert post_delete_config.xml_result.xpath("//configuration")[0].text.strip() == ""
    await conn.discard()


@pytest.mark.asyncio
async def test_lock_unlock(async_conn):
    conn = async_conn[0]
    device_type = async_conn[1]

    # stripping namespaces for this check because we dont really care that much about them here
    conn.strip_namespaces = True
    await conn.open()

    target = "candidate"
    if device_type in ["cisco_iosxe_1_0", "cisco_iosxe_1_1"]:
        target = "running"

    response = await conn.lock(target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert not xmldiffs(response.result, """<rpc-reply message-id="101"><ok/></rpc-reply>""")

    response = await conn.unlock(target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert not xmldiffs(response.result, """<rpc-reply message-id="102"><ok/></rpc-reply>""")


@pytest.mark.asyncio
async def test_rpc(async_conn):
    conn = async_conn[0]
    device_type = async_conn[1]

    await conn.open()

    expected_config_elements = INPUTS_OUTPUTS[device_type].RPC_ELEMENTS
    expected_result = INPUTS_OUTPUTS[device_type].RPC_EXPECTED
    filter_ = INPUTS_OUTPUTS[device_type].RPC_FILTER

    response = await conn.rpc(filter_=filter_)

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffs(response.result, expected_result)
