#!/bin/sh

# Check if the script is running as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root"
  exit
fi

# Extract hashes from the shadow file
awk -F':' '{ print $2 }' /etc/shadow > extracted_hashes.txt

# Path to the rockyou wordlist (update this if your path is different)
rockyou_path="/path/to/rockyou.txt"

# Function to determine hashcat mode based on hash prefix
get_hashcat_mode() {
    case "$1" in
        \$1\$*) echo "500" ;;  # MD5 Crypt
        \$2a\$*|\$2b\$*|\$2y\$*) echo "3200" ;;  # Blowfish
        \$5\$*) echo "7400" ;;  # SHA-256 Crypt
        \$6\$*) echo "1800" ;;  # SHA-512 Crypt
        *) echo "Unknown" ;;
    esac
}

# Read each hash and attempt to identify and crack it
while IFS= read -r hash; do
    hash_type=$(get_hashcat_mode "$hash")

    if [ "$hash_type" = "Unknown" ]; then
        echo "Unknown or unsupported hash type for hash: $hash"
    else
        echo "Cracking hash of type $hash_type: $hash"
        # Use -w 4 for maximum performance and --force to enable GPU acceleration
        echo $hash | hashcat -m $hash_type -a 0 -w 4 -O --force $rockyou_path
    fi
done < extracted_hashes.txt

echo "Hash cracking complete."
