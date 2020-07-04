GET_SUBTREE_FILTER = """
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name>
      GigabitEthernet1
    </name>
  </interface>
</interfaces>"""

GET_SUBTREE_ELEMENTS = ["interfaces"]

GET_SUBTREE_RESULT = """<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>GigabitEthernet1</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>true</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                        <ip>10.0.0.15</ip>
                        <netmask>255.255.255.0</netmask>
                    </address>
                </ipv4>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
        </interfaces>
    </data>
</rpc-reply>"""

GET_XPATH_FILTER = """//interfaces-state/interface[2]/name"""

GET_XPATH_ELEMENTS = ["interfaces-state"]

GET_XPATH_RESULT = """<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>GigabitEthernet1</name>
            </interface>
        </interfaces-state>
    </data>
</rpc-reply>"""

FULL_GET_CONFIG_ELEMENTS = [
    "native",
    "licensing",
    "netconf-yang",
    "acl",
    "interfaces",
    "lldp",
    "network-instances",
    "nacm",
    "routing",
]

FULL_GET_CONFIG_RESULT = """<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
            <version>16.12</version>
            <boot-start-marker/>
            <boot-end-marker/>
            <memory>
                <free>
                    <low-watermark>
                        <processor>72329</processor>
                    </low-watermark>
                </free>
            </memory>
            <call-home>
                <contact-email-addr xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-call-home">sch-smart-licensing@cisco.com</contact-email-addr>
                <profile xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-call-home">
                    <profile-name>CiscoTAC-1</profile-name>
                    <active>true</active>
                </profile>
            </call-home>
            <service>
                <timestamps>
                    <debug>
                        <datetime>
                            <msec/>
                        </datetime>
                    </debug>
                    <log>
                        <datetime>
                            <msec/>
                        </datetime>
                    </log>
                </timestamps>
                <call-home/>
            </service>
            <platform>
                <console xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-platform">
                    <output>serial</output>
                </console>
                <punt-keepalive xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-platform">
                    <disable-kernel-core>true</disable-kernel-core>
                </punt-keepalive>
            </platform>
            <hostname>csr1000v</hostname>
            <enable>
                <secret>
                    <type>9</type>
                    <secret>$9$h6Ayg86tb/EImk$2T6Ns.ke08cAlZ2TbMf3YRCYr7ngDGzgAxZB0YMe7lQ</secret>
                </secret>
            </enable>
            <archive>
                <log>
                    <config>
                        <logging>
                            <enable/>
                        </logging>
                    </config>
                </log>
                <path>bootflash:</path>
            </archive>
            <username>
                <name>vrnetlab</name>
                <privilege>15</privilege>
                <password>
                    <encryption>0</encryption>
                    <password>VR-netlab9</password>
                </password>
            </username>
            <ip>
                <domain>
                    <name>example.com</name>
                </domain>
                <forward-protocol>
                    <protocol>nd</protocol>
                </forward-protocol>
                <multicast>
                    <route-limit xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-multicast">2147483647</route-limit>
                </multicast>
                <pim>
                    <autorp-container xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-multicast">
                        <autorp>false</autorp>
                    </autorp-container>
                </pim>
                <scp>
                    <server>
                        <enable/>
                    </server>
                </scp>
                <ssh>
                    <pubkey-chain>
                        <username>
                            <name>vrnetlab</name>
                            <key-hash>
                                <key-type>ssh-rsa</key-type>
                                <key-hash-value>5CC74A68B18B026A1709FB09D1F44E2F</key-hash-value>
                            </key-hash>
                        </username>
                    </pubkey-chain>
                </ssh>
                <access-list>
                    <extended xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-acl">
                        <name>meraki-fqdn-dns</name>
                    </extended>
                </access-list>
                <http xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-http">
                    <server>false</server>
                    <secure-server>false</secure-server>
                </http>
            </ip>
            <interface>
                <GigabitEthernet>
                    <name>1</name>
                    <ip>
                        <address>
                            <primary>
                                <address>10.0.0.15</address>
                                <mask>255.255.255.0</mask>
                            </primary>
                        </address>
                    </ip>
                    <mop>
                        <enabled>false</enabled>
                        <sysid>false</sysid>
                    </mop>
                    <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
                        <auto>true</auto>
                    </negotiation>
                </GigabitEthernet>
                <GigabitEthernet>
                    <name>10</name>
                    <shutdown/>
                    <mop>
                        <enabled>false</enabled>
                        <sysid>false</sysid>
                    </mop>
                    <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
                        <auto>true</auto>
                    </negotiation>
                </GigabitEthernet>
                <GigabitEthernet>
                    <name>2</name>
                    <shutdown/>
                    <mop>
                        <enabled>false</enabled>
                        <sysid>false</sysid>
                    </mop>
                    <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
                        <auto>true</auto>
                    </negotiation>
                </GigabitEthernet>
                <GigabitEthernet>
                    <name>3</name>
                    <shutdown/>
                    <mop>
                        <enabled>false</enabled>
                        <sysid>false</sysid>
                    </mop>
                    <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
                        <auto>true</auto>
                    </negotiation>
                </GigabitEthernet>
                <GigabitEthernet>
                    <name>4</name>
                    <shutdown/>
                    <mop>
                        <enabled>false</enabled>
                        <sysid>false</sysid>
                    </mop>
                    <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
                        <auto>true</auto>
                    </negotiation>
                </GigabitEthernet>
                <GigabitEthernet>
                    <name>5</name>
                    <shutdown/>
                    <mop>
                        <enabled>false</enabled>
                        <sysid>false</sysid>
                    </mop>
                    <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
                        <auto>true</auto>
                    </negotiation>
                </GigabitEthernet>
                <GigabitEthernet>
                    <name>6</name>
                    <shutdown/>
                    <mop>
                        <enabled>false</enabled>
                        <sysid>false</sysid>
                    </mop>
                    <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
                        <auto>true</auto>
                    </negotiation>
                </GigabitEthernet>
                <GigabitEthernet>
                    <name>7</name>
                    <shutdown/>
                    <mop>
                        <enabled>false</enabled>
                        <sysid>false</sysid>
                    </mop>
                    <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
                        <auto>true</auto>
                    </negotiation>
                </GigabitEthernet>
                <GigabitEthernet>
                    <name>8</name>
                    <shutdown/>
                    <mop>
                        <enabled>false</enabled>
                        <sysid>false</sysid>
                    </mop>
                    <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
                        <auto>true</auto>
                    </negotiation>
                </GigabitEthernet>
                <GigabitEthernet>
                    <name>9</name>
                    <shutdown/>
                    <mop>
                        <enabled>false</enabled>
                        <sysid>false</sysid>
                    </mop>
                    <negotiation xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ethernet">
                        <auto>true</auto>
                    </negotiation>
                </GigabitEthernet>
            </interface>
            <control-plane/>
            <login>
                <on-success>
                    <log/>
                </on-success>
            </login>
            <multilink>
                <bundle-name xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ppp">authenticated</bundle-name>
            </multilink>
            <redundancy/>
            <spanning-tree>
                <extend xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree">
                    <system-id/>
                </extend>
            </spanning-tree>
            <subscriber>
                <templating/>
            </subscriber>
            <crypto>
                <pki xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-crypto">
                    <certificate>
                        <chain>
                            <name>SLA-TrustPoint</name>
                            <certificate>
                                <serial>01</serial>
                                <certtype>ca</certtype>
                            </certificate>
                        </chain>
                        <chain>
                            <name>TP-self-signed-434383619</name>
                            <certificate>
                                <serial>01</serial>
                                <certtype>self-signed</certtype>
                            </certificate>
                        </chain>
                    </certificate>
                    <trustpoint>
                        <id>SLA-TrustPoint</id>
                        <enrollment>
                            <pkcs12/>
                        </enrollment>
                        <revocation-check>crl</revocation-check>
                    </trustpoint>
                    <trustpoint>
                        <id>TP-self-signed-434383619</id>
                        <enrollment>
                            <selfsigned/>
                        </enrollment>
                        <revocation-check>none</revocation-check>
                        <subject-name>cn=IOS-Self-Signed-Certificate-434383619</subject-name>
                    </trustpoint>
                </pki>
            </crypto>
            <virtual-service>
                <name>csr_mgmt</name>
            </virtual-service>
            <license>
                <udi>
                    <pid>CSR1000V</pid>
                    <sn>9UMWQBNX1KX</sn>
                </udi>
            </license>
            <line>
                <console>
                    <first>0</first>
                    <stopbits>1</stopbits>
                </console>
                <vty>
                    <first>0</first>
                    <last>4</last>
                    <login>
                        <local/>
                    </login>
                    <transport>
                        <input>
                            <all/>
                        </input>
                    </transport>
                </vty>
                <vty>
                    <first>5</first>
                    <last>15</last>
                    <login>
                        <local/>
                    </login>
                    <transport>
                        <input>
                            <all/>
                        </input>
                    </transport>
                </vty>
            </line>
            <diagnostic xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-diagnostics">
                <bootup>
                    <level>minimal</level>
                </bootup>
            </diagnostic>
        </native>
        <licensing xmlns="http://cisco.com/ns/yang/cisco-smart-license">
            <config>
                <enable>false</enable>
                <privacy>
                    <hostname>false</hostname>
                    <version>false</version>
                </privacy>
                <utility>
                    <utility-enable>false</utility-enable>
                </utility>
            </config>
        </licensing>
        <netconf-yang xmlns="http://cisco.com/yang/cisco-self-mgmt">
            <cisco-ia xmlns="http://cisco.com/yang/cisco-ia">
                <snmp-trap-control>
                    <global-forwarding>true</global-forwarding>
                </snmp-trap-control>
                <snmp-community-string>private</snmp-community-string>
            </cisco-ia>
        </netconf-yang>
        <acl xmlns="http://openconfig.net/yang/acl">
            <acl-sets>
                <acl-set>
                    <name>meraki-fqdn-dns</name>
                    <type>ACL_IPV4</type>
                    <config>
                        <name>meraki-fqdn-dns</name>
                        <type>ACL_IPV4</type>
                    </config>
                </acl-set>
            </acl-sets>
        </acl>
        <interfaces xmlns="http://openconfig.net/yang/interfaces">
            <interface>
                <name>GigabitEthernet1</name>
                <config>
                    <name>GigabitEthernet1</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>true</enabled>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <config>
                            <index>0</index>
                            <enabled>true</enabled>
                        </config>
                        <ipv4 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <addresses>
                                <address>
                                    <ip>10.0.0.15</ip>
                                    <config>
                                        <ip>10.0.0.15</ip>
                                        <prefix-length>24</prefix-length>
                                    </config>
                                </address>
                            </addresses>
                        </ipv4>
                        <ipv6 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <config>
                                <enabled>false</enabled>
                            </config>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
                <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
                    <config>
                        <mac-address>MAC_ADDRESS</mac-address>
                        <auto-negotiate>true</auto-negotiate>
                        <enable-flow-control>true</enable-flow-control>
                    </config>
                </ethernet>
            </interface>
            <interface>
                <name>GigabitEthernet10</name>
                <config>
                    <name>GigabitEthernet10</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>false</enabled>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <config>
                            <index>0</index>
                            <enabled>false</enabled>
                        </config>
                        <ipv6 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <config>
                                <enabled>false</enabled>
                            </config>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
                <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
                    <config>
                        <mac-address>MAC_ADDRESS</mac-address>
                        <auto-negotiate>true</auto-negotiate>
                        <enable-flow-control>true</enable-flow-control>
                    </config>
                </ethernet>
            </interface>
            <interface>
                <name>GigabitEthernet2</name>
                <config>
                    <name>GigabitEthernet2</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>false</enabled>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <config>
                            <index>0</index>
                            <enabled>false</enabled>
                        </config>
                        <ipv6 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <config>
                                <enabled>false</enabled>
                            </config>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
                <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
                    <config>
                        <mac-address>MAC_ADDRESS</mac-address>
                        <auto-negotiate>true</auto-negotiate>
                        <enable-flow-control>true</enable-flow-control>
                    </config>
                </ethernet>
            </interface>
            <interface>
                <name>GigabitEthernet3</name>
                <config>
                    <name>GigabitEthernet3</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>false</enabled>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <config>
                            <index>0</index>
                            <enabled>false</enabled>
                        </config>
                        <ipv6 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <config>
                                <enabled>false</enabled>
                            </config>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
                <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
                    <config>
                        <mac-address>MAC_ADDRESS</mac-address>
                        <auto-negotiate>true</auto-negotiate>
                        <enable-flow-control>true</enable-flow-control>
                    </config>
                </ethernet>
            </interface>
            <interface>
                <name>GigabitEthernet4</name>
                <config>
                    <name>GigabitEthernet4</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>false</enabled>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <config>
                            <index>0</index>
                            <enabled>false</enabled>
                        </config>
                        <ipv6 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <config>
                                <enabled>false</enabled>
                            </config>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
                <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
                    <config>
                        <mac-address>MAC_ADDRESS</mac-address>
                        <auto-negotiate>true</auto-negotiate>
                        <enable-flow-control>true</enable-flow-control>
                    </config>
                </ethernet>
            </interface>
            <interface>
                <name>GigabitEthernet5</name>
                <config>
                    <name>GigabitEthernet5</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>false</enabled>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <config>
                            <index>0</index>
                            <enabled>false</enabled>
                        </config>
                        <ipv6 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <config>
                                <enabled>false</enabled>
                            </config>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
                <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
                    <config>
                        <mac-address>MAC_ADDRESS</mac-address>
                        <auto-negotiate>true</auto-negotiate>
                        <enable-flow-control>true</enable-flow-control>
                    </config>
                </ethernet>
            </interface>
            <interface>
                <name>GigabitEthernet6</name>
                <config>
                    <name>GigabitEthernet6</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>false</enabled>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <config>
                            <index>0</index>
                            <enabled>false</enabled>
                        </config>
                        <ipv6 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <config>
                                <enabled>false</enabled>
                            </config>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
                <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
                    <config>
                        <mac-address>MAC_ADDRESS</mac-address>
                        <auto-negotiate>true</auto-negotiate>
                        <enable-flow-control>true</enable-flow-control>
                    </config>
                </ethernet>
            </interface>
            <interface>
                <name>GigabitEthernet7</name>
                <config>
                    <name>GigabitEthernet7</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>false</enabled>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <config>
                            <index>0</index>
                            <enabled>false</enabled>
                        </config>
                        <ipv6 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <config>
                                <enabled>false</enabled>
                            </config>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
                <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
                    <config>
                        <mac-address>MAC_ADDRESS</mac-address>
                        <auto-negotiate>true</auto-negotiate>
                        <enable-flow-control>true</enable-flow-control>
                    </config>
                </ethernet>
            </interface>
            <interface>
                <name>GigabitEthernet8</name>
                <config>
                    <name>GigabitEthernet8</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>false</enabled>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <config>
                            <index>0</index>
                            <enabled>false</enabled>
                        </config>
                        <ipv6 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <config>
                                <enabled>false</enabled>
                            </config>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
                <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
                    <config>
                        <mac-address>MAC_ADDRESS</mac-address>
                        <auto-negotiate>true</auto-negotiate>
                        <enable-flow-control>true</enable-flow-control>
                    </config>
                </ethernet>
            </interface>
            <interface>
                <name>GigabitEthernet9</name>
                <config>
                    <name>GigabitEthernet9</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>false</enabled>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <config>
                            <index>0</index>
                            <enabled>false</enabled>
                        </config>
                        <ipv6 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <config>
                                <enabled>false</enabled>
                            </config>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
                <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
                    <config>
                        <mac-address>MAC_ADDRESS</mac-address>
                        <auto-negotiate>true</auto-negotiate>
                        <enable-flow-control>true</enable-flow-control>
                    </config>
                </ethernet>
            </interface>
        </interfaces>
        <lldp xmlns="http://openconfig.net/yang/lldp">
            <config>
                <enabled>false</enabled>
            </config>
            <interfaces>
                <interface>
                    <name>GigabitEthernet1</name>
                    <config>
                        <name>GigabitEthernet1</name>
                        <enabled>true</enabled>
                    </config>
                </interface>
                <interface>
                    <name>GigabitEthernet10</name>
                    <config>
                        <name>GigabitEthernet10</name>
                        <enabled>true</enabled>
                    </config>
                </interface>
                <interface>
                    <name>GigabitEthernet2</name>
                    <config>
                        <name>GigabitEthernet2</name>
                        <enabled>true</enabled>
                    </config>
                </interface>
                <interface>
                    <name>GigabitEthernet3</name>
                    <config>
                        <name>GigabitEthernet3</name>
                        <enabled>true</enabled>
                    </config>
                </interface>
                <interface>
                    <name>GigabitEthernet4</name>
                    <config>
                        <name>GigabitEthernet4</name>
                        <enabled>true</enabled>
                    </config>
                </interface>
                <interface>
                    <name>GigabitEthernet5</name>
                    <config>
                        <name>GigabitEthernet5</name>
                        <enabled>true</enabled>
                    </config>
                </interface>
                <interface>
                    <name>GigabitEthernet6</name>
                    <config>
                        <name>GigabitEthernet6</name>
                        <enabled>true</enabled>
                    </config>
                </interface>
                <interface>
                    <name>GigabitEthernet7</name>
                    <config>
                        <name>GigabitEthernet7</name>
                        <enabled>true</enabled>
                    </config>
                </interface>
                <interface>
                    <name>GigabitEthernet8</name>
                    <config>
                        <name>GigabitEthernet8</name>
                        <enabled>true</enabled>
                    </config>
                </interface>
                <interface>
                    <name>GigabitEthernet9</name>
                    <config>
                        <name>GigabitEthernet9</name>
                        <enabled>true</enabled>
                    </config>
                </interface>
            </interfaces>
        </lldp>
        <network-instances xmlns="http://openconfig.net/yang/network-instance">
            <network-instance>
                <name>default</name>
                <config>
                    <name>default</name>
                    <type xmlns:oc-ni-types="http://openconfig.net/yang/network-instance-types">oc-ni-types:DEFAULT_INSTANCE</type>
                    <description>default-vrf [read-only]</description>
                </config>
                <tables>
                    <table>
                        <protocol xmlns:oc-pol-types="http://openconfig.net/yang/policy-types">oc-pol-types:DIRECTLY_CONNECTED</protocol>
                        <address-family xmlns:oc-types="http://openconfig.net/yang/openconfig-types">oc-types:IPV4</address-family>
                        <config>
                            <protocol xmlns:oc-pol-types="http://openconfig.net/yang/policy-types">oc-pol-types:DIRECTLY_CONNECTED</protocol>
                            <address-family xmlns:oc-types="http://openconfig.net/yang/openconfig-types">oc-types:IPV4</address-family>
                        </config>
                    </table>
                    <table>
                        <protocol xmlns:oc-pol-types="http://openconfig.net/yang/policy-types">oc-pol-types:DIRECTLY_CONNECTED</protocol>
                        <address-family xmlns:oc-types="http://openconfig.net/yang/openconfig-types">oc-types:IPV6</address-family>
                        <config>
                            <protocol xmlns:oc-pol-types="http://openconfig.net/yang/policy-types">oc-pol-types:DIRECTLY_CONNECTED</protocol>
                            <address-family xmlns:oc-types="http://openconfig.net/yang/openconfig-types">oc-types:IPV6</address-family>
                        </config>
                    </table>
                    <table>
                        <protocol xmlns:oc-pol-types="http://openconfig.net/yang/policy-types">oc-pol-types:STATIC</protocol>
                        <address-family xmlns:oc-types="http://openconfig.net/yang/openconfig-types">oc-types:IPV4</address-family>
                        <config>
                            <protocol xmlns:oc-pol-types="http://openconfig.net/yang/policy-types">oc-pol-types:STATIC</protocol>
                            <address-family xmlns:oc-types="http://openconfig.net/yang/openconfig-types">oc-types:IPV4</address-family>
                        </config>
                    </table>
                    <table>
                        <protocol xmlns:oc-pol-types="http://openconfig.net/yang/policy-types">oc-pol-types:STATIC</protocol>
                        <address-family xmlns:oc-types="http://openconfig.net/yang/openconfig-types">oc-types:IPV6</address-family>
                        <config>
                            <protocol xmlns:oc-pol-types="http://openconfig.net/yang/policy-types">oc-pol-types:STATIC</protocol>
                            <address-family xmlns:oc-types="http://openconfig.net/yang/openconfig-types">oc-types:IPV6</address-family>
                        </config>
                    </table>
                </tables>
                <protocols>
                    <protocol>
                        <identifier xmlns:oc-pol-types="http://openconfig.net/yang/policy-types">oc-pol-types:STATIC</identifier>
                        <name>DEFAULT</name>
                        <config>
                            <identifier xmlns:oc-pol-types="http://openconfig.net/yang/policy-types">oc-pol-types:STATIC</identifier>
                            <name>DEFAULT</name>
                        </config>
                    </protocol>
                    <protocol>
                        <identifier xmlns:oc-pol-types="http://openconfig.net/yang/policy-types">oc-pol-types:DIRECTLY_CONNECTED</identifier>
                        <name>DEFAULT</name>
                        <config>
                            <identifier xmlns:oc-pol-types="http://openconfig.net/yang/policy-types">oc-pol-types:DIRECTLY_CONNECTED</identifier>
                            <name>DEFAULT</name>
                        </config>
                    </protocol>
                </protocols>
            </network-instance>
        </network-instances>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>GigabitEthernet1</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>true</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                        <ip>10.0.0.15</ip>
                        <netmask>255.255.255.0</netmask>
                    </address>
                </ipv4>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
            <interface>
                <name>GigabitEthernet10</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>false</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
            <interface>
                <name>GigabitEthernet2</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>false</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
            <interface>
                <name>GigabitEthernet3</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>false</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
            <interface>
                <name>GigabitEthernet4</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>false</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
            <interface>
                <name>GigabitEthernet5</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>false</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
            <interface>
                <name>GigabitEthernet6</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>false</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
            <interface>
                <name>GigabitEthernet7</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>false</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
            <interface>
                <name>GigabitEthernet8</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>false</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
            <interface>
                <name>GigabitEthernet9</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>false</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
        </interfaces>
        <nacm xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-acm">
            <enable-nacm>true</enable-nacm>
            <read-default>deny</read-default>
            <write-default>deny</write-default>
            <exec-default>deny</exec-default>
            <enable-external-groups>true</enable-external-groups>
            <rule-list>
                <name>admin</name>
                <group>PRIV15</group>
                <rule>
                    <name>permit-all</name>
                    <module-name>*</module-name>
                    <access-operations>*</access-operations>
                    <action>permit</action>
                </rule>
            </rule-list>
        </nacm>
        <routing xmlns="urn:ietf:params:xml:ns:yang:ietf-routing">
            <routing-instance>
                <name>default</name>
                <description>default-vrf [read-only]</description>
                <routing-protocols>
                    <routing-protocol>
                        <type>static</type>
                        <name>1</name>
                    </routing-protocol>
                </routing-protocols>
            </routing-instance>
        </routing>
    </data>
</rpc-reply>"""

