#!/bin/python3
import subprocess
import os
import sys
import ipaddress
sys.path.insert(0, ".")
import ncx_db
#check if running as root and exit if you are root
if os.geteuid() == 0:
    print("No running this as root, it will mess up the permissions")
    exit(1)
#check if the c3t_master_key exists, exit if it doesn't
if not os.path.exists("./c3t_master_key"):
    print("c3t_master_key not found. Make sure you are running \"python bluetools/hosts.py\" from the root of the repository")
    exit(1)
    
def print_hosts():
    h = ncx_db.get_hosts()  
    if h:
        for host in h:
            print(host.decode("utf-8"))
    else:
        print("No hosts found")
    
while True:
    c = input("> ")
    if c == "ls":
        print_hosts()
        
    elif c == "add":
        host = input("ip: ")
        user = input("user: ")
        result = subprocess.Popen(["ssh-copy-id", "-o", "StrictHostKeyChecking=no", "-i", "./c3t_master_key", user + "@" + host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        text = result.communicate()[0].decode("utf-8")
        print(text)
        return_code = result.returncode
        if return_code == 0:
            print("Host key registered successfully")
            if ncx_db.add_host(user + "@" + host):
                print("Host added successfully")
                #add host to the blacklist if it's an ip address
                try:
                    if ncx_db.add_blacklisted_ip(ipaddress.ip_address(host)):
                        print("Host blacklisted successfully")
                    else:
                        print("Host blacklisting failed, try again")
                except:
                    pass
            else:
                print("Host addition failed, try again")
        else:
            print("Host key registration failed, try again")
    #generate the config file
    elif c == "rm":
        if ncx_db.remove_host(input("host: ")):
            print("Host removed successfully")
        else:
            print("Host removal failed, try again")
    elif c == "config":
        print("Generating config file...")
        #check if the ~/.ssh/config file exists
        if os.path.exists(f"{os.path.expanduser('~')}/.ssh/config"):
            print("Config file exists")
            pass
        else:
            #create the ~/.ssh/config file
            print("Config file does not exist, creating it...")
            os.system("touch ~/.ssh/config")
        #check for the #C3T_HOSTS_START and #C3T_HOSTS_END comments, remove everything in between them and add the hosts
        middle = False
        c3t_hosts = ""
        hosts = ncx_db.get_hosts()
        for host in hosts:
            username, ip = host.decode("utf-8").split("@")
            c3t_hosts += f"Host {ip}\n"
            c3t_hosts += f"    HostName {ip}\n"
            c3t_hosts += f"    User {username}\n"
            c3t_hosts += f"    IdentityFile {os.path.abspath('./c3t_master_key')}\n"
        new_config = ""
        with open(f"{os.path.expanduser('~')}/.ssh/config", "r") as f:
            #if it doesn't have #C3T_HOSTS_START and #C3T_HOSTS_END, add them to the end of the file
            if "#C3T_HOSTS_START" not in f.read():
                new_config = f.read() + "\n#C3T_HOSTS_START\n" + c3t_hosts + "#C3T_HOSTS_END\n"
            else:
                #if it does, remove everything in between them and add the hosts
                f.seek(0)
                for line in f.readlines():
                    if "#C3T_HOSTS_START" in line:
                        middle = True
                    if not middle:
                        new_config += line
                    if "#C3T_HOSTS_END" in line:
                        middle = False
                new_config += "\n#C3T_HOSTS_START\n" + c3t_hosts + "#C3T_HOSTS_END\n"
        with open(f"{os.path.expanduser('~')}/.ssh/config", "w") as f:
            f.write(new_config)
            print("Config file generated successfully and installed. you can now use ssh to connect to the hosts with the following command: ssh <ip>, no need to specify the user or the key")
            print(new_config + "\n")