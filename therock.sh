#!/bin/bash

sudo apt-get -y install git net-tools procps --no-install-recommends
git clone github.com/konstruktoid/hardening.git
cd hardening
sudo bash ubuntu.sh
