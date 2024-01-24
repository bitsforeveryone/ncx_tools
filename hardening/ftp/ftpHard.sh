#!/bin/bash

# Check if vsftpd is installed
if ! command -v vsftpd &> /dev/null
then
    echo "FTP not present on this machine."
    exit
fi

# Backup the original configuration file
cp /etc/vsftpd.conf /etc/vsftpd.conf.bak

# Configure vsftpd
cat <<EOL > /etc/vsftpd.conf
listen=NO
listen_ipv6=YES
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=022
dirmessage_enable=YES
use_localtime=YES
xferlog_enable=YES
connect_from_port_20=YES
chroot_local_user=YES
secure_chroot_dir=/var/run/vsftpd/empty
pam_service_name=vsftpd
pasv_enable=YES
pasv_min_port=40000
pasv_max_port=40100
userlist_enable=YES
userlist_file=/etc/vsftpd.userlist
userlist_deny=NO
EOL

# Create a userlist file and add allowed users
echo echo $(whoami) >> /etc/vsftpd.userlist

# Restart vsftpd service
systemctl restart vsftpd

RED='\033[0;31m'
ORANGE='\033[0;33m'
echo "${RED}THE ONLY USER ABLE TO ACCESS FTP CURRENTLY IS YOUR USER. YOU NOW NEED TO MANUALLY ADD THE SCORING USER TO ${ORANGE}/etc/vsftpd.userlist"