CONFIG_FILTER_SINGLE = """
<interfaces xmlns="http://openconfig.net/yang/interfaces">
    <interface>
        <name>GigabitEthernet1</name>
    </interface>
</interfaces>
"""

CONFIG_FILTER_SINGLE_GET_CONFIG_ELEMENTS = ["interfaces"]

CONFIG_FILTER_SINGLE_GET_CONFIG_RESULT = """<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <interfaces xmlns="http://openconfig.net/yang/interfaces">
            <interface>
                <name>GigabitEthernet1</name>
                <config>
                    <name>GigabitEthernet1</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>true</enabled>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <config>
                            <index>0</index>
                            <enabled>true</enabled>
                        </config>
                        <ipv4 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <addresses>
                                <address>
                                    <ip>10.0.0.15</ip>
                                    <config>
                                        <ip>10.0.0.15</ip>
                                        <prefix-length>24</prefix-length>
                                    </config>
                                </address>
                            </addresses>
                        </ipv4>
                        <ipv6 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <config>
                                <enabled>false</enabled>
                            </config>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
                <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
                    <config>
                        <mac-address>MAC_ADDRESS</mac-address>
                        <auto-negotiate>true</auto-negotiate>
                        <enable-flow-control>true</enable-flow-control>
                    </config>
                </ethernet>
            </interface>
        </interfaces>
    </data>
</rpc-reply>"""

