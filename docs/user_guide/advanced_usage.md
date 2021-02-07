# Advanced Usage


## Capabilities

Netconf capabilities are exchanged when the session is opened. scrapli_netconf stores the server's capabilities in
 the aptly named `server_capabilities` attribute of the driver.

```python
>>> from scrapli_netconf.driver import NetconfDriver
>>> 
>>> my_device = {
...     "host": "172.18.0.13",
...     "auth_username": "vrnetlab",
...     "auth_password": "VR-netlab9",
...     "auth_strict_key": False,
...     "port": 830
... }
>>> conn = NetconfDriver(**my_device)
>>> conn.open()
>>> conn.server_capabilities
['urn:ietf:params:netconf:base:1.1', 'urn:ietf:params:netconf:capability:candidate:1.0']
```

*Capabilities truncated for readability*

As for capabilities that scrapli_netconf *sends* to the server, that depends on the capabilities advertised from the
 server! If netconf base 1.1 is in the advertised capabilities then scrapli_netconf will advertise netconf 1.1
  capabilities, otherwise it will advertise 1.0 capabilities.


## Datastores

scrapli_netconf drives contain an option `strict_datastores` which defaults to `False`. If this option is set to
 `True` scrapli will raise a `ValueError` when attempting to perform an operation against a datastore that has not
  been advertised as a capability by the server. With this option left to the default value of `False
  `, scrapli_netconf will simply issue a user warning.


## Using a Different Transport

Just like scrapli "core" -- scrapli-netconf supports using different libraries for "transport" -- or the actual SSH
 communication piece. By default, and like scrapli "core", scrapli-netconf uses the "system" transport. This "system
 " transport means that scrapli-netconf has no external dependencies (other than `lxml`!) as it just relies on what is
  available on the machine running the scrapli script. If you wish to swap this out, scrapli-netconf also supports
   the `paramiko`, `ssh2`, and `asyncssh` scrapli transport plugins.
    
Like scrapli "core", transport selection can be made when instantiating the scrapli connection object by passing in
 `paramiko`, `ssh2`, `asyncssh`" to force scrapli to use the corresponding transport mechanism. If you are using the
  `asyncssh` transport you must use the `AsyncNetconfScrape` driver!
  
While it will be a goal to ensure that these other transport mechanisms are supported and useful, the focus of
 scrapli development will be on the "system" SSH transport.
 
Example using `ssh2` as the transport:

```python
from scrapli_netconf import NetconfDriver

my_device = {
    "host": "172.18.0.11",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
    "transport": "ssh2"
}

with NetconfDriver(**my_device) as conn:
    print(conn.get_config())
```
