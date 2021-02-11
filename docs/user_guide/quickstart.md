# Quick Start Guide


## Installation

In most cases installation via pip is the simplest and best way to install scrapli_netconf.
See [here](/user_guide/installation) for advanced installation details.

```
pip install scrapli-netconf
```


## A Simple Example

```python
from scrapli_netconf.driver import NetconfDriver

my_device = {
    "host": "172.18.0.13",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
    "port": 830
}

conn = NetconfDriver(**my_device)
conn.open()
response = conn.get_config(source="running")
print(response.result)
```

```
$ python my_scrapli_script.py
<rpc-reply message-id="101">
 <data>
  <ssh>
   <server>
    <v2/>
    <netconf>830</netconf>
    <netconf-vrf-table>
     <vrf>
      <vrf-name>default</vrf-name>
      <enable/>
     </vrf>
    </netconf-vrf-table>
   </server>
  </ssh>
  <interface-configurations>
   <interface-configuration>
    <active>act</active>
    <interface-name>MgmtEth0/RP0/CPU0/0</interface-name>
<SNIP>
 </data>
</rpc-reply>
```


## More Examples

- [Basic Operations IOS-XR](https://github.com/scrapli/scrapli_netconf/blob/master/examples/basic_usage/basic_usage_iosxr.py)
- [Basic Operations Junos](https://github.com/scrapli/scrapli_netconf/blob/master/examples/basic_usage/basic_usage_junos.py)
- [Edit Config IOS-XR](https://github.com/scrapli/scrapli_netconf/blob/master/examples/edit_config/edit_config_iosxr.py)
- [Asyncio Edit Config IOS-XR](https://github.com/scrapli/scrapli_netconf/blob/master/examples/edit_config/async_edit_config_iosxr.py)
