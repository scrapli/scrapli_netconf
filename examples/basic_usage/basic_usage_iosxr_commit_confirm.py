"""
Script to verify commit confirm functionality using Cisco always on IOSXR
sandbox device.

Sample terminal output:

# --------------------------------------------------
# Test commit confirmed within same session
# --------------------------------------------------
    
IOSXR OPEN
IOSXR LOCK:  <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <ok/>
</rpc-reply>

IOSXR EDIT:  <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="102">
  <ok/>
</rpc-reply>

IOSXR COMMIT CONFIRMED:  <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="102">
  <ok/>
</rpc-reply>

IOSXR COMMIT:  <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="102">
  <ok/>
</rpc-reply>

IOSXR UNLOCK:  <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="105">
  <ok/>
</rpc-reply>

IOSXR CHECK description is 'Configured by scrapli-netconf, random int - 7570'
IOSXR INTERFACE CONFIG <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="106">
  <data>
    <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
      <interface-configuration>
        <active>act</active>
        <interface-name>Loopback111</interface-name>
        <interface-virtual/>
        <description>Configured by scrapli-netconf, random int - 7570</description>
      </interface-configuration>
    </interface-configurations>
  </data>
</rpc-reply>

IOSXR CLOSED

# --------------------------------------------------
# Test commit confirmed within another session 
# using persist-id
# --------------------------------------------------
    
IOSXR OPEN
IOSXR EDIT:  <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <ok/>
</rpc-reply>

IOSXR COMMIT CONFIRMED WITH PERSIST:  <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <ok/>
</rpc-reply>

IOSXR CLOSED
IOSXR OPEN AGAIN
IOSXR COMMIT PERSIST-ID:  <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <ok/>
</rpc-reply>

IOSXR CHECK description is 'Configured by scrapli-netconf, random int - 5811'
IOSXR INTERFACE CONFIG <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="102">
  <data>
    <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
      <interface-configuration>
        <active>act</active>
        <interface-name>Loopback111</interface-name>
        <interface-virtual/>
        <description>Configured by scrapli-netconf, random int - 5811</description>
      </interface-configuration>
    </interface-configurations>
  </data>
</rpc-reply>

IOSXR CLOSED

# --------------------------------------------------
# Test commit confirmed with timeout
# --------------------------------------------------
    
IOSXR OPEN
IOSXR EDIT:  <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <ok/>
</rpc-reply>

IOSXR COMMIT CONFIRMED TIMEOUT 10s:  <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <ok/>
</rpc-reply>

IOSXR CHECK description is 'Configured by scrapli-netconf, random int - 5644'
IOSXR INTERFACE CONFIG:  <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="103">
  <data>
    <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
      <interface-configuration>
        <active>act</active>
        <interface-name>Loopback111</interface-name>
        <interface-virtual/>
        <description>Configured by scrapli-netconf, random int - 5644</description>
      </interface-configuration>
    </interface-configurations>
  </data>
</rpc-reply>

IOSXR CLOSED
IOSXR sleeping 15 seconds for commit to timeout
IOSXR OPEN AGAIN
IOSXR CHECK description is not 'Configured by scrapli-netconf, random int - 5644'
IOSXR INTERFACE CONFIG after timeout:  <rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
  <data>
    <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
      <interface-configuration>
        <active>act</active>
        <interface-name>Loopback111</interface-name>
        <interface-virtual/>
        <description>Configured by scrapli-netconf, random int - 5811</description>
      </interface-configuration>
    </interface-configurations>
  </data>
</rpc-reply>

IOSXR CLOSED
"""
from scrapli_netconf.driver import NetconfDriver
import random
import time

iosxr1 = {
    "host": "sandbox-iosxr-1.cisco.com",
    "auth_username": "admin",
    "auth_password": "C1sco12345",
    "port": 830,
    "auth_strict_key": False,
}

IOS_XR_EDIT_CONFIG = """
<config>
  <interfaces xmlns="http://openconfig.net/yang/interfaces">
   <interface>
    <name>Loopback111</name>
    <config>
     <name>Loopback111</name>
     <type xmlns:idx="urn:ietf:params:xml:ns:yang:iana-if-type">idx:softwareLoopback</type>
     <enabled>true</enabled>
     <description>{}</description>
    </config>
   </interface>
  </interfaces>
</config>
"""

IOS_XR_FILTER = """
<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
    <interface-configuration>
        <interface-name>Loopback111</interface-name>
    </interface-configuration>
</interface-configurations>
"""


