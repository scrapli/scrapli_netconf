"""async_edit_config_iosxr"""
from scrapli_netconf.driver import NetconfScrape

IOSXR_DEVICE = {
    "host": "172.18.0.13",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
}

EDIT_INTERFACE_G_0_0_0_0 = """
<config>
  <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
    <interface-configuration>
      <active>act</active>
      <interface-name>GigabitEthernet0/0/0/0</interface-name>
      <description>skfasjdlkfjdsf</description>
      <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
        <addresses>
          <primary>
            <address>10.10.0.1</address>
            <netmask>255.255.255.0</netmask>
          </primary>
        </addresses>
      </ipv4-network>
    </interface-configuration>
  </interface-configurations>
</config>
"""


def main():
    """Edit config example"""
    # create scrapli_netconf connection just like with scrapli, open the connection
    conn = NetconfScrape(**IOSXR_DEVICE)
    conn.open()

    # lock the candidate config before starting because why not
    result = conn.lock(target="candidate")
    print(result.result)

    config = EDIT_INTERFACE_G_0_0_0_0
    result = conn.edit_config(config=config, target="candidate")
    print(result.result)

    # commit config changes
    conn.commit()
    print(result.result)

    # unlock the candidate now that we're done
    result = conn.unlock(target="candidate")
    print(result.result)

    # close the session
    conn.close()


if __name__ == "__main__":
    main()
