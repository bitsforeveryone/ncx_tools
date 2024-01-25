#!/bin/python
import sys
sys.path.insert(0, ".")
import ncx_db
import argparse 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a target to the target list")
    #seperator
    parser.add_argument("-s", "--seperator", help="The seperator to use when parsing the target", default=" ")
    #print a newline after each target
    parser.add_argument("-n", "--newline", help="Print a newline after each target", action="store_true", default=False)
    #you can add multiple targets at once
    parser.add_argument("target", help="The target ip range to print", nargs="+")
    targeted = []
    args = parser.parse_args()
    for targets in args.target:
        ips = ncx_db.ip_range_parser(targets)
        #get the current scope and make sure the target is in the scope
        for ip in ips:
            if ncx_db.is_in_scope(ip) and ip not in targeted:
                targeted.append(ip)
                print(ip, end=args.seperator)
                if args.newline:
                    print()
            else:
                #print the stderr to the screen
                print("Warning: {} is not in the current scope. If this is intentional that\'s fine. Make sure you have properly configured the scope in the area_of_operations.py".format(ip), file=sys.stderr)
    if not args.newline:
        print()