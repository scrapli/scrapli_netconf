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

EDIT_INTERFACE_G_0_0_0_0 = """
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
"""

EDIT_INTERFACE_G_0_0_0_1 = """
<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
  <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/1</interface-name>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
      <addresses>
        <primary>
          <address>10.10.1.1</address>
          <netmask>255.255.255.0</netmask>
        </primary>
      </addresses>
    </ipv4-network>
  </interface-configuration>
</interface-configurations>
"""


def main():
    # create scrapli_netconf connection just like with scrapli, open the connection
    conn = NetconfScrape(**IOSXR_DEVICE)
    conn.open()

    # lock the candidate config before starting because why not
    result = conn.lock(target="candidate")
    print(result.result)

    # edit multiple elements of the config -- note you can do this in one big xml, or pass a list
    # of things to edit
    configs = [EDIT_INTERFACE_G_0_0_0_0]  # , EDIT_INTERFACE_G_0_0_0_1]
    result = conn.edit_config(configs=configs, target="candidate")
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
