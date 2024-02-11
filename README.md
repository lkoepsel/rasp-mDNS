# Raspberry Pi Startup Solution

## Description
A possible solution for identifying newly programmed Raspberry Pi's on the network. In a large network situation (ex: community college), the wireless network might have two issues:

1. The network is quite large, making it difficult to readily identify a Raspberry Pi which has recently joined the network
2. The wireless network might run sans password, which previously wasn't easily handled by the Raspberry Pi Imager software.

This solution uses version 1.8.3 or later of the Raspberry Pi Imager application to create an image which allows for a blank password to the wireless network. And it assigns a unique host name to make it easily identifiable, once it connects to the network.

## Solution
The solution consists of two steps:

1. Attempt to connect on startup using the *Bonjour* service. This uses the existing solution of [*Raspberry Pi Bonjour*]() to connect with the Pi. It can work quite well and is the best solution. However, it doesn't always work. And when it doesn't there needs to be a remediation step.
2. The remediation is to use a local ethernet connection (or sometimes serial) to put a startup application on the Pi, such that it pings a local server with its host name and IP address.

## Steps
### 1. Python hello.py service (on Raspberry Pi)
This will ping a **known** server by *IP address* and report **its** host name and IP address.
#### Installation
1. In a folder of your choosing, `nano hello.py` then copy/paste contents below into file:
    ```python
    # run on Raspberry Pi, once connected
    # will attempt to connect to server with hostname and address
    import logging
    import requests
    import socket


    # set logging to DEBUG, if not showing up
    logging.basicConfig(level=logging.WARNING)
    logging.debug('hello.py: Begin')

    host_name = socket.gethostname()
    logging.debug("Host name: %s  ", host_name)

    # url must be the URL of the host server
    url = 'http://192.168.1.124'
    text = f"Hello from {host_name}"

    data = {'text': text}

    response = requests.post(url, data=data)

    logging.debug(response.status_code)
    logging.debug(response.text)
    ```

2. Exit nano using *Ctrl-S* *Ctrl-X*
3. `chmod +x hello.py`
### 2. Setup `systemd` unit file for hello.py service
This will execute the hello.py app, after all other startup services have been launched on the Raspberry Pi.
#### Installation
1. `sudo nano /lib/systemd/system/hello.service` then copy/paste contents below into file
    ```bash
    [Unit]
     Description=Hello
     After=multi-user.target

     [Service]
     Type=idle
     ExecStart=/usr/bin/python /home/lkoepsel/hello.py

     [Install]
     WantedBy=multi-user.target
    ```

2. Exit nano using *Ctrl-S* *Ctrl-X*
3. Run the following three commands:
    ```bash
      sudo chmod 644 /lib/systemd/system/hello.service
      sudo systemctl daemon-reload
      sudo systemctl enable hello.service
    ```

### 3. Python server.py app (on Server)
This will listen for all connections to it as a server and will print the host name and IP address when it is contacted by the *hello.py* client. Run this on your PC, make sure your are on the same network as the Raspberry Pi wireless connection.
#### Installation
1. `sudo nano server.py` then copy/paste contents below into file:

    ```python
    # run on server, will print attempts to contact server
    # close when client has been identified
    from flask import Flask, request

    app = Flask(__name__)


    @app.route('/', methods=['POST'])
    def print_text():
        text = request.form['text']
        print(text)
        return 'Text printed'


    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=80, debug=True)
    ```
2. Exit nano using *Ctrl-S* *Ctrl-X*
3. `chmod +x server.py` then `python server.py`
To close the server, once the Raspberry Pi has connected, *Ctrl-C*

#### Example Output of server.py:
```bash
python serverv2.py
 * Serving Flask app 'serverv2'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:80
 * Running on http://192.168.1.124:80
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 101-330-852
Hello from pitwo
192.168.1.76 - - [10/Feb/2024 16:16:36] "POST / HTTP/1.1" 200 -
Hello from pitwo
192.168.1.76 - - [10/Feb/2024 16:17:29] "POST / HTTP/1.1" 200 -
Hello from pisan
192.168.1.76 - - [11/Feb/2024 06:46:41] "POST / HTTP/1.1" 200 -
```

## Additional Raspberry Pi Research
## Links
* [Howto: ethernet gadget on Pi4B USB C](https://forums.raspberrypi.com/viewtopic.php?t=245810)
* [Five Ways to Run a Program On Your Raspberry Pi At Startup](https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/)

## Steps
1. Write appropriate image to card
2. Open firstrun.sh:
   1. remove text in second parameter after mpc-wifi 
   2. change psk='......' to 'key_mgmt=NONE
### Optional Use to add Serial port connection
3. Add *dtoverlay=dwc2* to end of **config.txt**
4. Add *modules-load=dwc2,g_ether* to **cmdline.txt**, after root wait
5. 
## Successful Connection
```bash
wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.24.1.226  netmask 255.255.0.0  broadcast 172.24.255.255
        inet6 fe80::3e4d:f30e:ac89:3eba  prefixlen 64  scopeid 0x20<link>
        ether b8:27:eb:3f:3c:0f  txqueuelen 1000  (Ethernet)
        RX packets 15116  bytes 4016901 (3.8 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 60  bytes 5855 (5.7 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

## Failed Connection
```bash
wlan0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether b8:27:eb:3f:3c:0f  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```