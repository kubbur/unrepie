# UnrePie

UnrePie is a tool to manage an Unraid server from a Raspberry Pi with a relay hat.

## Installation

Clone the repository and install the package:

```bash
git clone https://github.com/kubbur/unrepie.git
cd unrepie
pip install .
 ```
you might want to add the binary folder to path
 ```
echo 'export PATH=$PATH:/home/username/.local/bin' >> ~/.bashrc
source ~/.bashrc
 ```
replace username with your username

## Usage
Run the program:


unrepie


## Features
Hard Power: Control the power relay.

Hard Restart: Control the restart relay.

Soft Restart: Restart the server via SSH.

Soft Power: Power down the server via SSH.

Ping: Monitor the server's ping response times.


## Configuration
On the first run, you will be prompted to configure the server connection settings. You can update these settings anytime by selecting the "Configure" option.
