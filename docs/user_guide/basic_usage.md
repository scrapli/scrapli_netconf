# Basic Usage


## Picking the right Driver

Because netconf is a standard we don't need to deal with "platform" type drivers for scrapli_netconf! Instead, there
 are only two options -- `NetconfDriver` or `AsyncNetconfDriver`, these can be imported from `scrapli_netconf.driver
 ` like so:

```python
from scrapli_netconf.driver import NetconfDriver
from scrapli_netconf.driver import AsyncNetconfDriver
```

Note: if you are using async you *must* set the transport to `asyncssh` -- this is the only async transport supported
 at this time!


## Basic Driver Arguments

The drivers of course need some information about the device you are trying to connect to. The most common arguments
 to provide to the driver are outlined below:
 
| Argument         | Purpose/Value                                                |
|------------------|--------------------------------------------------------------|
| host             | name/ip of host to connect to                                |
| port             | port of host to connect to (defaults to port 830)            |
| auth_username    | username for authentication                                  |
| auth_password    | password for authentication                                  |
| auth_secondary   | password for secondary authentication (enable password)      |
| auth_private_key | private key for authentication                               |
| auth_strict_key  | strict key checking -- TRUE by default!                      |
| ssh_config_file  | True/False or path to ssh config file to use                 |
| strip_namespaces | True/False strip namespaces from returned XML (default False)|

These arguments may be passed as keyword arguments to the driver of your choice, or, commonly are passed via
 dictionary unpacking as show below:
 
```python
from scrapli_netconf.driver import NetconfDriver

my_device = {
    "host": "172.18.0.11",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
}

conn = NetconfDriver(**my_device)
conn.open()
```

*NOTE* that scrapli enables strict host key checking by default!


## Opening and Closing a Connection

scrapli_netconf does *not* open the connection for you when creating your scrapli connection object in normal operations
, you must manually call the `open` method prior to sending any commands to the device as shown below.

 ```python
from scrapli_netconf.driver import NetconfDriver

my_device = {
    "host": "172.18.0.11",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
}

conn = NetconfDriver(**my_device)
conn.open()
response = conn.get_config(source="running")
```

Connections can be closed by calling the `close` method:

```python
conn.close()
```


## Get Config

Configurations can be retrieved from datastores on a netconf device using the `get-config` netconf method. The
 `get_config` method accepts a `source` argument which must refer to an available datastore on the device -- options
  for this would be one of:
  
- running
- startup
- candidate


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


## Get

Much like `get-config`, the `get` method can be used to get data from the device, generally "operational" or "show
" type data. The `get` method requires a "filter" to be applied in order to identify the data to get -- this filter
 can be one of two types -- "subtree" (default) or "xpath". In the context of network devices it seems that not many
  devices support "xpath" filters (only IOSXE with netconf 1.1 of the tested platforms supports xpath for example).


```python
from scrapli_netconf.driver import NetconfDriver

my_device = {
    "host": "172.18.0.13",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
    "port": 830
}

filter_ = """
<components xmlns="http://openconfig.net/yang/platform">
    <component>
        <state>
        </state>
    </component>
</components>"""

conn = NetconfDriver(**my_device)
conn.open()
response = conn.get(filter_=filter_, filter_type="subtree")
print(response.result)
```


## Lock and Unlock

Netconf provides the ability to lock a configuration datastore. Much like `get-config` a target datastore must be
 provided, and is dependent on the capabilities of the platform you are interacting with.

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
response = conn.lock(target="candidate")
print(response.result)
response = conn.unlock(target="candidate")
print(response.result)
```


## Commit and Discard

If your platform supports commit operations (IOS-XR and Junos in the context of scrapli_netconf tested platforms
), any changes created using the `edit-config` method will need to be committed (or discarded).

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
response = conn.commit()
print(response.result)
response = conn.discard()
print(response.result)
```


## Edit Config

To edit configs, simply use the `edit_config` method with an appropriate config payload and target.

```python
from scrapli_netconf.driver import NetconfDriver

my_device = {
    "host": "172.18.0.13",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
    "port": 830
}

cdp_config = """
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

conn = NetconfDriver(**my_device)
conn.open()
result = conn.edit_config(config=cdp_config, target="candidate")
print(result.result)
```


## Delete Config

Some devices may allow you to delete a candidate/startup configuration. You can do so with the `delete_config` method
; note that this is only currently tested on Junos as the test environment IOSXR version does not support this method
. Per the RFC, "running" is never a valid target; `scrapli_netconf` will produce a warning indicating this if
 "running" is set as the target; if `strict_datastores` is set to `True` an exception will be raised.

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
result = conn.delete_config(target="candidate")
print(result.result)
```


## RPC

The `rpc` method is a "bare-bones" rpc call which does not apply any formatting/standardization beyond the outer most
 rpc tag. Generally this is used for Juniper devices and the "bare rpc" type calls supported on junos devices not
  supporting/using models (YANG/IETF/etc.), but can of course be used to send any kind of custom crafted rpc you'd like!

```python
from scrapli_netconf.driver import NetconfDriver

my_device = {
    "host": "172.18.0.15",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
    "port": 22
}

commit_filter = """
<get-commit-revision-information>
    <level>detail</level>
</get-commit-revision-information>
"""

conn = NetconfDriver(**my_device)
conn.open()
result = conn.rpc(filter_=commit_filter)
print(result.result)
```
