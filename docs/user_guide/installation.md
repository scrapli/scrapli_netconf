# Installation


## Standard Installation

As outlined in the quick start, you should be able to pip install scrapli_netconf "normally":

```
pip install scrapli_netconf
```


## Installing current master branch

To install from the source repositories master branch:

```
pip install git+https://github.com/scrapli/scrapli_netconf
```


## Installing current develop branch

To install from this repositories develop branch:

```
pip install -e git+https://github.com/scrapli/scrapli_netconf.git@develop#egg=scrapli_netconf
```


## Installation from Source

To install from source:

```
git clone https://github.com/scrapli/scrapli_netconf
cd scrapli_netconf
python setup.py install
```


## Optional Extras

Just like scrapli "core" scrapli_netconf tries to have as few dependencies as possible. scrapli_netconf requires 
scrapli (of course!) and `lxml`. If you would like to use any of the transport plugins that are not part of the 
standard library you can install those as optional extras via pip:

```
pip install scrapli_netconf[paramiko]
```

The available optional installation extras options are:

- paramiko
- ssh2
- asyncssh


## Supported Platforms

As for platforms to *run* scrapli on -- it has and will be tested on MacOS and Ubuntu regularly and should work on 
any POSIX system. Windows at one point was being tested very minimally via GitHub Actions builds, however this is no 
longer the case as it is just not worth the effort. While scrapli/scrapli_netconf should work on Windows when 
using the paramiko or ssh2-python transport drivers, it is not "officially" supported. It is *strongly* 
recommended/preferred for folks to use WSL/Cygwin instead of Windows.
