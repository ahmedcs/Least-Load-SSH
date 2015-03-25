#!/usr/bin/env python
"""
@Author: Nicholas Piazza
@Description: Identify the SSH server with the least load and return it to the user
"""

import sys                          #To drive the program
import argparse                     #To parse all of the arguments
import pxssh                        #Connect to servers and execute commands
import getpass                      #To get the password relatively securely
from threading import Thread, Lock  #For multiple threads for each connection
import time                         #To wait in between connection attempts


#create a class for the results
class result:
    server     = str()
    num_users  = int()
    list_users = list()
 
    def __init__(self, serv, num, ls_users):
        server     = serv
        num_users  = num
        list_users = ls_users
        

#Worker for each process spawned
def worker(server, username, password):#, lock):
    #Try each server 3 times (0, 1, 2)
    for tries in range(3):
        #Try to create the pxssh object and log into it
        #If successful, execute the commands
        try:
            s = pxssh.pxssh()
            s.login(server, username, password, login_timeout=3)
            break
        except pxssh.ExceptionPxssh, e:
            err = str(e).split('\n')[0]
            
            #password error
            if "password".upper() in err.upper():
                print("Error {}: {}".format(server, err))
                return -1
            
            #Connection refused error
            if "could not set shell prompt".upper() in err.upper() or \
                    "EOF" in err.upper():
                print("Error {}: {}".format(server, "Connection Refused"))
                if tries == 2:
                    return -1
            
            #If we have tried 3 times and still nothing, then we shall quit
            if tries == 2:
                print("Error {}: {}".format(server, err))
                return -1
            
            #Sleep for half a second and then try it again
            time.sleep(.5)
    
    #If the connection died for some reason, then quit
    if not s.isalive():
        return -1

    print("Testing {}".format(server))  #Print the server that we are testing
    s.sendline('who -u')              #Send the `hostname` command for test
    s.prompt()                          #Synchronize with the prompt
    outputArray = filter(None, \
            s.before.split('\r\n'))
    outputArray = outputArray[1:]
    print type(s.before)
    print s.before                    #Print the results of the command
    print outputArray
    summary = result(server, len(outputArray) - 1, outputArray)
    results.append(summary)
    s.logout()                          #Logout of the server


def main():
    #Create my argument parser
    parser = argparse.ArgumentParser()

    parser.add_argument("filename", help="File containing a list of SSH servers.")
    #parser.add_argument("-sc", "--short-circuit", help="If a server has 0 users logged on, stop examination of all other servers and return this server as the successful server.", action='store_true')
    #parser.add_argument("-k", "--key-file", help="Specify a private key for login.")
    args = parser.parse_args()
    
    global results
    results = list()
    #Initialize array of servers
    servers = []
    try:
        with open(args.filename) as f:
            servers = f.readlines()
            servers = map(lambda s: s.strip(), servers)
    except:
        print("Cannot open file {} for reading.".format(args.filename))

    #get the username and the password
    username = raw_input("username: ")
    password = getpass.getpass("password: ")

    threads = []    #Create an empty list of threads
    #lock = lock()   #Create a lock object for threading
    
    for server in servers:
        thread = Thread(target=worker, args=(server, username, password))#, lock))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print "NOW PRINTING THE SUMMARY OF THE STUFF!!!!"
    print results

    first = True
    for result in results:
        if first == True:
            first = False
            least = result
        elif result[1] < least[1]:
            least = []
            least.append(result)
        elif result[1] == least[1]:
            least.extend(result)

    if len(least) == 1:
        print "The server with the least number of users is:"
        print "{}\t{}".format(least[0][0],least[0][1])
    elif len(least) > 1:
        print least
        print "The servers with the least number of users are:"
        for index in range(0, len(least)):
            print "Index>> {}".format(index)
            print least[index]
    elif len(least) < 1:
        print "Something has gone terribly wrong"
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
