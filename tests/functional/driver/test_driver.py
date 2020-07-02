import pytest

from scrapli_netconf.response import NetconfResponse

from ...helper import xmldiffs
from ...test_data.devices import CONFIG_REPLACER, INPUTS_OUTPUTS


def test_get_filter_subtree(sync_conn):
    conn = sync_conn[0]
    device_type = sync_conn[1]

    # TODO juniper
    if device_type == "juniper_junos_1_0":
        pytest.skip("need to add junos tests here!")

    conn.open()

    expected_config_elements = INPUTS_OUTPUTS[device_type].GET_SUBTREE_ELEMENTS
    expected_result = INPUTS_OUTPUTS[device_type].GET_SUBTREE_RESULT
    filter_ = INPUTS_OUTPUTS[device_type].GET_SUBTREE_FILTER

    response = conn.get(filter_=filter_, filter_type="subtree")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffs(response.result, expected_result)


# def test_get_filter_xpath(sync_conn):
#     # TODO do any of these platforms actually support xpath?
#     pass


def test_get_config(sync_conn):
    conn = sync_conn[0]
    device_type = sync_conn[1]
    conn.open()

    config_replacer = CONFIG_REPLACER[device_type]
    expected_config_elements = INPUTS_OUTPUTS[device_type].FULL_GET_CONFIG_ELEMENTS
    expected_result = INPUTS_OUTPUTS[device_type].FULL_GET_CONFIG_RESULT

    response = conn.get_config()

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffs(config_replacer(response.result), expected_result)


def test_get_config_filtered_single_filter_subtree(sync_conn):
    conn = sync_conn[0]
    device_type = sync_conn[1]
    conn.open()

    config_replacer = CONFIG_REPLACER[device_type]
    expected_config_elements = INPUTS_OUTPUTS[device_type].CONFIG_FILTER_SINGLE_GET_CONFIG_ELEMENTS
    filters = INPUTS_OUTPUTS[device_type].CONFIG_FILTER_SINGLE
    expected_result = INPUTS_OUTPUTS[device_type].CONFIG_FILTER_SINGLE_GET_CONFIG_RESULT

    response = conn.get_config(filters=filters, filter_type="subtree")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffs(config_replacer(response.result), expected_result)


def test_get_config_filtered_multi_filter_subtree(sync_conn):
    conn = sync_conn[0]
    device_type = sync_conn[1]
    conn.open()

    # TODO juniper and iosxe
    if device_type != "cisco_iosxr_1_1":
        pytest.skip("need to add iosxe/junos tests here!")

    config_replacer = CONFIG_REPLACER[device_type]
    expected_config_elements = INPUTS_OUTPUTS[device_type].CONFIG_FILTER_MULTI_GET_CONFIG_ELEMENTS
    filters = INPUTS_OUTPUTS[device_type].CONFIG_FILTER_MULTI
    expected_result = INPUTS_OUTPUTS[device_type].CONFIG_FILTER_MULTI_GET_CONFIG_RESULT

    response = conn.get_config(filters=filters, filter_type="subtree")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffs(config_replacer(response.result), expected_result)


# def test_get_config_filter_single_filter_xpath(sync_conn):
#     # TODO do any of these platforms actually support xpath?
#     pass


# def test_get_config_filter_multi_filter_xpath(sync_conn):
#     # TODO do any of these platforms actually support xpath? and if they do is there a "multi"
#     #  xpath filter option, i dont think so?
#     pass


def test_edit_config_single_config(sync_conn):
    conn = sync_conn[0]
    device_type = sync_conn[1]

    if device_type != "cisco_iosxr_1_1":
        pytest.skip("skipping edit config on iosxe for now!")

    configs = INPUTS_OUTPUTS[device_type].EDIT_CONFIG_SINGLE
    validate_filter = INPUTS_OUTPUTS[device_type].EDIT_CONFIG_SINGLE_VALIDATE_FILTER
    expected_result = INPUTS_OUTPUTS[device_type].EDIT_CONFIG_SINGLE_VALIDATE_EXPECTED

    conn.open()

    target = "candidate"
    if device_type == "cisco_iosxe_1_0":
        # TODO maybe skip and have a test just for iosxe cuz of no candidate? also maybe just
        #  upgrade iosxe in the lab to the new 16.X w/ actual netconfyang support
        target = "running"

    response = conn.edit_config(configs=configs, target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert not xmldiffs(
        response.result,
        """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">\n <ok/>\n</rpc-reply>""",
    )

    validation_response = conn.get_config(
        source=target, filter_type="subtree", filters=validate_filter
    )
    assert isinstance(validation_response, NetconfResponse)
    assert validation_response.failed is False
    assert not xmldiffs(validation_response.result, expected_result)

    discard_response = conn.discard()
    assert isinstance(discard_response, NetconfResponse)
    assert discard_response.failed is False


# def test_commit(sync_conn):
#     pass


# def test_discard(sync_conn):
#     pass


def test_lock_unlock(sync_conn):
    conn = sync_conn[0]
    device_type = sync_conn[1]

    # stripping namespaces for this check because we dont really care that much about them here
    conn.strip_namespaces = True
    conn.open()

    target = "candidate"
    if device_type == "cisco_iosxe_1_0":
        target = "running"

    response = conn.lock(target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert not xmldiffs(response.result, """<rpc-reply message-id="101"><ok/></rpc-reply>""")

    response = conn.unlock(target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert not xmldiffs(response.result, """<rpc-reply message-id="102"><ok/></rpc-reply>""")


# def test_rpc(sync_conn):
#     pass
