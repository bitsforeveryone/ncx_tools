#!/bin/bash

# Script must NOT be run as root
if [ "$EUID" -eq 0 ]; then
  echo "Do not run this script as root"
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

sudo apt install -y python3-full python3-pip python3-venv
#create the virtual environment
python3 -m venv venv
#activate the virtual environment
source venv/bin/activate
#install the requirements
pip install -r requirements.txt
#print a message to the user saying that they must activate the virtual environment every time they want to run the tool
echo "You must activate the virtual environment every time you want to run the tools here. Run 'source venv/bin/activate' to activate the virtual environment."

# ask if the user is the host or the client
echo "Are you the host or the client? Only one person on the team should be the host."
select yn in "Host" "Client"; do
    case $yn in
        Host ) 
          echo "You are the host"; 
          # Generate the redis password
          echo "Generating redis password. Share this via a secure channel."
          REDIS_PASSWORD=$(openssl rand -base64 32)
          echo "Redis password: $REDIS_PASSWORD"
          # Write the password to the redis password file
          echo "Writing redis password to file"
          echo REDISCLI_AUTH=$REDIS_PASSWORD > .redis_env
          echo "Writing redis host IP to file"
          echo HOST_IP=localhost >> .redis_env
          echo REDIS_PORT=6379 >> .redis_env
          #setup the redis server
          echo "Setting up redis server"
          sudo docker run -d --name ncx_database -p 6379:6379 -v ./ncx_database:/data -d redis redis-server --appendonly yes --requirepass $REDIS_PASSWORD
          source .redis_env 
          export REDIS_PASSWORD=$REDIS_PASSWORD
          # Generate the SSH master key
          read -p "Press enter to continue"
          echo "Generating SSH master key. Install this key on the client machines."
          read -p "Press enter to continue"
          ssh-keygen -t rsa -b 4096 -f ./c3t_master_key -q -N ""
          echo "SSH master key generated and placed in ./c3t_master_key"
          #move the master key to the redis server
          echo "Moving the master key to the redis server"
          sudo docker run --network host --rm redis redis-cli -h localhost -a $REDIS_PASSWORD set c3t_master_key_pub "$(cat ./c3t_master_key.pub)"
          sudo docker run --network host --rm redis redis-cli -h localhost -a $REDIS_PASSWORD set c3t_master_key_priv "$(cat ./c3t_master_key)"
          select yn in "Yes" "No"; do
            case $yn in
              Yes ) 
                python redtools/area_of_operations.py
                break;;
              No ) 
                break;;
            esac
          done
          break;;
        Client ) 
          echo "You are the client"; 
          # Get the redis password from the host
          echo "Enter the redis password: "
          read REDIS_PASSWORD
          echo "Enter the hoster's IP address (Talk to your team lead if you don't know this): "
          read HOST_IP
          # Get the redis port
          echo "Enter the redis port [enter to set default of 6379]: "
          read REDIS_PORT -i "6379"
          #write the password to the redis password file
          echo "Writing redis password to file"
          echo REDISCLI_AUTH=$REDIS_PASSWORD > .redis_env
          echo "Writing host to file"
          echo HOST_IP=$HOST_IP >> .redis_env
          echo "Writing redis port to file"
          echo REDIS_PORT=$REDIS_PORT >> .redis_env
          source .redis_env
          #download the master key from the redis server
          echo "Downloading the master key from the redis server"
          sudo sudo docker run --network host --rm redis redis-cli -p 17139 -h $HOST_IP -p $REDIS_PORT -a $REDIS_PASSWORD get c3t_master_key_pub > ./c3t_master_key.pub
          sudo docker run --network host --rm redis redis-cli -p 17139 -h $HOST_IP -p $REDIS_PORT -a $REDIS_PASSWORD get c3t_master_key_priv > ./c3t_master_key
          #ask the user if they want to run redtools/area_of_operations.py to set the enemy and friendly hosts
          echo "Do you want to run redtools/area_of_operations.py to set the enemy and friendly hosts? [y/n]"
          break;;
    esac
done
CURRENT_USER=$(whoami)
echo "Setting permissions on the master key so they are owned by $CURRENT_USER"
sudo chown $CURRENT_USER:$CURRENT_USER ./c3t_master_key
sudo chown $CURRENT_USER:$CURRENT_USER ./c3t_master_key.pub
chmod 600 ./c3t_master_key.pub
chmod 600 ./c3t_master_key