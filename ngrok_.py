# Creates ngrok tunnel to access our website hosted on colab server
# The original plan is to run the script in otgher colab to see if tey work interchangably. If not then we will have to add async functionality on our original application

from pyngrok import ngrok, conf
import re 
import time

import ssl

ssl._create_default_https_context = ssl._create_unverified_context


# Helps to chnage the location to desired location
region_name = input("Enter the region: ")
conf.get_default().region = region_name
print("Default region = ",conf.get_default().region)


# <NgrokTunnel: "tcp://0.tcp.ngrok.io:12345" -> "localhost:22">
ssh_tunnel = ngrok.connect(25565, "tcp")
print(type(str(ssh_tunnel)))
print (ssh_tunnel)
print (ssh_tunnel.public_url)
reduced_string = re.sub(r'.', '',ssh_tunnel.public_url , count = 6)
print(reduced_string)


# The script runs for atleast 12 hours
time.sleep(18000)