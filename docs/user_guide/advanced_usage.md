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


## A Note about Filters

The `filter_` string value for the `get` and `get_config` methods may contain multiple xml elements at its "root" 
(for subtree filters) -- when cast to an lxml etree object this would normally result in the first filter being the 
only element in the resulting object. This is because `etree.fromstring` assumes (rather correctly) that this is the 
root of the document, and it ignores the remaining filter elements. In example, given the following string data:

```
<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
    <interface-configuration>
        <active>act</active>
    </interface-configuration>
</interface-configurations>
<netconf-yang xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-man-netconf-cfg">
</netconf-yang>
```

The resulting lxml object (when re-dumped back to string) would look like this:

```
<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
    <interface-configuration>
        <active>act</active>
    </interface-configuration>
</interface-configurations>
```

This is.... shall we say not ideal if we want to pass in a string like the previous section to filter for multiple 
things in our config. To cope with this scrapli_netconf will wrap the user provided string filter in a "tmp" tag, 
which allows us to load up the filter with all element(s) intact; we then simply ditch the outer temp tag when 
placing the filter element(s) into the final filter payload, allowing users to simply provide a big string 
containing as many or few filters as they want.

If you preferred to craft your payloads more... "correctly" shall we say, then you are welcome to do so, and 
provide the valid lxml object to the `rpc` method. The `rpc` method does nothing but wrap the provided element in 
the outer-most xml tags needed for a NETCONF payload, so your provided element would need to contain the 
get/filter/edit/etc. tags as appropriate!