def test_iosxr_commit_confirmed_in_same_session():
    print(
        """
# --------------------------------------------------
# Test commit confirmed within same session
# --------------------------------------------------
    """
    )
    description = "Configured by scrapli-netconf, random int - {}".format(
        random.randrange(1, 10000)
    )
    iosxr1_conn = NetconfDriver(**iosxr1)
    iosxr1_conn.open()
    print("IOSXR OPEN")

    result = iosxr1_conn.lock(target="candidate")
    print("IOSXR LOCK: ", result.result)

    result = iosxr1_conn.edit_config(
        config=IOS_XR_EDIT_CONFIG.format(description), target="candidate"
    )
    print("IOSXR EDIT: ", result.result)

    iosxr1_conn.commit(confirmed=True)
    print("IOSXR COMMIT CONFIRMED: ", result.result)

    iosxr1_conn.commit()
    print("IOSXR COMMIT: ", result.result)

    result = iosxr1_conn.unlock(target="candidate")
    print("IOSXR UNLOCK: ", result.result)

    print("IOSXR CHECK description is '{}'".format(description))
    result = iosxr1_conn.get_config(source="running", filter_=IOS_XR_FILTER)
    print("IOSXR INTERFACE CONFIG", result.result)

    iosxr1_conn.close()
    print("IOSXR CLOSED")


def test_iosxr_commit_confirmed_in_another_session():
    print(
        """
# --------------------------------------------------
# Test commit confirmed within another session 
# using persist-id
# --------------------------------------------------
    """
    )
    description = "Configured by scrapli-netconf, random int - {}".format(
        random.randrange(1, 10000)
    )
    iosxr1_conn = NetconfDriver(**iosxr1)
    iosxr1_conn.open()
    print("IOSXR OPEN")

    result = iosxr1_conn.edit_config(
        config=IOS_XR_EDIT_CONFIG.format(description), target="candidate"
    )
    print("IOSXR EDIT: ", result.result)

    iosxr1_conn.commit(confirmed=True, persist="foobar1234")
    print("IOSXR COMMIT CONFIRMED WITH PERSIST: ", result.result)

    iosxr1_conn.close()
    print("IOSXR CLOSED")

    iosxr1_conn = NetconfDriver(**iosxr1)
    iosxr1_conn.open()
    print("IOSXR OPEN AGAIN")

    iosxr1_conn.commit(persist_id="foobar1234")
    print("IOSXR COMMIT PERSIST-ID: ", result.result)

    print("IOSXR CHECK description is '{}'".format(description))
    result = iosxr1_conn.get_config(source="running", filter_=IOS_XR_FILTER)
    print("IOSXR INTERFACE CONFIG", result.result)

    iosxr1_conn.close()
    print("IOSXR CLOSED")


def test_iosxr_commit_confirmed_timeout():
    print(
        """
# --------------------------------------------------
# Test commit confirmed with timeout
# --------------------------------------------------
    """
    )
    description = "Configured by scrapli-netconf, random int - {}".format(
        random.randrange(1, 10000)
    )
    iosxr1_conn = NetconfDriver(**iosxr1)
    iosxr1_conn.open()
    print("IOSXR OPEN")

    result = iosxr1_conn.edit_config(
        config=IOS_XR_EDIT_CONFIG.format(description), target="candidate"
    )
    print("IOSXR EDIT: ", result.result)

    iosxr1_conn.commit(confirmed=True, timeout=10)
    print("IOSXR COMMIT CONFIRMED TIMEOUT 10s: ", result.result)

    print("IOSXR CHECK description is '{}'".format(description))
    result = iosxr1_conn.get_config(source="running", filter_=IOS_XR_FILTER)
    print("IOSXR INTERFACE CONFIG: ", result.result)

    iosxr1_conn.close()
    print("IOSXR CLOSED")

    print("IOSXR sleeping 15 seconds for commit to timeout")
    time.sleep(15)

    iosxr1_conn = NetconfDriver(**iosxr1)
    iosxr1_conn.open()
    print("IOSXR OPEN AGAIN")

    print("IOSXR CHECK description is not '{}'".format(description))
    result = iosxr1_conn.get_config(source="running", filter_=IOS_XR_FILTER)
    print("IOSXR INTERFACE CONFIG after timeout: ", result.result)

    iosxr1_conn.close()
    print("IOSXR CLOSED")


test_iosxr_commit_confirmed_in_same_session()
test_iosxr_commit_confirmed_in_another_session()
test_iosxr_commit_confirmed_timeout()
