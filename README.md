# Raspberry Pi Startup Solution

## Description
This is a solution for identifying freshly programmed, headless *Raspberry Pi (RPI)*'s on a large network. In large networks (*ex: community college*), the wireless network might have two issues:

1. As network is quite large, it can be difficult to readily identify a *RPi* which has recently joined the network, therefore making it almost impossible to connect to the *RPi*.
2. The wireless network might also use a blank password, which previously wasn't easily handled by the *Raspberry Pi Imager* software.

This solution uses version *1.8.3* or later of the *RPi Imager* application to create an image which allows for a blank password to the wireless network. It also assigns a unique host name to make it easily identifiable, once it connects to the network.

## Solution
The solution consists of two steps and an optional backup step:

1. Attempt to connect on startup using the *multicast DNS* service. This uses the existing solution of [*avahi aka zeroconfig or Bonjour*](https://www.raspberrypi.com/documentation/computers/remote-access.html#resolving-raspberrypi-local-with-mdns) to connect with the *RPi*. It can work quite well and is the best solution, however, it doesn't always work. And when it doesn't work, there needs to be a remediation step.

    Using the username and hostname you used in programming the SD card with the *Pi Imager* application, try:
    ```bash
    ssh username@hostname.local
    ```
2. In large networks this might take a while or not work at all. To mitigate this issue, try this command: (*replace hostname with the name you provided when programming the SD card*). This command tends to work faster than attempting to login immediately.
    ```bash
    dns-sd -G v4 hostname.local
    ```
    Example Output:
    ```bash
    DATE: ---Tue 13 Feb 2024---
    16:32:22.348  ...STARTING...
    Timestamp     A/R  Flags IF  Hostname      Address     TTL
    16:32:51.715  Add  2.    17  pisan.local.  192.168.1.  120
    ```
    Notice that the IP address is provided in the second line of *192.168.1.6*

    ```bash
    # Connect to the board using the IP address
    ssh 192.168.1.6
    # after a warning regarding the "...authenticity of host..." and a few seconds, you will see the CLI prompt.
    ```

**Optional** - An insurance step is to utilize this connection to implement an auto-connecting application as a startup application on the *RPi*. This application will ping a local server with its host name and IP address. This ensures you have ready access to the *RPi* without having to go through determing its IP addrss again. This is particularly important when you move to a new network.

## (Optional) Startup Application to Automatically Ping a Server
These steps will implement a small startup application on the *RPi* which pings a known IP address with its hostname and IP address.  The server's IP address is saved in the *boot* folder of the *RPi* SD card, making it easy to update.
### 1. Python hello.py service (on Raspberry Pi)
Create a startup application, which will ping a server by *IP address* and report **its own** host name and IP address.

#### Installation
1. On your *RPi* in your home folder (*/home/username/*), `nano hello.py` then copy/paste contents below into file:
    ```python
    import logging
    import requests
    import socket
    import os
    import sys


    # set logging to DEBUG, if not showing up
    logging.basicConfig(format='%(filename)s:%(levelname)s: %(message)s',
                        level=logging.DEBUG)
    logging.debug('Begin')

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

    try:
        response = requests.post(url, data=data)

    except requests.exceptions.RequestException as e:
        logging.error(e)
        sys.exit(1)

    logging.debug(response.status_code)
    logging.debug(response.text)
    ```
Once the service is working well, you may change the logging level from DEBUG to ERROR in this line: `level=logging.DEBUG` to stop the messages from appearing in the boot log.

2. Exit nano using *Ctrl-S* *Ctrl-X*
### 2. Setup `systemd` unit file for hello.py service
This will execute the hello.py app, after all other startup services have been executed on the RPi. 

If you have issues with determining if this service is executing properly, use the command `journalctl -b`, to see all boot messages of the *RPi*. You will have to go towards then end (approximately 500+ lines) to see the appropriate lines. 

You can use the space bar, to quickly go through screens of lines. Look for the word DEBUG as the *hello.py* application uses logging to print messages.

#### Installation
1. Create file, copy/paste contents below then exit *nano*. **Be sure to change *username* to what is appropriate for your system.
    ```bash
    sudo nano /lib/systemd/system/hello.service
    ```

    Copy/paste contents below into the file:
    ```bash
    [Unit]
    Description=Ping a known server (ip.txt) with hostname and IP address
    After=network-online.target
    Wants=network-online.target

    [Service]
    Type=simple
    ExecStart=/usr/bin/python /home/username/hello.py
    Restart=on-failure
    RestartSec=1
    StartLimitInterval=0
    StartLimitBurst=5

    [Install]
    WantedBy=multi-user.target
    ```

    Exit nano using *Ctrl-S* *Ctrl-X*
3. Run the following three commands:
    ```bash
      sudo chmod 644 /lib/systemd/system/hello.service
      sudo systemctl daemon-reload
      sudo systemctl enable hello.service
    ```
#### Add IP address of the server on the Boot folder
An example of *ip.txt* in in this repository, the directions to create it on the *RPi* are the following:
```bash
sudo mount /dev/mmcblk0p1 /boot
sudo nano /boot/ip.txt
```
Enter the IP address of your PC WITHOUT a return at the end of the line, then exit nano using *Ctrl-S* *Ctrl-X*. Finally, unmount boot on *RPi*.
```bash
sudo umount /boot
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
3. `python server.py`

The server will run and listening for the *RPi* on your PC. **Reboot** your *RPi* and it will connect to the server with its host name and IP address.

Once the RPi has connected and the IP address has been identified, *Ctrl-C* to exit the server program.

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
1. If the *RPi* isn't connecting, it might be a problem with startup. Reconnect with the *Pi* use `journalctl -b` to examine the startup log. Changing the *logging to DEBUG* in the *hello.py* application, might help as well.
1. Implementing the optional solution, allows you to change networks and identify your PC's new IP address. Mount the SD card on your PC and edit /bootfs/ip.txt, replacing the IP address with the new one. Put the SD card back into the *RPi*, run `python server.py` then boot the *RPi*. It will ping your server with its new address.
1. If you have multiple *RPI*'s and want to confirm which one is which, run `sudo du -h /`, which prints the size of all folders to the screen. This will make the green led light for several seconds.

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
* [How to Use Avahi to advertise a service](https://sosheskaz.github.io/tutorial/2016/09/26/Avahi-HTTP-Service.html)
* [Advertising Linux Services via Avahi/Bonjour](https://holyarmy.org/2008/01/advertising-linux-services-via-avahibonjour/)
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

