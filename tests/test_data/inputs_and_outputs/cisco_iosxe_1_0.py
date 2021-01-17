GET_SUBTREE_FILTER = """
<config-format-text-cmd>
 <text-filter-spec> | include interface </text-filter-spec>
</config-format-text-cmd>"""

GET_SUBTREE_ELEMENTS = ["cli-config-data"]

GET_SUBTREE_RESULT = """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><data><cli-config-data><cmd>interface GigabitEthernet1</cmd>
<cmd>interface GigabitEthernet2</cmd>
<cmd>interface GigabitEthernet3</cmd>
<cmd>interface GigabitEthernet4</cmd>
<cmd>interface GigabitEthernet5</cmd>
<cmd>interface GigabitEthernet6</cmd>
<cmd>interface GigabitEthernet7</cmd>
<cmd>interface GigabitEthernet8</cmd>
<cmd>interface GigabitEthernet9</cmd>
<cmd>interface GigabitEthernet10</cmd></cli-config-data></data></rpc-reply>"""

FULL_GET_CONFIG_ELEMENTS = ["cli-config-data-block"]

FULL_GET_CONFIG_RESULT = """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><data><cli-config-data-block>!
TIMESTAMP
!
version 16.12
service timestamps debug datetime msec
service timestamps log datetime msec
service call-home
platform qfp utilization monitor load 80
platform punt-keepalive disable-kernel-core
platform console serial
!
hostname csr1000v
!
boot-start-marker
boot-end-marker
!
!
enable secret 9 $9$h6Ayg86tb/EImk$2T6Ns.ke08cAlZ2TbMf3YRCYr7ngDGzgAxZB0YMe7lQ
!
no aaa new-model
call-home
 ! If contact email address in call-home is configured as sch-smart-licensing@cisco.com
 ! the email address configured in Cisco Smart License Portal will be used as contact email address to send SCH notifications.
 contact-email-addr sch-smart-licensing@cisco.com
 profile "CiscoTAC-1"
  active
  destination transport-method http
  no destination transport-method email
!
!
!
!
!
!
!
ip domain name example.com
!
!
!
login on-success log
!
!
!
!
!
!
!
subscriber templating
!
!
!
!
!
!
multilink bundle-name authenticated
!
!
!
!
!
!
!
!
!
!
!
!
!
!
!
CERTIFICATES AND LICENSE
diagnostic bootup level minimal
archive
 log config
  logging enable
 path bootflash:
memory free low-watermark processor 72329
!
!
spanning-tree extend system-id
!
username vrnetlab privilege 15 password 0 VR-netlab9
!
redundancy
!
!
!
!
!
!
!
!
!
!
!
!
!
!
!
!
!
!
!
!
!
!
!
interface GigabitEthernet1
 ip address 10.0.0.15 255.255.255.0
 negotiation auto
 no mop enabled
 no mop sysid
!
interface GigabitEthernet2
 no ip address
 shutdown
 negotiation auto
 no mop enabled
 no mop sysid
!
interface GigabitEthernet3
 no ip address
 shutdown
 negotiation auto
 no mop enabled
 no mop sysid
!
interface GigabitEthernet4
 no ip address
 shutdown
 negotiation auto
 no mop enabled
 no mop sysid
!
interface GigabitEthernet5
 no ip address
 shutdown
 negotiation auto
 no mop enabled
 no mop sysid
!
interface GigabitEthernet6
 no ip address
 shutdown
 negotiation auto
 no mop enabled
 no mop sysid
!
interface GigabitEthernet7
 no ip address
 shutdown
 negotiation auto
 no mop enabled
 no mop sysid
!
interface GigabitEthernet8
 no ip address
 shutdown
 negotiation auto
 no mop enabled
 no mop sysid
!
interface GigabitEthernet9
 no ip address
 shutdown
 negotiation auto
 no mop enabled
 no mop sysid
!
interface GigabitEthernet10
 no ip address
 shutdown
 negotiation auto
 no mop enabled
 no mop sysid
!
!
virtual-service csr_mgmt
!
ip forward-protocol nd
no ip http server
no ip http secure-server
!
ip ssh pubkey-chain
  username vrnetlab
   key-hash ssh-rsa 5CC74A68B18B026A1709FB09D1F44E2F
ip scp server enable
!
!
!
!
!
!
!
control-plane
!
!
!
!
!
!
line con 0
 stopbits 1
line vty 0 4
 login local
 transport input all
line vty 5 15
 login local
 transport input all
!
netconf ssh
!
!
!
!
!
netconf-yang
end</cli-config-data-block></data></rpc-reply>"""

CONFIG_FILTER_SINGLE = """
<config-format-text-cmd>
    <text-filter-spec>
        interface GigabitEthernet1
    </text-filter-spec>
</config-format-text-cmd> 
"""

CONFIG_FILTER_SINGLE_GET_CONFIG_ELEMENTS = ["cli-config-data"]

CONFIG_FILTER_SINGLE_GET_CONFIG_RESULT = """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><data><cli-config-data><cmd>!</cmd>
<cmd>interface GigabitEthernet1</cmd>
<cmd> ip address 10.0.0.15 255.255.255.0</cmd>
<cmd> negotiation auto</cmd>
<cmd> no mop enabled</cmd>
<cmd> no mop sysid</cmd>
<cmd>end</cmd></cli-config-data></data></rpc-reply>"""

EDIT_CONFIG = """
<config>
<cli-config-data>
<cmd>interface GigabitEthernet2</cmd>
<cmd>description scrapli was here!</cmd>
</cli-config-data>
</config>"""

REMOVE_EDIT_CONFIG = """
<config>
<cli-config-data>
<cmd>interface GigabitEthernet2</cmd>
<cmd>no description</cmd>
</cli-config-data>
</config>"""

EDIT_CONFIG_VALIDATE_FILTER = """
<config-format-text-cmd>
 <text-filter-spec>
   interface GigabitEthernet2
 </text-filter-spec>
</config-format-text-cmd>"""

EDIT_CONFIG_VALIDATE_EXPECTED = """<rpc-reply message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <data>
        <cli-config-data>
            <cmd>!</cmd>
            <cmd>interface GigabitEthernet2</cmd>
            <cmd>description scrapli was here!</cmd>
            <cmd>no ip address</cmd>
            <cmd>shutdown</cmd>
            <cmd>negotiation auto</cmd>
            <cmd>no mop enabled</cmd>
            <cmd>no mop sysid</cmd>
            <cmd>end</cmd></cli-config-data>
    </data>
</rpc-reply>"""

RPC_FILTER = """<get><filter type="subtree"><config-format-text-cmd>
    <text-filter-spec> | include interface </text-filter-spec>
</config-format-text-cmd></filter></get>"""

RPC_ELEMENTS = ["cli-config-data"]

RPC_EXPECTED = """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101"><data><cli-config-data><cmd>interface GigabitEthernet1</cmd>
<cmd>interface GigabitEthernet2</cmd>
<cmd>interface GigabitEthernet3</cmd>
<cmd>interface GigabitEthernet4</cmd>
<cmd>interface GigabitEthernet5</cmd>
<cmd>interface GigabitEthernet6</cmd>
<cmd>interface GigabitEthernet7</cmd>
<cmd>interface GigabitEthernet8</cmd>
<cmd>interface GigabitEthernet9</cmd>
<cmd>interface GigabitEthernet10</cmd></cli-config-data></data></rpc-reply>"""
