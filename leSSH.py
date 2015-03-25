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


"""
@Class: result
@Attribute: server : The FQDN or IP address of the target server.
@Attribute: num_users : Number of users currently logged on - 1 for your connection.
@Attribute: list_users: Individual lines of output from the `who -u` command.
"""
class result:
    server     = str()
    num_users  = int()
    list_users = list()
 
"""
@Function: worker
@Description: Worker for each process spawned to test the SSH server.
@Parameter: server : The target SSH server to be tested.
@Parameter: username : The username to log in with.
@Parameter: password : The password to log in with.
@Returns: Zero (0) if successful, negative 1 (-1) if there is an error.
"""
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

    #Initiate testing of the server
    print("Testing {}".format(server))
    s.sendline('who -u')                #Send the `who -u` command for testing
    s.prompt()                          #Synchronize with the prompt
    
    #Put each line into an array and ignore the first entry holding the command
    outputArray = filter(None, s.before.split('\r\n'))     
    outputArray = outputArray[1:]
    
    #Create a result object to hold the information
    r = result()
    r.server = server
    r.num_users = len(outputArray) - 1
    r.list_users = outputArray

    #Append the information to the global array and quit
    results.append(r)
    s.logout()

"""
@Function: main
@Description: Main function for execution.  Creates individual threads to test each of the SSH servers
"""
def main():
    #Create my argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="File containing a list of SSH servers.")
    '''
    Options to be added soon:
    #parser.add_argument("-sc", "--short-circuit", help="If a server has 0 users logged on, stop examination of all other servers and return this server as the successful server.", action='store_true')
    #parser.add_argument("-k", "--key-file", help="Specify a private key for login.")
    '''
    parser.add_argument("--sentence", "-s", help="Print the final output in a sentence", action='store_true')
    args = parser.parse_args()
    
    
    #Create a global results list for all worker threads to append to
    global results
    results = list()

    #Initialize array of servers and try to open the file of servers
    servers = list()
    try:
        with open(args.filename) as f:
            servers = f.readlines()
            servers = map(lambda s: s.strip(), servers)
    except:
        print("Cannot open file {} for reading.".format(args.filename))

    #get the username and the password
    username = raw_input("username: ")
    password = getpass.getpass("password: ")

    #Create an empty list of threads
    threads = []
    
    #Iterate through the list of servers and create a thread to handle testing
    for server in servers:
        thread = Thread(target=worker, args=(server, username, password))
        thread.start()
        threads.append(thread)

    #Join the threads back together after execution
    for thread in threads:
        thread.join()

    #Find the server with the least number of users
    first = True
    least = result()
    for res in results:
        if first == True:
            first = False
            least = res
        elif res.num_users < least.num_users:
            least = res

    #Print out the server with the least number of users
    if args.sentence:
        print "The server with the least number of users is {} which has {} users".format(least.server, least.num_users)
    else:
        print "{}\t{}".format(least.server, least.num_users)

if __name__ == "__main__":
    sys.exit(main())
