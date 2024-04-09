#!/bin/bash
# Check if correct number of arguments are provided
if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <credentials_csv_file> <ip_addresses_file> <command>"
    exit 1
fi

credentials_file="$1"
ip_file="$2"
command="$3"

# Check if files exist
if [ ! -f "$credentials_file" ]; then
    echo "Credentials file $credentials_file not found."
    exit 1
fi

if [ ! -f "$ip_file" ]; then
    echo "IP addresses file $ip_file not found."
    exit 1
fi

# Read credentials file line by line
while IFS=',' read -r username password || [ -n "$username" ]; do
    # Read IP addresses file line by line
    while IFS= read -r ip || [ -n "$ip" ]; do
        # SSH using the current combination of credentials and IP address and execute the command
        sshpass -p "$password" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$username"@"$ip" "$command" &
    done < "$ip_file"
done < "$credentials_file"
wait
