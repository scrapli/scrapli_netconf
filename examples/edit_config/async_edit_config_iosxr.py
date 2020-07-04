import asyncio
import logging

from scrapli_netconf.driver import AsyncNetconfScrape

logging.basicConfig(filename="scrapli.log", level=logging.INFO)
logger = logging.getLogger("scrapli")

IOSXR_DEVICE = {
    "host": "172.18.0.13",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
    "transport": "asyncssh",
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


async def main():
    # create scrapli_netconf connection just like with scrapli, open the connection
    conn = AsyncNetconfScrape(**IOSXR_DEVICE)
    await conn.open()

    # lock the candidate config before starting because why not
    result = await conn.lock(target="candidate")
    print(result.result)

    config = EDIT_INTERFACE_G_0_0_0_0
    result = await conn.edit_config(config=config, target="candidate")
    print(result.result)

    # commit config changes
    result = await conn.commit()
    print(result.result)

    # unlock the candidate now that we're done
    result = await conn.unlock(target="candidate")
    print(result.result)

    # close the session
    await conn.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