_CONFIG_FILTER_MULTI = """
<netconf-yang xmlns="http://cisco.com/yang/cisco-self-mgmt">
</netconf-yang>
"""

CONFIG_FILTER_MULTI = [CONFIG_FILTER_SINGLE, _CONFIG_FILTER_MULTI]

CONFIG_FILTER_MULTI_GET_CONFIG_ELEMENTS = ["interfaces", "netconf-yang"]

CONFIG_FILTER_MULTI_GET_CONFIG_RESULT = """<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <netconf-yang xmlns="http://cisco.com/yang/cisco-self-mgmt">
            <cisco-ia xmlns="http://cisco.com/yang/cisco-ia">
                <snmp-trap-control>
                    <global-forwarding>true</global-forwarding>
                </snmp-trap-control>
                <snmp-community-string>private</snmp-community-string>
            </cisco-ia>
        </netconf-yang>
        <interfaces xmlns="http://openconfig.net/yang/interfaces">
            <interface>
                <name>GigabitEthernet1</name>
                <config>
                    <name>GigabitEthernet1</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                    <enabled>true</enabled>
                </config>
                <subinterfaces>
                    <subinterface>
                        <index>0</index>
                        <config>
                            <index>0</index>
                            <enabled>true</enabled>
                        </config>
                        <ipv4 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <addresses>
                                <address>
                                    <ip>10.0.0.15</ip>
                                    <config>
                                        <ip>10.0.0.15</ip>
                                        <prefix-length>24</prefix-length>
                                    </config>
                                </address>
                            </addresses>
                        </ipv4>
                        <ipv6 xmlns="http://openconfig.net/yang/interfaces/ip">
                            <config>
                                <enabled>false</enabled>
                            </config>
                        </ipv6>
                    </subinterface>
                </subinterfaces>
                <ethernet xmlns="http://openconfig.net/yang/interfaces/ethernet">
                    <config>
                        <mac-address>MAC_ADDRESS</mac-address>
                        <auto-negotiate>true</auto-negotiate>
                        <enable-flow-control>true</enable-flow-control>
                    </config>
                </ethernet>
            </interface>
        </interfaces>
    </data>
</rpc-reply>"""

