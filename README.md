# cyberdBot [t.me/cyberdbot](https://t.me/cyberdbot)  
Telegram bot for [cyberd](https://github.com/cybercongress/cyberd/) node status data and upload content to IPFS
## Install
Install [IPFS node](https://docs-beta.ipfs.io/install/command-line-quick-start/)  
Install [cyberd node](https://cybercongress.ai/docs/cyberd/run_validator/)  
Clone repository:
```bash 
git clone https://github.com/Snedashkovsky/cyberdBot
```
Install requirements 
```bash
pip3 install --user -r cyberdBot/requirements.txt
sudo apt-get install expect
```
Add your Telegram Bot Token, cyberd key name and cyberd passphrase into `start_bot.sh`
## Run
```bash  
./start_bot.sh  m|main|s|scheduler  [d|dev]

Using:
   m|main - Main Bot
   s|scheduler - Monitoring Scheduler
   [d|dev] - Development Mode
```
## Test
```
python3 -m pytest -s -v *.py src/*.py
```

## Requirements
Python 3.6 or higher