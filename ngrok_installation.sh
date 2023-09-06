#!/bin/bash

# Download and install Ngrok
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
unzip ngrok-stable-linux-amd64.zip
rm ngrok-stable-linux-amd64.zip
chmod +x ngrok
sudo mv ngrok /usr/local/bin/

# Add your Ngrok authentication token
read -p "Enter your Ngrok authentication token: " authtoken
ngrok authtoken "$authtoken"

echo "Ngrok setup complete."