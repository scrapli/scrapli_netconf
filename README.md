![](https://github.com/scrapli/scrapli_netconf/workflows/Weekly%20Build/badge.svg)
[![PyPI version](https://badge.fury.io/py/scrapli_netconf.svg)](https://badge.fury.io/py/scrapli_netconf)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


scrapli_netconf
===============

scrapli_netconf is a netconf driver built on top of [scrapli](https://github.com/carlmontanari/scrapli). The purpose
 of scrapli_netconf is to provide a fast, flexible, thoroughly tested, well typed, well documented, simple API that
  supports both synchronous and asynchronous usage. Working together scrapli and scrapli_netconf aim to provide a
   consistent (as is practical) look and feel when automating devices over telnet, SSH, or netconf (over SSH). 

scrapli_netconf aims to be fully RFC compliant at some point, but at the moment does not implement all netconf
 features/methods.


# Table of Contents

- [Quick Start Guide](#quick-start-guide)
  - [Installation](#installation)
  - [A Simple Example](#a-simple-example)
  - [More Examples](#more-examples)
  - [Documentation](#documentation)
- [scrapli_netconf: What is it](#scrapli-what-is-it)
- [Related Scrapli Libraries](#related-scrapli-libraries)
- [Supported Platforms](#supported-platforms)
- [Advanced Installation](#advanced-installation)
- [Basic Usage](#basic-usage)
  - [Picking the right Driver](#picking-the-right-driver)
  - [Basic Driver Arguments](#basic-driver-arguments)
  - [Opening and Closing a Connection](#opening-and-closing-a-connection)
  - [Get Config](#get-operations)
  - [Get](#get-operations)
  - [Lock and Unlock](#lock-and-unlock)
  - [Edit Config](#edit-config)
  - [Delete Config](#delete-config)
  - [Commit and Discard](#commit-and-discard)
  - [RPC](#rpc)
- [Advanced Usage](#advanced-usage)
  - [Capabilities](#capabilities)
  - [Datastores](#datastores)
- [FAQ](#faq)
- [Linting and Testing](#linting-and-testing)


# Quick Start Guide

## Installation

In most cases installation via pip is the simplest and best way to install scrapli_netconf.
See below or [here](#advanced-installation) for advanced installation details.

```
pip install scrapli-netconf
```

## A Simple Example

```python
from scrapli_netconf.driver import NetconfScrape

my_device = {
    "host": "172.18.0.13",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
    "port": 830
}

conn = NetconfScrape(**my_device)
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

- [Basic Operations IOS-XR](/examples/basic_usage/basic_usage_iosxr.py)
- [Basic Operations Junos](/examples/basic_usage/basic_usage_junos.py)
- [Edit Config IOS-XR](/examples/edit_config/edit_config_iosxr.py)
- [Asyncio Edit Config IOS-XR](/examples/edit_config/async_edit_config_iosxr.py)


## Documentation

Documentation is auto-generated [using pdoc3](https://github.com/pdoc3/pdoc). Documentation is linted (see Linting and
 Testing section) via [pydocstyle](https://github.com/PyCQA/pydocstyle/) and
 [darglint](https://github.com/terrencepreilly/darglint).

Documentation is hosted via GitHub Pages and can be found
[here](https://scrapli.github.io/scrapli_netconf/docs/scrapli_netconf/index.html). You can also view this readme as a
 web page [here](https://scrapli.github.io/scrapli_netconf/).

To regenerate documentation locally, use the following make command:

```
make docs
```


# scrapli_netconf: What is it

scrapli_netconf is a library to help send or receive netconf messages to devices, specifically routers (though could
 be anything speaking netconf in theory). 

Netconf is an IETF network management protocol that uses XML for message encoding, and SSH (or TLS, which is not
 supported by scrapli_netconf) for transport of messages. scrapli_netconf is simply an extension of the scrapli
  "screen scraping" library that adds proper message creation, framing, and validation to allow for scrapli to be
   used as a netconf client.

scrapli_netconf adds new drivers (`NetconfScrape` and `AsyncNetconfScrape`), new transports (`NetconfTransport
` and `AsyncNetconfTransport`), and new channels (`NetconfChannel` and `AsyncNetconfChannel`) all of which inherit from
, and build on, the core scrapli components. scrapli_netconf also includes an extension of the `Response` object
 -- aptly named `NetconfResponse` that adds netconf-specific data to the existing object.

A great question to ask right now is: "why"! The primary driver is to get `ncclient` like functionality without
 needing `paramiko` for the transport so that we can take full advantage of "normal" OpenSSH options, as well as have
  fewer dependencies (only absolte required dependency is lxml!). Additionally, as scrapli_netconf is just an
   extension of scrapli, this means that automation of devices over telnet, SSH, and netconf (over SSH) can be done
    all with an extremely consistent look and feel. Realistically this should cover most modes of present day network
     automation other than HTTP based APIs (which would likely have a pretty different look and feel anyway). Finally
     , but still quite important -- with the `asyncssh` transport plugin, scrapli_netconf provides asyncio support
      for netconf operations.


# Related Scrapli Libraries

This repo is the "netconf" component scrapli project, however there are other libraries/repos in the scrapli family
 -- here is a list/link to all of the other scrapli things!

- [scrapli](https://github.com/carlmontanari/scrapli) -- the "core" project
- [scrapli_paramiko](https://github.com/scrapli/scrapli_paramiko) -- the paramiko transport driver
- [scrapli_ssh2](https://github.com/scrapli/scrapli_ssh2) -- the ssh2-python transport driver
- [scrapli_asyncssh](https://github.com/scrapli/scrapli_asyncssh) -- the asyncssh transport driver
- [nornir_scrapli](https://github.com/scrapli/nornir_scrapli) -- scrapli's nornir plugin
- [scrapli_stubs](https://github.com/scrapli/scrapli_stubs) -- scrapli type stubs


# Supported Platforms

At this time scrapli_netconf is a base implementation of netconf 1.0 and netconf 1.1 (note that scrapli is not 100
% RFC compliant in that it currently does not support all methods/options). It *should* work on anything that runs
 those versions of netconf, but has only been tested against the following platforms/versions:

- Cisco IOS-XE (tested on: 16.12.03) with Netconf 1.0 and 1.1
- Cisco IOS-XR (tested on: 6.5.3) with Netconf 1.1
- Juniper JunOS (tested on: 17.3R2.10) with Netconf 1.0

In addition to the above devices, there has been testing on various versions of Juniper SRX, QFX, and MX platforms on
 ~18ish+ code, as well as Cisco NCS devices on 6.6.2+ code, and finally there has been limited testing on Nokia devices.


# Advanced Installation

As outlined in the quick start, you should be able to pip install scrapli_netconf "normally":

```
pip install scrapli-netconf
```

To install from this repositories master branch:

```
pip install git+https://github.com/scrapli/scrapli_netconf
```

To install from this repositories develop branch:

```
pip install -e git+https://github.com/scrapli/scrapli_netconf.git@develop#egg=scrapli_netconf
```

To install from source:

```
git clone https://github.com/scrapli/scrapli_netconf
cd scrapli_netconf
python setup.py install
```

scrapli_netconf has made an effort to have as few dependencies as possible -- at this time only requiring scrapli (of
 course) and lxml. That is a bit of a lie, as right now scrapli_asyncssh (and of course asyncssh) are also required
  -- in future releases this will likely change to allow you to use scrapli_netconf with only scrapli and lxml
   installed.

As for platforms to *run* scrapli_netconf on -- it has and will be tested on MacOS and Ubuntu regularly and should
 work on any POSIX system. At this time scrapli_netconf will not run on Windows as it requires the `system` transport
  or `asyncssh` transport flavors of scrapli which are not supported on Windows. If you are on Windows and wish to try
   out scrapli_netconf you can fire up WSL, or this likely works in Cygwin as well.


# Basic Usage

## Picking the right Driver

Because netconf is a standard we don't need to deal with "platform" type drivers for scrapli_netconf! Instead there
 are only two options -- `NetconfScrape` or `AsyncNetconfScrape`, these can be imported from `scrapli_netconf.driver
 ` like so:

```python
from scrapli_netconf.driver import NetconfScrape
from scrapli_netconf.driver import AsyncNetconfScrape
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
from scrapli_netconf.driver import NetconfScrape

my_device = {
    "host": "172.18.0.11",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
}

conn = NetconfScrape(**my_device)
conn.open()
```

*NOTE* that scrapli enables strict host key checking by default!


## Opening and Closing a Connection

scrapli_netconf does *not* open the connection for you when creating your scrapli connection object in normal operations
, you must manually call the `open` method prior to sending any commands to the device as shown below.

 ```python
from scrapli_netconf.driver import NetconfScrape

my_device = {
    "host": "172.18.0.11",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
}

conn = NetconfScrape(**my_device)
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
from scrapli_netconf.driver import NetconfScrape

my_device = {
    "host": "172.18.0.13",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
    "port": 830
}

conn = NetconfScrape(**my_device)
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
from scrapli_netconf.driver import NetconfScrape

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

conn = NetconfScrape(**my_device)
conn.open()
response = conn.get(filter_=filter_, filter_type="subtree")
print(response.result)
```

## Lock and Unlock

Netconf provides the ability to lock a configuration datastore. Much like `get-config` a target datastore must be
 provided, and is dependant on the capabilities of the platform you are interacting with.

```python
from scrapli_netconf.driver import NetconfScrape

my_device = {
    "host": "172.18.0.13",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
    "port": 830
}

conn = NetconfScrape(**my_device)
conn.open()
response = conn.lock(target="candidate")
print(response.result)
response = conn.unlock(target="candidate")
print(response.result)
```


## Commit and Discard

If your platform supports commit operations (IOS-XR and Junos in the context of scrapli_netconf tested platforms
), any changes created using the `edit-config` method will need to be commited (or discarded).

```python
from scrapli_netconf.driver import NetconfScrape

my_device = {
    "host": "172.18.0.13",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
    "port": 830
}

conn = NetconfScrape(**my_device)
conn.open()
response = conn.commit()
print(response.result)
response = conn.discard()
print(response.result)
```

## Edit Config

To edit configs, simply use the `edit_config` method with an appropriate config payload and target.

```python
from scrapli_netconf.driver import NetconfScrape

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

conn = NetconfScrape(**my_device)
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
from scrapli_netconf.driver import NetconfScrape

my_device = {
    "host": "172.18.0.13",
    "auth_username": "vrnetlab",
    "auth_password": "VR-netlab9",
    "auth_strict_key": False,
    "port": 830
}

conn = NetconfScrape(**my_device)
conn.open()
result = conn.delete_config(target="candidate")
print(result.result)
```


## RPC

The `rpc` method is a "bare-bones" rpc call which does not apply any formatting/standardization beyond the outer most
 rpc tag. Generally this is used for Juniper devices and the "bare rpc" type calls supported on junos devices not
  supporting/using models (YANG/IETF/etc.), but can of course be used to send any kind of custom crafted rpc you'd like!

```python
from scrapli_netconf.driver import NetconfScrape

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

conn = NetconfScrape(**my_device)
conn.open()
result = conn.rpc(filter_=commit_filter)
print(result.result)
```


# Advanced Usage

## Capabilities

Netconf capabilities are exchanged when the session is opened. scrapli_netconf stores the server's capabilities in
 the aptly named `server_capabilities` attribute of the driver.

```python
>>> from scrapli_netconf.driver import NetconfScrape
>>> 
>>> my_device = {
...     "host": "172.18.0.13",
...     "auth_username": "vrnetlab",
...     "auth_password": "VR-netlab9",
...     "auth_strict_key": False,
...     "port": 830
... }
>>> conn = NetconfScrape(**my_device)
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


# FAQ

- Question: Why build this? ncclient exists?
  - Answer: After building scrapli it was apparent that it could be fairly easily extended to handle netconf
   connections, at the time dayjob$ had lots of netconf-y things with ncclient happening. I'm not a big fan of
    ncclient as I find it rather obtuse/hard to understand whats going on, and the dependency on paramiko is not
     super great. I figured I could support enough netconf things with system transport so... I did. Then it was
      fairly trivial to add asyncssh to support netconf with asyncio!
- Question: Is this better than ncclient?
  - Answer: Nope! Supporting asyncio may be a killer use case for some, but otherwise ncclient and scrapli_netconf
   accomplish much of the same things -- probably with ncclient having a wider/deeper range of netconf rfc support
   . Net/net though is they are just different! Use whichever you prefer! 
- Question: Is this easy to use?
  - Answer: Biased, but I think so! A big part of the goal of all of this was to have a consistent feel across ssh
   and netconf both with sync and async support, and (again, biased) I think that has been achieved.
- Other questions? Ask away!


# Linting and Testing

Please see [scrapli Linting and Testing](https://github.com/carlmontanari/scrapli/blob/master/README.md#linting-and-testing)
 for details.
