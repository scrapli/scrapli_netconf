import logging

from scrapli_netconf.driver import NetconfScrape

logging.basicConfig(filename="scrapli.log", level=logging.INFO)
logger = logging.getLogger("scrapli")

JUNOS_DEVICE = {
    "host": "172.18.0.15",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
    "transport": "system",
    "timeout_ops": 10,
    "timeout_transport": 10,
    "port": 22,
}


CONFIG_FILTER = """
<configuration>
    <interfaces>
    </interfaces>
    <system>
        <services>
            <ssh>
            </ssh>
        </services>
    </system>    
</configuration>
"""

COMMIT_FILTER = """
<get-commit-revision-information>
    <level>detail</level>
</get-commit-revision-information>
"""

EDIT_NETCONF = """
<config>
    <configuration>
        <system>
            <services>
                <netconf>
                    <ssh>
                        <port>22</port>
                    </ssh>
                </netconf>
            </services>
        </system>    
    </configuration>
</config>
"""

EDIT_MULTIPLE = """
<config>
    <configuration>
        <system>
            <login>
                <user>
                    <name>scrapli</name>
                    <uid>9999</uid>
                </user>
            </login>
            <services>
                <netconf>
                    <ssh>
                        <port>22</port>
                    </ssh>
                </netconf>
            </services>        
        </system>    
    </configuration>
</config>
"""


def main():
    # create scrapli_netconf connection just like with scrapli, open the connection
    conn = NetconfScrape(**JUNOS_DEVICE)
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

    # get the whole config, but apply some filters (subtree filters) in the case of junos since its
    # just a config, not a model and we are filtering for things under `configuration` this has to
    # live in a single filter unlike iosxr
    result = conn.get_config(filters=CONFIG_FILTER)
    print(result.result)

    # get some operational data via "rpc" for juniper style rpc calls; note the `filter_` to
    # not reuse builtins
    result = conn.rpc(filter_=COMMIT_FILTER)
    print(result.result)

    # edit the candidate configuration
    result = conn.edit_config(config=EDIT_NETCONF, target="candidate")
    print(result.result)

    # commit config changes
    conn.commit()
    print(result.result)

    # edit multiple config elements
    result = conn.edit_config(config=EDIT_MULTIPLE, target="candidate")
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
