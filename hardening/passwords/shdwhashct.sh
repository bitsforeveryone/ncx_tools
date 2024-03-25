#!/bin/sh

# Check if the script is running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

# Path to the rockyou wordlist (update this if your path is different)
rockyou_path="/home/justin/ncx_tools/rockyou.txt"


#unshadow the passwd and shadow files
unshadow /etc/passwd /etc/shadow > ./unshadowed

#crack the hashes with john
john --format=crypt --wordlist=$rockyou_path ./unshadowed
