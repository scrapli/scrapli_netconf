![](https://github.com/scrapli/scrapli_netconf/workflows/Weekly%20Build/badge.svg)
[![PyPI version](https://badge.fury.io/py/scrapli_netconf.svg)](https://badge.fury.io/py/scrapli_netconf)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


scrapli_netconf
===============

scrapli_netconf is a netconf driver built on top of [scrapli](https://github.com/carlmontanari/scrapli). The purpose
 of scrapli_netconf is to provide a fast, flexible, thoroughly tested (*coming soon TM), well typed, well documented
 , simple API that supports both synchronous and asynchronous usage. Working together scrapli and scrapli_netconf aim
  to provide a consistent (as is practical) look and feel when automating devices over telnet, SSH, or netconf (over
   SSH). 

*NOTE* This is still very much in beta, use with caution!


# Table of Contents

- [Quick Start Guide](#quick-start-guide)
  - [Installation](#installation)
  - [A Simple Example](#a-simple-example)
  - [More Examples](#more-examples)


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
  fewer dependencies. Additionally, as scrapli_netconf is just an extension of scrapli, this means that automation of
   devices over telnet, SSH, and netconf (over SSH) can be done all with an extremely consistent look and feel
   . Realistically this should cover most modes of present day network automation other than HTTP based APIs (which
    would likely have a pretty different look and feel anyway). Finally, but still quite important -- with the
     `asyncssh` transport plugin, scrapli_netconf provides asyncio support for netconf operations.


# Documentation

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


# Supported Platforms

At this time scrapli_netconf is a base implementation of very basic netconf 1.0 and netconf 1.1. It *should* work on
 anything that runs those versions of netconf, but has only been tested against the following platforms/versions:

- Cisco IOS-XE (tested on: 16.04.01)
- Cisco IOS-XR (tested on: 6.5.3)
- Juniper JunOS (tested on: 17.3R2.10)

Note that testing right now is still very limited so there may be some broken things!


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

## Basic Driver Arguments

The drivers of course need some information about the device you are trying to connect to. The most common arguments
 to provide to the driver are outlined below:
 
| Argument         | Purpose/Value                                               |
|------------------|-------------------------------------------------------------|
| host             | name/ip of host to connect to                               |
| port             | port of host to connect to (defaults to port 830)           |
| auth_username    | username for authentication                                 |
| auth_password    | password for authentication                                 |
| auth_secondary   | password for secondary authentication (enable password)     |
| auth_private_key | private key for authentication                              |
| auth_strict_key  | strict key checking -- TRUE by default!                     |
| ssh_config_file  | True/False or path to ssh config file to use                |
| strip_namespaces | True/False strip namespaces from returned XML (default True)|

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

TODO - add context manager!


# FAQ

- When given a list of filters/configs need to combine them if they are of the same top level class, ex:

```python
EDIT_INTERFACE_G_0_0_0_0 = """
<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
  <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/0</interface-name>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
      <addresses>
        <primary>
          <address>10.10.0.1</address>
          <netmask>255.255.255.0</netmask>
        </primary>
      </addresses>
    </ipv4-network>
  </interface-configuration>
</interface-configurations>
"""

EDIT_INTERFACE_G_0_0_0_1 = """
<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
  <interface-configuration>
    <active>act</active>
    <interface-name>GigabitEthernet0/0/0/1</interface-name>
    <ipv4-network xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ipv4-io-cfg">
      <addresses>
        <primary>
          <address>10.10.1.1</address>
          <netmask>255.255.255.0</netmask>
        </primary>
      </addresses>
    </ipv4-network>
  </interface-configuration>
</interface-configurations>
"""
```

the above should all be in a single parent "interface-configurations" block.

- Validate that a device supports a given operation (capabilities) before attempting to run xyz method
- Add `<default-operation>merge</default-operation>` to edit config (and maybe other methods?) (good doc: https://www
.juniper.net/documentation/en_US/junos/topics/task/configuration/netconf-configuration-setting-edit-config-mode.html)
- Need to add dry run mode(s) -- looks like `test-option`
- Need to add error-options: `error-option`
- Add copy-config && delete-config methods
- Looks like there is maybe a validate method too?
- Add options to commit -- confirmed/confirm-timeout/etc.(?)
- Add cancel-commit method


# Linting and Testing

Please see [scrapli Linting and Testing](https://github.com/carlmontanari/scrapli/blob/master/README.md#linting-and-testing)
 for details.


# Todo and Roadmap

## Todo

- TESTS!!!
- Context manager
