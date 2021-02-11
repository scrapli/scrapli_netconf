# Project Details


## What is scrapli_netconf

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
  fewer dependencies (only absolute required dependency is lxml!). Additionally, as scrapli_netconf is just an
   extension of scrapli, this means that automation of devices over telnet, SSH, and netconf (over SSH) can be done
    all with an extremely consistent look and feel. Realistically this should cover most modes of present day network
     automation other than HTTP based APIs (which would likely have a pretty different look and feel anyway). Finally
     , but still quite important -- with the `asyncssh` transport plugin, scrapli_netconf provides asyncio support
      for netconf operations.


## Supported Platforms

At this time scrapli_netconf is a base implementation of netconf 1.0 and netconf 1.1 (note that scrapli is not 100
% RFC compliant in that it currently does not support all methods/options). It *should* work on anything that runs
 those versions of netconf, but has only been tested against the following platforms/versions:

- Cisco IOS-XE (tested on: 16.12.03) with Netconf 1.0 and 1.1
- Cisco IOS-XR (tested on: 6.5.3) with Netconf 1.1
- Juniper JunOS (tested on: 17.3R2.10) with Netconf 1.0

In addition to the above devices, there has been testing on various versions of Juniper SRX, QFX, and MX platforms on
 ~18ish+ code, as well as Cisco NCS devices on 6.6.2+ code, and finally there has been limited testing on Nokia devices.
