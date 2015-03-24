#!/usr/bin/env python
"""
@Author: Nicholas Piazza
@Purpose: Identify the least load server and either return it to the user 
          or launch an SSH session
"""

import argparse
import pxssh
import getpass

def main():
    #Create my argument parser
    parser = argparse.ArgumentParser()

    parser.add_argument("file", help="File containing a list of SSH servers.")
    parser.add_argument("--short-circuit", "-sc", help="If a server has 0 users logged on, stop examination of all other servers and return this server as the successful server.", action='store_true')
    args = parser.parse_args()
    
    #Read lines from a file and then strip the newlines
    with open(args.file) as f:
        servers = f.readlines()
        servers = map(lambda s: s.strip(), servers)

    serverCount = 0
    for server in servers:
        serverCount += 1
        print "Testing server %d: %s" % (serverCount, server)



if __name__ == "__main__":
    main()
