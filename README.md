#Least-Load-SSH

##Purpose
SSH into a server that has the least load.  It's really annoying when a server is flooded with users and I don't have any CPU cycles to run my code.

##General Method
Supply the script with a list of servers, log into all of them, execute \`who -u\` or \`uptime\` to log the useage of the server, log into the server that has the least load
