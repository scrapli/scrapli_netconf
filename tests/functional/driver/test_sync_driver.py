import pytest

from scrapli_netconf.response import NetconfResponse


def test_get_filter_subtree(sync_conn, test_cases, xmldiffer):
    conn = sync_conn[0]
    device_type = sync_conn[1]

    if device_type == "juniper_junos_1_0":
        pytest.skip("juniper get data is retrieved with the 'bare' rpc call")

    conn.open()

    expected_config_elements = test_cases[device_type]["get_filter_subtree"][
        "expected_config_elements"
    ]
    expected_result = test_cases[device_type]["get_filter_subtree"]["expected_output"]
    filter_ = test_cases[device_type]["get_filter_subtree"]["filter_"]

    response = conn.get(filter_=filter_, filter_type="subtree")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffer(response.result, expected_result)


def test_get_filter_xpath(sync_conn, test_cases, xmldiffer):
    conn = sync_conn[0]
    device_type = sync_conn[1]

    if device_type != "cisco_iosxe_1_1":
        pytest.skip(
            "iosxe with netconf 1.1 is the only test device type supporting xpath filtering"
        )

    conn.open()

    expected_config_elements = test_cases[device_type]["get_filter_xpath"][
        "expected_config_elements"
    ]
    expected_result = test_cases[device_type]["get_filter_xpath"]["expected_output"]
    filter_ = test_cases[device_type]["get_filter_xpath"]["filter_"]

    response = conn.get(filter_=filter_, filter_type="xpath")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffer(response.result, expected_result)


def test_get_config(sync_conn, test_cases, config_replacer_dict, xmldiffer):
    conn = sync_conn[0]
    device_type = sync_conn[1]
    conn.open()

    config_replacer = config_replacer_dict[device_type]
    expected_config_elements = test_cases[device_type]["get_config"]["expected_config_elements"]
    expected_result = test_cases[device_type]["get_config"]["expected_output"]

    response = conn.get_config()

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffer(config_replacer(response.result), expected_result)


def test_get_config_filtered_single_filter_subtree(
    sync_conn, test_cases, config_replacer_dict, xmldiffer
):
    conn = sync_conn[0]
    device_type = sync_conn[1]
    conn.open()

    config_replacer = config_replacer_dict[device_type]
    expected_config_elements = test_cases[device_type]["get_config_filtered_single"][
        "expected_config_elements"
    ]
    expected_result = test_cases[device_type]["get_config_filtered_single"]["expected_output"]
    filter_ = test_cases[device_type]["get_config_filtered_single"]["filter_"]

    response = conn.get_config(filter_=filter_, filter_type="subtree")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffer(config_replacer(response.result), expected_result)


def test_get_config_filtered_multi_filter_subtree(
    sync_conn_1_1, test_cases, config_replacer_dict, xmldiffer
):
    # only testing the "multi" filter on 1.1 devices
    conn = sync_conn_1_1[0]
    device_type = sync_conn_1_1[1]

    conn.open()

    config_replacer = config_replacer_dict[device_type]
    expected_config_elements = test_cases[device_type]["get_config_filtered_multi"][
        "expected_config_elements"
    ]
    expected_result = test_cases[device_type]["get_config_filtered_multi"]["expected_output"]
    filter_ = test_cases[device_type]["get_config_filtered_multi"]["filter_"]

    response = conn.get_config(filter_=filter_, filter_type="subtree")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffer(config_replacer(response.result), expected_result)


def test_get_config_filter_single_filter_xpath(sync_conn_1_1, test_cases, xmldiffer):
    conn = sync_conn_1_1[0]
    device_type = sync_conn_1_1[1]

    if device_type != "cisco_iosxe_1_1":
        pytest.skip(
            "iosxe with netconf 1.1 is the only test device type supporting xpath filtering"
        )

    conn.open()

    expected_config_elements = test_cases[device_type]["get_config_filtered_xpath"][
        "expected_config_elements"
    ]
    expected_result = test_cases[device_type]["get_config_filtered_xpath"]["expected_output"]
    filter_ = test_cases[device_type]["get_config_filtered_xpath"]["filter_"]

    response = conn.get_config(filter_=filter_, filter_type="xpath")

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffer(response.result, expected_result)


