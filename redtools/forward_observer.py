#!/bin/python
import sys
sys.path.insert(0, ".")
import ipaddress

def ip_range_parser(ip_range_string):
    #supported formats:
    #192.168.*.3
    #192.168.1.*
    #192.168.1-225.*
    octets = ip_range_string.split(".")
    if len(octets) != 4:
        return None
    if octets[0] == "*":
        octets[0] = "0-255"
    if octets[1] == "*":
        octets[1] = "0-255"
    if octets[2] == "*":
        octets[2] = "0-255"
    if octets[3] == "*":
        octets[3] = "0-255"
    octets_possible = []
    for octet in octets:
        if "-" in octet:
            octet_range = octet.split("-")
            if len(octet_range) != 2:
                return None
            octets_possible.append(list(range(int(octet_range[0]), int(octet_range[1]) + 1)))
        else:
            octets_possible.append([int(octet)])
    ips = []
    if len(octets_possible[0]) * len(octets_possible[1]) * len(octets_possible[2]) * len(octets_possible[3]) > 10000:
        print("Too many IPs to scan, please narrow your range")
        return None
    for octet0 in octets_possible[0]:
        for octet1 in octets_possible[1]:
            for octet2 in octets_possible[2]:
                for octet3 in octets_possible[3]:
                    ips.append(ipaddress.ip_address(str(octet0) + "." + str(octet1) + "." + str(octet2) + "." + str(octet3)))
    return ips

import argparse 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print a list of targets to use in custom scripts")
    #seperator
    parser.add_argument("-s", "--seperator", help="The seperator to use when parsing the target", default=" ")
    #print a newline after each target
    parser.add_argument("-n", "--newline", help="Print a newline after each target", action="store_true", default=True)
    #you can add multiple targets at once
    parser.add_argument("target", help="The target ip range to print", nargs="+")
    targeted = []
    args = parser.parse_args()
    for targets in args.target:
        ips = ip_range_parser(targets)
        for ip in ips:
            targeted.append(ip)
            print(ip, end=args.seperator)
            if args.newline:
                print()
    if not args.newline:
        print()
