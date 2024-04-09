#!/bin/bash
# Check if correct number of arguments are provided
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <private_key_file> <ip_addresses_file> <command>"
    exit 1
fi

private_key="$1"
ip_file="$2"
command="$3"

# Check if files exist
if [ ! -f "$private_key" ]; then
    echo "Private key file $private_key not found."
    exit 1
fi

if [ ! -f "$ip_file" ]; then
    echo "IP addresses file $ip_file not found."
    exit 1
fi

# Read IP addresses file line by line
while IFS= read -r ip || [ -n "$ip" ]; do
    # SSH using the private key and IP address and execute the command
    ssh -o ConnectTimeout=10 -i "$private_key" -o StrictHostKeyChecking=no "$ip" "$command" &
done < "$ip_file"
wait
