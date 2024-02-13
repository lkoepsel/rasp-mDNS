# Raspberry Pi Startup Solution

## Description
A possible solution for identifying newly programmed *Raspberry Pi (RPI)*'s on the network. In a large network situation (*ex: community college*), the wireless network might have two issues:

1. The network is quite large, making it difficult to readily identify a *RPi* which has recently joined the network
2. The wireless network might run sans password, which previously wasn't easily handled by the *Raspberry Pi Imager* software.

This solution uses version *1.8.3* or later of the *RPi Imager* application to create an image which allows for a blank password to the wireless network. And it assigns a unique host name to make it easily identifiable, once it connects to the network.

## Solution
The solution consists of two steps:

1. Attempt to connect on startup using the *multicast DNS* service. This uses the existing solution of [*RPi avahi/zeroconfig/Bonjour*](https://www.raspberrypi.com/documentation/computers/remote-access.html#resolving-raspberrypi-local-with-mdns) to connect with the Pi. It can work quite well and is the best solution. However, it doesn't always work. And when it doesn't there needs to be a remediation step.
2. The remediation is to use a local ethernet connection (or sometimes serial) to put a startup application on the Pi, such that it pings a local server with its host name and IP address.

## Steps to Manually Ping a Server from the boot of a Raspberry Pi
### 1. Python hello.py service (on Raspberry Pi)
This will ping a **known** server by *IP address* and report **its** host name and IP address. 

**This step requires the ability to connect locally to the RPi.** There are two *easy* solutions:
* **Connect via ethernet**, by connecting an ethernet cable directly between your PC and the RPi. With this connection, you will be able to easily login using `ssh hostname.local`, replacing *hostname* with the name you used in *RPi Imager "Set hostname"*.
* **Connect via USB console using USB cable, keyboard and monitor** - Standard method of using RPi as a computer.
A **less easy solution** is to possibly connect via *USB Gadget*, for [Pi Zero](https://learn.adafruit.com/turning-your-raspberry-pi-zero-into-a-usb-gadget/ethernet-gadget), or [ethernetgadget.pdf]( https://github.com/thagrol/Guides) or using a [Pi 4](https://forums.raspberrypi.com/viewtopic.php?t=245810).
#### Installation
C
1. On the RPi In a folder of your choosing, `nano hello.py` then copy/paste contents below into file:
    ```python
    # run on RPi, once connected
    # will attempt to connect to server with hostname and address
    import logging
    import requests
    import socket


    # set logging to DEBUG, if having issues with the app starting
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
This will execute the hello.py app, after all other startup services have been launched on the RPi.
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
This will listen for all connections to it as a server and will print the host name and IP address when it is contacted by the *hello.py* client. Run this on your PC, make sure your are on the same network as the RPi wireless connection.
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

The server will be running and listening on your PC. **Reboot** your *RPi* and it will connect to the server with its host name and IP address.

To close the server, once the RPi has connected, *Ctrl-C*

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
## Notes
1. If the *RPi* isn't connecting, it might be a problem with startup. Reconnect with the *Pi* locally, using an ethernet or serial connection and use `journalctl -b` to examine the startup log. Changing the *logging to DEBUG* in the *hello.py* application, might help as well.
2. When using *RPi Imager* software, use *Shift-Ctrl-X* to bring up the options screen.
## Additional Raspberry Pi Research
## Links
* [Use Network Manager to print everything about the Pi's Network Interface](https://www.raspberrypi.com/documentation/computers/remote-access.html#network-manager)
* [Howto: ethernet gadget on Pi4B USB C](https://forums.raspberrypi.com/viewtopic.php?t=245810)
* [Five Ways to Run a Program On Your Raspberry Pi At Startup](https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/)
* [Name your PIs with mDNS](https://bloggerbrothers.com/2017/01/08/name-your-pis-with-mdns-forget-the-ips-with-zeroconf/)
* [StackExchange mDNS Pi](https://raspberrypi.stackexchange.com/questions/117206/reaching-my-pi-with-mdns-avahi)
* [Raspberry Pi Resolving .local](https://www.raspberrypi.com/documentation/computers/remote-access.html#resolving-raspberrypi-local-with-mdns)
* [Listing Bonjour Services](https://www.ralfebert.com/macos/listing-bonjour-services/)
* [Pentesting mDNS](https://book.hacktricks.xyz/network-services-pentesting/5353-udp-multicast-dns-mdns)
* [Five Ways to Run a Program On Your Raspberry Pi At Startup](https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/)
* [avahi-daemon(8): Avahi mDNS/DNS-SD daemon - Linux man page](https://linux.die.net/man/8/avahi-daemon)
* [avahi-daemon.conf(5): avahi-daemon config file - Linux man page](https://linux.die.net/man/5/avahi-daemon.conf)
* [Difference Between resolve.conf, systemd-resolve, and Avahi | Baeldung on Linux](https://www.baeldung.com/linux/resolve-conf-systemd-avahi)
  4.3. Avahi Services
  The Avahi zeroconf browser will show the various services on our network. Further, we can browse SSH and VNC servers using bssh and bvnc, respectively. Avahi advertises the *.service files found in /etc/avahi/service. Besides, the Avahi user/group should be able to read files in this directory. We can easily create our own if we want to advertise a service without the *.service file. Let’s look at an example of an Avahi file that advertises a regular FTP server – vsftpd:
  `/etc/avahi/services/ftp.service`
    ```xml
    <?XML version="1.0" standalone=’no’?>
    <!DOCTYPE service-group SYSTEM "avahi-service.dtd">
    <service-group>
    <name>FTP file sharing</name>
    <service>
    <type>_ftp._tcp</type>
    <port>21</port>
    </service>
    </service-group>
    ```
  This file allows Avahi to advertise the FTP server. As a result, we should be able to find the FTP server from a file manager on another computer within our network. We also need to enable hostname resolution on the client.
[Avahi - Debian Wiki](https://wiki.debian.org/Avahi)
* To resolve a hostname to an IPv4 address with avahi-resolve:
  `avahi-resolve -n -4 <host>.local`
* The reverse process is performed with:
  `avahi-resolve -a 192.168.7.235`
  avahi-resolve obtains an IP address or hostname directly from the mDNS multicast from hosts. It does not use the NSS functionality of libnss-mdns.
* Using avahi-browse:
  For a complete view of services and hosts on the network:
  `avahi-browse -art | less`
* For example, install the following ssh service in  /etc/avahi/services/ssh.service
    ```xml
    <?xml version="1.0" standalone='no'?><!--*-nxml-*-->
    <!DOCTYPE service-group SYSTEM "avahi-service.dtd">
    <service-group>
    <name replace-wildcards="yes">%h SSH</name>
    <service>
    <type>_ssh._tcp</type>
    <port>22</port>
    </service>
    </service-group>
    ```

