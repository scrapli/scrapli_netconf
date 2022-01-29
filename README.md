[![Supported Versions](https://img.shields.io/pypi/pyversions/scrapli-netconf.svg)](https://pypi.org/project/scrapli-netconf)
[![PyPI version](https://badge.fury.io/py/scrapli-netconf.svg)](https://badge.fury.io/py/scrapli-netconf)
[![Weekly Build](https://github.com/scrapli/scrapli_netconf/workflows/Weekly%20Build/badge.svg)](https://github.com/scrapli/scrapli_netconf/actions?query=workflow%3A%22Weekly+Build%22)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-blueviolet.svg)](https://opensource.org/licenses/MIT)

scrapli_netconf
===============

---

**Documentation**: <a href="https://scrapli.github.io/scrapli_netconf" target="_blank">https://scrapli.github.io/scrapli_netconf</a>

**Source Code**: <a href="https://github.com/scrapli/scrapli_netconf" target="_blank">https://github.com/scrapli/scrapli_netconf</a>

**Examples**: <a href="https://github.com/scrapli/scrapli_netconf/tree/master/examples" target="_blank">https://github.com/scrapli/scrapli_netconf/tree/master/examples</a>

---

scrapli_netconf is a NETCONF driver built on top of scrapli, giving you all the scrapli behaviour you know and love, 
but for NETCONF connections.


#### Key Features:

- __Easy__: Just like scrapli, scrapli_netconf is easy to get going with, and looks and feels just like "normal" 
  scrapli -- check out the documentation and example links above, and you'll be connecting to devices in no time.
- __Fast__: Do you like to go fast? Of course you do! scrapli_netconf supports all of the ssh transports that 
  scrapli core supports; check out the `ssh2` transport if you've got the need for speed!
- __Great Developer Experience__: scrapli_netconf has great editor support thanks to being fully typed; that plus 
  thorough docs make developing with scrapli a breeze.
- __Well Tested__: Perhaps out of paranoia, but regardless of the reason, scrapli_netconf has lots of tests! Unit tests 
  cover the basics, regularly ran functional tests connect to virtual routers to ensure that everything works IRL! 
- __Concurrency on Easy Mode__: [Nornir's](https://github.com/nornir-automation/nornir) 
  [scrapli plugin](https://github.com/scrapli/nornir_scrapli) gives you all the normal benefits of scrapli __plus__ 
  all the great features of Nornir.


## Requirements

MacOS or \*nix<sup>1</sup>, Python 3.7+

scrapli_netconf's only requirements are `scrapli`, of course, and `lxml`.

<sup>1</sup> Although many parts of scrapli *do* run on Windows, Windows is not officially supported


## Installation

```
pip install scrapli_netconf
```

See the [docs](https://scrapli.github.io/scrapli_netconf/user_guide/installation) for other installation methods/details.



## A Simple Example

```python
from scrapli_netconf.driver import NetconfDriver

my_device = {
    "host": "172.18.0.13",
    "auth_username": "scrapli",
    "auth_password": "scrapli",
    "auth_strict_key": False,
    "port": 830
}

conn = NetconfDriver(**my_device)
conn.open()
response = conn.get_config(source="running")
print(response.result)
```
