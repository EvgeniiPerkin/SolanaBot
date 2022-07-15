# Solana telegram bot
Script for monitoring the status of nodes.  
Solana must be installed on the machine that runs the script.

## Navigation
* [Description](#Brief-description-of-the-script-operation)
* [Getting Started](#getting-started)

## Brief description of the script operation
1 Loads all the necessary json files.  
2 Uploads a file with public key addresses.  
3 It cycles through these addresses and requests information from downloaded files and some information from Internet resources (in particular https://kyc-api.vercel.app ).  
4 Taking into account the conditions of the information received, the script sends out a telegram.  
```bash
usage: main.py [-h] [-c CLUSTER] [-v]

Solana telegram bot

options:
  -h, --help            show this help message and exit
  -c CLUSTER, --cluster CLUSTER
                        type of cluster - m(main) or t(test))
  -v, --verbose         increase output verbosity to DEBUG
```
## Getting Started
### Install requirements
```bash
sudo apt-get update \
&& sudo apt-get install python3 git -y \
&& git clone https://github.com/EvgeniiPerkin/SolanaBot.git \
&& cd SolanaBot \
&& mkdir files_t \
&& mkdir files_m \
&& touch addresses_t.txt \
&& touch addresses_m.txt
```
Fill in the files addresses_t.txt addresses_m.txt your key addresses.  
Fill in the file constant.py your data.  
### Start script
Mainnet
```python
python3 main.py -c m
```

TdS  
```python
python3 main.py -c t
``` 