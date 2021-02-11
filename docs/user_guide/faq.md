# FAQ

* Question: Why build this? ncclient exists?
    - Answer: After building scrapli it was apparent that it could be fairly easily extended to handle netconf
   connections, at the time dayjob$ had lots of netconf-y things with ncclient happening. I'm not a big fan of
    ncclient as I find it rather obtuse/hard to understand whats going on, and the dependency on paramiko is not
     super great. I figured I could support enough netconf things with system transport so... I did. Then it was
      fairly trivial to add asyncssh to support netconf with asyncio!
* Question: Is this better than ncclient?
    - Answer: Nope! Supporting asyncio may be a killer use case for some, but otherwise ncclient and scrapli_netconf
   accomplish much of the same things -- probably with ncclient having a wider/deeper range of netconf rfc support
   . Net/net though is they are just different! Use whichever you prefer! 
* Question: Is this easy to use?
    - Answer: Biased, but I think so! A big part of the goal of all of this was to have a consistent feel across ssh
   and netconf both with sync and async support, and (again, biased) I think that has been achieved.
* Other questions? Ask away!
