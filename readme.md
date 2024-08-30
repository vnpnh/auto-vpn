AUTO VPN
===========
This VPN Command-Line Tool allows you to connect, disconnect, check status, and manage configurations for VPN connections. The tool is designed to be simple and flexible, providing various options to suit different use cases.


## Table of Contents
- [Installation](#installation)
- [Requirements](#requirements)
- [Supported VPN Clients](#supported-vpn-clients)
- [Usage](#usage)
  - [Connecting to a VPN](#connecting-to-a-vpn)
  - [Disconnecting from a VPN](#disconnecting-from-a-vpn)
  - [Checking VPN Status](#checking-vpn-status)
  - [Create VPN Configuration](#create-vpn-configuration)
- [Contributing](#contributing)
- [License](#license)


Requirements
------------
- Windows
- VPN Client (Cisco Anyconnect)
- Python 3.10 or higher
- pip install -r requirements.txt


Supported VPN Clients:
------------
- Cisco Anyconnect


Installation Exe
------------
1. Download the latest release from the [Releases]
2. Extract the zip file
3. setup the environment variable for the extracted folder
4. setup config file. Example for cisco vpn:
```bash
vpn --set-config="C:\\Program Files (x86)\\Cisco\\Cisco AnyConnect Secure Mobility Client\\vpncli.exe" --type=cisco
```
5. setup vpn credential. Example for cisco vpn:
```bash
vpn create --config=production
```

Usage
-----
### Connecting to a VPN
You can connect to a VPN using several options depending on your needs:

**Connection using a specific configuration:**
```bash
vpn connect cisco --config=dev
vpn connect cisco -C dev
````

**Advanced connection:**
```bash
vpn connect cisco --retry 3 --delay 5
vpn connect cisco -r 3 -d 5
````

**Manual connection (with host, user, and password):**
```bash
vpn connect cisco --host=vpn.example.com --user=user --password=pass
````

**Manual connection with saved credentials:**
```bash
vpn connect cisco --host=vpn.example.com --user=user --password=pass --save=dev
````


### Disconnecting from a VPN
You can disconnect from a VPN using the following options:
**Basic disconnection:**
```bash
vpn disconnect cisco
````


### Checking VPN Status
You can check the status of a VPN connection using the following options:
**Basic status check:**
```bash
vpn status cisco
````

### Create VPN Configuration
You can create a VPN configuration using the following options:

**Create a new configuration**
```bash
vpn create --config=dev
````
After running the command above, you will be prompted to enter the following required information:

* VPN Type (required)
* Host (required)
* User (required)
* Password (required)


Compile
-------
Compile the script using pyinstaller, install first **pip install pyinstaller**.
dont use --onefile because it will detected as virus.
```cmd
pyinstaller vpn.py --icon=favicon.ico --name autovpn
```


Contributing
------------
Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or feedback.


License
-------
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

