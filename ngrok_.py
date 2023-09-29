# Creates ngrok tunnel to access our website hosted on colab server
# The original plan is to run the script in otgher colab to see if tey work interchangably. If not then we will have to add async functionality on our original application

from pyngrok import ngrok, conf
# import threading
import multiprocessing
import re 
import time
import asyncio
import inspect
import ssl
import os
import subprocess

ssl._create_default_https_context = ssl._create_unverified_context


# Helps to chnage the location to desired location
# region_name = input("Enter the region: ")
# conf.get_default().region = region_name
# print("Default region = ",conf.get_default().region)

# # default port address for streamlit app is 8501
# # <NgrokTunnel: "tcp://0.tcp.ngrok.io:12345" -> "localhost:22">
# ssh_tunnel = ngrok.connect(8501, "tcp")
# print(type(str(ssh_tunnel)))
# print (ssh_tunnel)
# print (ssh_tunnel.public_url)
# reduced_string = re.sub(r'.', '',ssh_tunnel.public_url , count = 6)
# print(reduced_string)




def sleep():
    time.sleep(18000)
    print("After sleep")

# For Streamlit application
def main_init(region_name:str = 'in', port_number: int = 8051, decider:int = 1):
    print("Port number =", port_number)
    conf.get_default().region = region_name
    print("Default region = ",conf.get_default().region)
    
    # Determines the usage of terminal as it is hosted on localhost
    if decider == 1:
        ssh_tunnel = ngrok.connect(port_number, "tcp")
        print (ssh_tunnel)
        reduced_string = re.sub(r'.', '',ssh_tunnel.public_url , count = 6)
        print("Copy and paste this URL in your browser: ",reduced_string)

    # Determines the usage of streamlmit as it is seen to be hosted on a network url other than the localhost
    elif decider == 2:
        # Address of the tunnel
        # target_addr = input("Enter the target address: ")
        target_addr = 'http://172.28.0.12:8501'
        # Create a Ngrok tunnel to the target address
        public_url = ngrok.connect(addr = target_addr)

        # Print the public URL of the tunnel
        print("Copy and paste this tunnel URL in your browser :", public_url)

def async_tasks():
    
    # Getting the information of which file the function was called form
    calling_file = inspect.currentframe().f_back.f_code.co_filename
    
    if calling_file.endswith('ngrok_.py') or calling_file.endswith('frontend.py'):
        PORT_NUMBER = 8051
    else:
        PORT_NUMBER = 10000
    
    print("Calling function name =", calling_file, 'port number =', PORT_NUMBER)
    region_name = input("Enter the region: ")
    local_network_decider = int(input("Enter 1 for accessiong terminal and 2 for accessing streamit : "))
    main_init(region_name=region_name, port_number=PORT_NUMBER, decider = local_network_decider)
    print("Before Sleep")
    process_thread = multiprocessing.Process(target=sleep)
    process_thread.start()
    # The script runs for atleast 12 hours
    


if __name__ == '__main__':
    # process_thread.start()
    from pathlib import Path
    app_script = Path.cwd() / 'frontend.py'

    async_tasks()
    print("The async is working perfectly fine")
    
    # Runs the streamlit app here itself
    subprocess.run(["streamlit", "run", app_script])
