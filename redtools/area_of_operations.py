import sys
sys.path.insert(0, ".")
import ncx_db
import argparse 
import ipaddress

while True:
    cmd = input("Enter a command: ")
    if cmd == "ls":
        print("Targets:")
        targets = ncx_db.get_targets()
        if targets:
            for target in targets:
                print(target.decode("utf-8"))
        else:
            print("No targets in the target list")
    elif cmd == "add":
        arg = input("Enter a target: ")
        if ncx_db.ip_range_parser(arg):
            if ncx_db.add_target(arg):
                print("Target added")
            else:
                print("Unable to add target")
        else:
            print("Invalid target")
    elif cmd == "rm":
        arg = input("Enter a target: ")
        if ncx_db.ip_range_parser(arg):
            if ncx_db.remove_target(arg):
                print("Target removed")
            else:
                print("Unable to remove target")
        else:
            print("Invalid target")
    elif cmd == "exit":
        break
    elif cmd == "blacklisted":
        print("Blacklisted IPs:")
        blacklisted = ncx_db.get_blacklisted()
        if blacklisted:
            for ip in blacklisted:
                print(ip)
        else:
            print("No blacklisted IPs")
    elif cmd == "blacklist":
        arg = input("Enter an IP: ")
        try: 
            if ncx_db.add_blacklisted_ip(ipaddress.ip_address(arg)):
                print("IP blacklisted")
            else:
                print("Unable to blacklist IP")
        except:
            print("Invalid IP")
    elif cmd == "unblacklist":
        arg = input("Enter an IP: ")
        try:
            if ncx_db.remove_blacklisted_ip(ipaddress.ip_address(arg)):
                print("IP unblacklisted")
            else:
                print("Unable to unblacklist IP")
        except:
            print("Invalid IP")
    else:
        print("Invalid command, valid commands are: ls, add, rm, exit, blacklisted, blacklist, unblacklist")
        
        