FULL_GET_CONFIG_ELEMENTS = ["configuration"]

FULL_GET_CONFIG_RESULT = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/17.3R2/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
<data>
<configuration xmlns="http://xml.juniper.net/xnm/1.1/xnm" timestamp="TIMESTAMP" junos:commit-user="vrnetlab">
    <version>17.3R2.10</version>
    <system>
        <root-authentication>
            PASSWORD
        </root-authentication>
        <login>
            <user>
                <name>vrnetlab</name>
                <uid>2000</uid>
                <class>super-user</class>
                <authentication>
                    PASSWORD
                </authentication>
            </user>
        </login>
        <services>
            <ssh>
                <protocol-version>v2</protocol-version>
            </ssh>
            <telnet>
            </telnet>
            <netconf>
                <ssh>
                </ssh>
            </netconf>
            <web-management>
                <http>
                    <interface>fxp0.0</interface>
                </http>
            </web-management>
        </services>
        <syslog>
            <user>
                <name>*</name>
                <contents>
                    <name>any</name>
                    <emergency/>
                </contents>
            </user>
            <file>
                <name>messages</name>
                <contents>
                    <name>any</name>
                    <any/>
                </contents>
                <contents>
                    <name>authorization</name>
                    <info/>
                </contents>
            </file>
            <file>
                <name>interactive-commands</name>
                <contents>
                    <name>interactive-commands</name>
                    <any/>
                </contents>
            </file>
        </syslog>
        <license>
            <autoupdate>
                <url>
                    <name>https://ae1.juniper.net/junos/key_retrieval</name>
                </url>
            </autoupdate>
        </license>
    </system>
    <security>
        <screen>
            <ids-option>
                <name>untrust-screen</name>
                <icmp>
                    <ping-death/>
                </icmp>
                <ip>
                    <source-route-option/>
                    <tear-drop/>
                </ip>
                <tcp>
                    <syn-flood>
                        <alarm-threshold>1024</alarm-threshold>
                        <attack-threshold>200</attack-threshold>
                        <source-threshold>1024</source-threshold>
                        <destination-threshold>2048</destination-threshold>
                        <undocumented><queue-size>2000</queue-size></undocumented>
                        <timeout>20</timeout>
                    </syn-flood>
                    <land/>
                </tcp>
            </ids-option>
        </screen>
        <policies>
            <policy>
                <from-zone-name>trust</from-zone-name>
                <to-zone-name>trust</to-zone-name>
                <policy>
                    <name>default-permit</name>
                    <match>
                        <source-address>any</source-address>
                        <destination-address>any</destination-address>
                        <application>any</application>
                    </match>
                    <then>
                        <permit>
                        </permit>
                    </then>
                </policy>
            </policy>
            <policy>
                <from-zone-name>trust</from-zone-name>
                <to-zone-name>untrust</to-zone-name>
                <policy>
                    <name>default-permit</name>
                    <match>
                        <source-address>any</source-address>
                        <destination-address>any</destination-address>
                        <application>any</application>
                    </match>
                    <then>
                        <permit>
                        </permit>
                    </then>
                </policy>
            </policy>
        </policies>
        <zones>
            <security-zone>
                <name>trust</name>
                <tcp-rst/>
            </security-zone>
            <security-zone>
                <name>untrust</name>
                <screen>untrust-screen</screen>
            </security-zone>
        </zones>
    </security>
    <interfaces>
        <interface>
            <name>fxp0</name>
            <unit>
                <name>0</name>
                <family>
                    <inet>
                        <address>
                            <name>10.0.0.15/24</name>
                        </address>
                    </inet>
                </family>
            </unit>
        </interface>
    </interfaces>
</configuration>
</data>
</rpc-reply>"""

CONFIG_FILTER_SINGLE = """
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

CONFIG_FILTER_SINGLE_GET_CONFIG_ELEMENTS = ["configuration"]

