# C3T NCX Toolsuite

# setup.sh

This script will install all the tools needed to run the C3T NCX Toolsuite. It will also install the C3T NCX Toolsuite.

Select host mode only if you are the team captain. Select client mode if you are a team member. 

In order for the tools to work properly, you must NOT run the script as root.

The computers used for the engagement need to be able to talk to each other.

To launch it:
```
./setup.sh
```
And follow the prompts.

# Red Tools

## Area of Operations
Used to set the scope of the competition and blacklist friendly hosts from being scanned.

It is recommended to run this script at the beginning of the competition to set the scope and blacklist friendly hosts. This will prevent the scanner from scanning friendly hosts and will prevent the scanner from scanning out of scope hosts. Additionally it allows other tools to check if a host is in scope or not.

When you run the script, it will open up a command prompt. The commands are as follows:

```
python redtools/area_of_operations.py

Valid commands are: ls, add, rm, exit, blacklisted, blacklist, unblacklist

ls : List all the in scope ranges.

add : Add a range to the in scope ranges.

rm : Remove a range from the in scope ranges.

blacklisted : List all the blacklisted ranges.

blacklist : Blacklist a range.

unblacklist : Unblacklist a range.

```

## Forward Observer
Used to print lists of hosts for exploit scripts.

It is recommended to use this script to print lists of hosts for exploit scripts. This will allow you to easily copy and paste the list of hosts into your exploit script.

When you run the script it will spit out a list of targets. The targets are seperated by a space by default. You can change the seperator with the -s flag. You can also add a newline after each target with the -n flag.

Targets will NOT be printed if they are blacklisted or out of scope, and it will print a warning if you try to add a target that is blacklisted or out of scope.


```
usage: forward_observer.py [-h] [-s SEPERATOR] [-n] target [target ...]

Print a list of targets to use in custom scripts

positional arguments:
  target                The target ip range to print

options:
  -h, --help            show this help message and exit
  -s SEPERATOR, --seperator SEPERATOR
                        The seperator to use when parsing the target
  -n, --newline         Print a newline after each target
```

You can pipe the output of this script into another script like so:

```
python redtools/forward_observer.py | ./exploit_script.py
```

or you can write the output to a file like so:

```
python redtools/forward_observer.py > targets.txt
```


## Bermuda

Reverse shell manager.

It is recommended to run this script in a screen or tmux session. This will allow you to keep the reverse shell alive even if you disconnect from the server.

When you run the script it will open up a command prompt. The commands are as follows:

```
help: print this help message
exit: exit the server
mass_command: run a command on all the reverse shells that match the given IP range
        Usage: mass_command (target ip glob range) (command) ...
shells: list all the reverse shells that are connected
interact: interact with a reverse shell
        Usage: interact (shell_ip:shell_port)
attach: interact with a reverse shell
        Usage: attach (shell_ip:shell_port)
connect: interact with a reverse shell
        Usage: connect (shell_ip:shell_port)
upload: upload a file to a reverse shell
        Usage: upload (ip glob) (filename)
download: download a file from a reverse shell
        Usage: download (shell_ip:shell_port) (filename) [directory]
```

# Payloads

## kworker
This payload will spawn a reverse shell to the given IP and port.

To set the IP and port, edit the Makefile.

To build the payload, run the following command:

```
cd payloads/revshell
make
```

The payload will be in the payloads/revshell directory.