GET_CONFIG_XPATH_FILTER = """/interfaces/interface[1]/name"""

GET_CONFIG_XPATH_ELEMENTS = ["interfaces"]

GET_CONFIG_XPATH_RESULT = """<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <interfaces xmlns="http://openconfig.net/yang/interfaces">
            <interface>
                <name>GigabitEthernet1</name>
            </interface>
        </interfaces>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>GigabitEthernet1</name>
            </interface>
        </interfaces>
    </data>
</rpc-reply>"""

EDIT_CONFIG = """
<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>GigabitEthernet1</name>
            <description>scrapli was here!</description>
        </interface>
    </interfaces>
</config>"""

REMOVE_EDIT_CONFIG = """
<config>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
            <name>GigabitEthernet1</name>
            <description operation="delete"></description>
        </interface>
    </interfaces>
</config>"""

EDIT_CONFIG_VALIDATE_FILTER = """
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name>
      GigabitEthernet1
    </name>
  </interface>
</interfaces>"""

EDIT_CONFIG_VALIDATE_EXPECTED = """
<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>GigabitEthernet1</name>
                <description>scrapli was here!</description>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>true</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                        <ip>10.0.0.15</ip>
                        <netmask>255.255.255.0</netmask>
                    </address>
                </ipv4>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
        </interfaces>
    </data>
</rpc-reply>"""

RPC_FILTER = """<get><filter type="subtree"><interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
  <interface>
    <name>
      GigabitEthernet1
    </name>
  </interface>
</interfaces></filter></get>"""

RPC_ELEMENTS = ["interfaces"]

RPC_EXPECTED = """<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>GigabitEthernet1</name>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
                <enabled>true</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                        <ip>10.0.0.15</ip>
                        <netmask>255.255.255.0</netmask>
                    </address>
                </ipv4>
                <ipv6 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip"/>
            </interface>
        </interfaces>
    </data>
</rpc-reply>"""
