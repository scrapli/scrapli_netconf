import logging

from scrapli_netconf.driver import NetconfScrape

logging.basicConfig(filename="scrapli.log", level=logging.INFO)
logger = logging.getLogger("scrapli")

IOSXR_DEVICE = {
    "host": "172.18.0.13",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
}

INTERFACE_ACTIVE_FILTER = """
<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
    <interface-configuration>
        <active>act</active>
    </interface-configuration>
</interface-configurations>
"""

NETCONF_YANG_FILTER = """
<netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg">
</netconf-yang>
"""

PLATFORM_FILTER = """
<components xmlns="http://openconfig.net/yang/platform">
    <component>
        <state>
        </state>
    </component>
</components>
"""

EDIT_CDP = """
<config>
    <cdp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-cdp-cfg">
        <timer>80</timer>
        <enable>true</enable>
        <log-adjacency></log-adjacency>
        <hold-time>200</hold-time>
        <advertise-v1-only></advertise-v1-only>
    </cdp>
</config>
"""

EDIT_BANNER = """
<config>
    <banners xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-infra-infra-cfg">
        <banner>
          <banner-name>motd</banner-name>
          <banner-text>somestupidbanner</banner-text>
        </banner>
    </banners>
</config>
"""


def main():
    # create scrapli_netconf connection just like with scrapli, open the connection
    conn = NetconfScrape(**IOSXR_DEVICE)
    conn.open()

    # lock the candidate config before starting because why not
    result = conn.lock(target="candidate")
    print(result.result)

    # get the whole config; just like scrapli the result is a `Response` object, in this case a
    # `NetconfResponse` object with some additional methods
    result = conn.get_config()
    # print xml text result
    print(result.result)
    # print xml element result
    print(result.xml_result)

    # get the whole config, but apply some filters (subtree filters)
    filters = [INTERFACE_ACTIVE_FILTER, NETCONF_YANG_FILTER]
    result = conn.get_config(filters=filters)
    print(result.result)

    # get something other than the config; note the `filter_` to not reuse builtins
    result = conn.get(filter_=PLATFORM_FILTER)
    print(result.result)

    # edit the candidate configuration
    result = conn.edit_config(config=EDIT_CDP, target="candidate")
    print(result.result)

    # commit config changes
    conn.commit()
    print(result.result)

    # stage a config we'll discard
    config = EDIT_BANNER
    result = conn.edit_config(config=config, target="candidate")
    print(result.result)

    # discard this config change
    result = conn.discard()
    print(result.result)

    # unlock the candidate now that we're done
    result = conn.unlock(target="candidate")
    print(result.result)

    # close the session
    conn.close()


if __name__ == "__main__":
    main()
