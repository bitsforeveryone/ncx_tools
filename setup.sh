#!/bin/bash

# Script must be run as root
if [ "$EUID" -ne 0 ]
  then echo "Please setup as root"
  exit
fi
# Check if docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo "Docker is not installed. Installing docker"
  read -p "Press enter to continue"
  # Install docker
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  # Add the current user to the docker group
  echo "Adding current user to docker group"
  sudo usermod -aG docker $USER
  # Remove the docker install script
  echo "Removing docker install script"
  rm get-docker.sh
  #start the docker service
  echo "Starting docker service"
  systemctl start docker
fi

# ask if the user is the host or the client
echo "Are you the host or the client?"
select yn in "Host" "Client"; do
    case $yn in
        Host ) 
          echo "You are the host"; 
          # Generate the redis password
          echo "Generating redis password"
          REDIS_PASSWORD=$(openssl rand -base64 32)
          echo "Redis password: $REDIS_PASSWORD"
          # Write the password to the redis password file
          echo "Writing redis password to file"
          echo REDISCLI_AUTH=$REDIS_PASSWORD > redis_password.txt
          #setup the redis server
          echo "Setting up redis server"
          docker run -d --name ncx_database -p 6379:6379 -v ./redis-data:/data -d redis redis-server --appendonly yes --requirepass $REDIS_PASSWORD
          source redis_password.txt
          export REDIS_PASSWORD=$REDIS_PASSWORD
          # Generate the SSH master key
          read -p "Press enter to continue"
          echo "Generating SSH master key. Install this key on the client machines."
          read -p "Press enter to continue"
          ssh-keygen -t rsa -b 4096 -f ./c3t_master_key -q -N ""
          echo "SSH master key generated and placed in ./c3t_master_key"
          #move the master key to the redis server
          echo "Moving the master key to the redis server"
          docker run --network host --rm redis redis-cli -h localhost -a $REDIS_PASSWORD set c3t_master_key_pub "$(cat ./c3t_master_key.pub)"
          docker run --network host --rm redis redis-cli -h localhost -a $REDIS_PASSWORD set c3t_master_key_priv "$(cat ./c3t_master_key)"
          #set the permissions on the master key
          echo "Enter your username (not root): "
          read USERNAME
          echo "Setting permissions on the master key"
          chown $USERNAME:$USERNAME ./c3t_master_key
          break;;
        Client ) 
          echo "You are the client"; 
          # Get the redis password from the host
          echo "Enter the redis password: "
          read REDIS_PASSWORD
          echo "Enter the hoster's IP address (Talk to your team lead if you don't know this): "
          read HOST_IP
          #write the password to the redis password file
          echo "Writing redis password to file"
          echo REDISCLI_AUTH=$REDIS_PASSWORD > redis_password.txt
          source redis_password.txt
          #download the master key from the redis server
          echo "Downloading the master key from the redis server"
          docker run --network host --rm redis redis-cli -h $HOST_IP -a $REDIS_PASSWORD get c3t_master_key_pub > ./c3t_master_key.pub
          docker run --network host --rm redis redis-cli -h $HOST_IP -a $REDIS_PASSWORD get c3t_master_key_priv > ./c3t_master_key
          #set the permissions on the master key
          echo "Enter your username (not root): "
          read USERNAME
          echo "Setting permissions on the master key"
          chown $USERNAME:$USERNAME ./c3t_master_key.pub
          chown $USERNAME:$USERNAME ./c3t_master_key
          chmod 600 ./c3t_master_key.pub
          chmod 600 ./c3t_master_key

          break
        ;;
    esac
done