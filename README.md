#Least-Load-SSH

##Purpose
SSH into a server that has the least load.  It's really annoying when a server is flooded with users and I don't have any CPU cycles to run my code.

##Usage
```
$ python leSSH.py --help
usage: leSSH.py [-h] [--sentence] filename

positional arguments:
  filename        File containing a list of SSH servers.

  optional arguments:
    -h, --help      show this help message and exit
      --sentence, -s  Print the final output in a sentence
```

##Dependencies
This script uses, `pxssh`, which is part of `pexpect`.  Please see [installation instructions](http://pexpect.readthedocs.org/en/latest/install.html).

##General Method
Supply the script with a list of servers, either as an FQDN or an IP address, log into all of them, execute \`who -u\` to log the number of users on the server, return the server that has the least number of users logged in.
