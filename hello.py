import logging
import requests
import socket
import os
import sys


# set logging to DEBUG, if not showing up
logging.basicConfig(format='%(filename)s:%(levelname)s: %(message)s',
                    level=logging.DEBUG)
logging.debug('Begin')

hadtomount = False

if not os.path.exists('/boot'):
    hadtomount = True
    os.system("sudo mount /dev/mmcblk0p1 /boot")

with open("/boot/ip.txt", "r") as f:
    ip = f.read().rstrip("\n")

if hadtomount:
    os.system("sudo umount /boot")

host_name = socket.gethostname()
logging.debug("Host name: %s  ", host_name)

url = 'http://' + ip
text = f"Hello from {host_name}"
logging.debug(url)

data = {'text': text}

try:
    response = requests.post(url, data=data)

except requests.exceptions.RequestException as e:
    logging.error(e)
    sys.exit(1)

logging.debug(response.status_code)
logging.debug(response.text)
