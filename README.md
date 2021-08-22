# cyberdBot [t.me/cyberdbot](https://t.me/cyberdbot)  
Telegram bot for creation cyberLinks on the cyberd knoledge graph, upload content to IPFS and monitoring [cyberd](https://github.com/cybercongress/cyberd/) node status data
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

## Commands
You can set commands in the [@BotFather](t.me/BotFather) by `/setcommands` command. The command list:
```
search - Search
cyberlink - Create cyberLink  
ipfs - Upload to IPFS  
tweet - Tweet  
check - Jail check  
validators - Validator list  
issue - Create issue or send feedback
```

## Requirements
Python 3.6 or higher
