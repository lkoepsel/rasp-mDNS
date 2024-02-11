import logging
import requests
import socket


# set logging to DEBUG, if not showing up
logging.basicConfig(level=logging.WARNING)
logging.debug('hello.py: Begin')

host_name = socket.gethostname()
logging.debug("Host name: %s  ", host_name)

url = 'http://192.168.1.124'
text = f"Hello from {host_name}"

data = {'text': text}

response = requests.post(url, data=data)

logging.debug(response.status_code)
logging.debug(response.text)