def test_edit_config_and_discard(sync_conn, test_cases, config_replacer_dict, xmldiffer):
    conn = sync_conn[0]
    device_type = sync_conn[1]

    if device_type in ["cisco_iosxe_1_0", "cisco_iosxe_1_1"]:
        pytest.skip("skipping for platforms with no candidate config")

    config_replacer = config_replacer_dict[device_type]
    config = test_cases[device_type]["edit_config"]["config"]
    expected_result = test_cases[device_type]["edit_config"]["expected_output"]
    validate_filter = test_cases[device_type]["edit_config"]["validate_config_filter"]

    conn.open()

    target = "candidate"
    response = conn.edit_config(config=config, target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert not xmldiffer(
        config_replacer(response.result),
        """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">\n <ok/>\n</rpc-reply>""",
    )

    validation_response = conn.get_config(
        source=target, filter_type="subtree", filter_=validate_filter
    )
    assert isinstance(validation_response, NetconfResponse)
    assert validation_response.failed is False
    assert not xmldiffer(config_replacer(validation_response.result), expected_result)

    discard_response = conn.discard()
    assert isinstance(discard_response, NetconfResponse)
    assert discard_response.failed is False


def test_edit_config_and_commit(sync_conn, test_cases, config_replacer_dict, xmldiffer):
    conn = sync_conn[0]
    device_type = sync_conn[1]

    config_replacer = config_replacer_dict[device_type]
    config = test_cases[device_type]["edit_config"]["config"]
    remove_config = test_cases[device_type]["edit_config"]["remove_config"]
    expected_result = test_cases[device_type]["edit_config"]["expected_output"]
    validate_filter = test_cases[device_type]["edit_config"]["validate_config_filter"]

    conn.open()

    target = "running"
    if device_type not in ["cisco_iosxe_1_0", "cisco_iosxe_1_1"]:
        target = "candidate"

    response = conn.edit_config(config=config, target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert not xmldiffer(
        config_replacer(response.result),
        """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">\n <ok/>\n</rpc-reply>""",
    )

    if device_type not in ["cisco_iosxe_1_0", "cisco_iosxe_1_1"]:
        # no commit for iosxe!
        commit_response = conn.commit()
        assert isinstance(commit_response, NetconfResponse)
        assert commit_response.failed is False

    validation_response = conn.get_config(
        source=target, filter_type="subtree", filter_=validate_filter
    )
    assert isinstance(validation_response, NetconfResponse)
    assert validation_response.failed is False
    assert not xmldiffer(config_replacer(validation_response.result), expected_result)

    response = conn.edit_config(config=remove_config, target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False

    if device_type not in ["cisco_iosxe_1_0", "cisco_iosxe_1_1"]:
        # no commit for iosxe!
        commit_response = conn.commit()
        assert isinstance(commit_response, NetconfResponse)
        assert commit_response.failed is False


def test_delete_config(sync_conn, test_cases, config_replacer_dict, xmldiffer):
    conn = sync_conn[0]
    device_type = sync_conn[1]

    if device_type in ["cisco_iosxe_1_0", "cisco_iosxe_1_1", "cisco_iosxr_1_1"]:
        pytest.skip(
            "skipping `delete_config` for iosxe as there is no candidate data store, and "
            "iosxr version used in vrnetlab test environment does not support delete-config"
        )

    config_replacer = config_replacer_dict[device_type]
    config = test_cases[device_type]["edit_config"]["config"]

    conn.strip_namespaces = True
    conn.open()

    target = "candidate"

    _ = conn.get_config(source=target)

    response = conn.edit_config(config=config, target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert not xmldiffer(
        config_replacer(response.result),
        """<rpc-reply message-id="101">\n <ok/>\n</rpc-reply>""",
    )

    response = conn.delete_config(target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False

    post_delete_config = conn.get_config(source=target)
    # confirm that the config we got back is empty (since we deleted it!)
    assert post_delete_config.xml_result.xpath("//configuration")[0].text.strip() == ""
    conn.discard()


def test_lock_unlock(sync_conn, xmldiffer):
    conn = sync_conn[0]
    device_type = sync_conn[1]

    # stripping namespaces for this check because we dont really care that much about them here
    conn.strip_namespaces = True
    conn.open()

    target = "candidate"
    if device_type in ["cisco_iosxe_1_0", "cisco_iosxe_1_1"]:
        target = "running"

    response = conn.lock(target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert not xmldiffer(response.result, """<rpc-reply message-id="101"><ok/></rpc-reply>""")

    response = conn.unlock(target=target)
    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert not xmldiffer(response.result, """<rpc-reply message-id="102"><ok/></rpc-reply>""")


def test_rpc(sync_conn, test_cases, xmldiffer):
    conn = sync_conn[0]
    device_type = sync_conn[1]

    conn.open()

    expected_config_elements = test_cases[device_type]["rpc"]["expected_config_elements"]
    expected_result = test_cases[device_type]["rpc"]["expected_output"]
    filter_ = test_cases[device_type]["rpc"]["filter_"]

    response = conn.rpc(filter_=filter_)

    assert isinstance(response, NetconfResponse)
    assert response.failed is False
    assert all(
        elem in list(response.get_xml_elements().keys()) for elem in expected_config_elements
    )
    assert not xmldiffer(response.result, expected_result)
