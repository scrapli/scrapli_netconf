# Security Policies and Procedures


## Disclosure Policy

Please open an issue to identify any bugs or security vulnerabilities in scrapli. There is a bug report issue template
 that you can fill out that will help get things rolling!


## Update Policy

We will do our best to make any necessary updates to keep scrapli_netconf secure, if there is a known issue/gap, this
 document will outline the issue and affected version(s) of scrapli_netconf. 


## Security Related Configurations

scrapli_netconf allows for -- and defaults to -- strict SSH host key checking (though this can be disabled). Strict
 host key checking can be disabled though, so if that worries you, don't do that! scrapli_netconf does not store any
  credential information, however of course username/password/etc. is stored in memory when using scrapli_netconf. 

## Known Security Gaps/Issues

At the moment there are no known security gaps/issues. In the future we will try to update this document with any
 issues and what version of scrapli and any dependencies are affected, however this will all be best effort, and
  there is are no guarantees/assurance that scrapli is secure; though of course effort is invested to try to make it
   as secure as possible! 