CONFIG_FILTER_SINGLE_GET_CONFIG_RESULT = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/17.3R2/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
<data>
<configuration xmlns="http://xml.juniper.net/xnm/1.1/xnm" timestamp="TIMESTAMP" junos:commit-user="vrnetlab">
    <interfaces>
        <interface>
            <name>fxp0</name>
            <unit>
                <name>0</name>
                <family>
                    <inet>
                        <address>
                            <name>10.0.0.15/24</name>
                        </address>
                    </inet>
                </family>
            </unit>
        </interface>
    </interfaces>
    <system>
        <services>
            <ssh>
                <protocol-version>v2</protocol-version>
            </ssh>
        </services>
    </system>
</configuration>
</data>
</rpc-reply>"""

_CONFIG_FILTER_MULTI = """
<configuration>
    <system>
        <syslog>
            <user>
            </user>
        </syslog>
    </system>    
</configuration>
"""

CONFIG_FILTER_MULTI = [CONFIG_FILTER_SINGLE, _CONFIG_FILTER_MULTI]

CONFIG_FILTER_MULTI_GET_CONFIG_ELEMENTS = ["configuration"]

CONFIG_FILTER_MULTI_GET_CONFIG_RESULT = """"""

EDIT_CONFIG = """
<config>
  <configuration>
    <interfaces>
        <interface>
            <name>ge-0/0/0</name>
            <description>scrapli was here</description>
        </interface>
    </interfaces>
  </configuration>
</config>"""

REMOVE_EDIT_CONFIG = """
<config>
  <configuration>
    <interfaces>
        <interface>
            <name>ge-0/0/0</name>
            <description operation="delete"></description>
        </interface>
    </interfaces>
  </configuration>
</config>"""

EDIT_CONFIG_VALIDATE_FILTER = """
<configuration>
    <interfaces>
    </interfaces>
</configuration>"""

EDIT_CONFIG_VALIDATE_EXPECTED = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/17.3R2/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
<data>
<configuration xmlns="http://xml.juniper.net/xnm/1.1/xnm" timestamp="TIMESTAMP">
    <interfaces>
        <interface>
            <name>ge-0/0/0</name>
            <description>scrapli was here</description>
        </interface>
        <interface>
            <name>fxp0</name>
            <unit>
                <name>0</name>
                <family>
                    <inet>
                        <address>
                            <name>10.0.0.15/24</name>
                        </address>
                    </inet>
                </family>
            </unit>
        </interface>
    </interfaces>
</configuration>
</data>
</rpc-reply>"""

RPC_FILTER = """<get-zones-information><terse/></get-zones-information>"""

RPC_ELEMENTS = []

RPC_EXPECTED = """<rpc-reply xmlns:junos="http://xml.juniper.net/junos/17.3R2/junos" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
    <zones-information xmlns="http://xml.juniper.net/junos/17.3R2/junos-zones" junos:style="terse">
        <zones-security>
            <zones-security-zonename>trust</zones-security-zonename>
            <zones-security-send-reset>On</zones-security-send-reset>
            <zones-security-policy-configurable>Yes</zones-security-policy-configurable>
            <zones-security-interfaces-bound>0</zones-security-interfaces-bound>
            <zones-security-interfaces>
            </zones-security-interfaces>
        </zones-security>
        <zones-security>
            <zones-security-zonename>untrust</zones-security-zonename>
            <zones-security-send-reset>Off</zones-security-send-reset>
            <zones-security-policy-configurable>Yes</zones-security-policy-configurable>
            <zones-security-screen>untrust-screen</zones-security-screen>
            <zones-security-interfaces-bound>0</zones-security-interfaces-bound>
            <zones-security-interfaces>
            </zones-security-interfaces>
        </zones-security>
        <zones-security>
            <zones-security-zonename>junos-host</zones-security-zonename>
            <zones-security-send-reset>Off</zones-security-send-reset>
            <zones-security-policy-configurable>Yes</zones-security-policy-configurable>
            <zones-security-interfaces-bound>0</zones-security-interfaces-bound>
            <zones-security-interfaces>
            </zones-security-interfaces>
        </zones-security>
    </zones-information>
</rpc-reply>"""
