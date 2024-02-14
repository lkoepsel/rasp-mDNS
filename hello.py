import logging
import requests
import socket
import os


# set logging to DEBUG, if not showing up
logging.basicConfig(level=logging.DEBUG)
logging.debug('hello.py: Begin')

os.system("sudo mount /dev/mmcblk0p1 /boot")
with open("/boot/ip.txt", "r") as f:
    ip = f.read().rstrip("\n")
os.system("sudo umount /boot")

host_name = socket.gethostname()
logging.debug("Host name: %s  ", host_name)

url = 'http://' + ip
text = f"Hello from {host_name}"
logging.debug(url)

data = {'text': text}

response = requests.post(url, data=data)

logging.debug(response.status_code)
logging.debug(response.text)
