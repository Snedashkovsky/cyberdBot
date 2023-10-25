# cyberdBot [t.me/cyberdbot](https://t.me/cyberdbot)  
Telegram bot for creation cyberLinks on the cyberd knoledge graph, upload content to IPFS and monitoring [cyberd](https://github.com/cybercongress/cyberd/) node status data
## Install
- Install [IPFS node](https://docs-beta.ipfs.io/install/command-line-quick-start/)  
- Install [cyberd node](https://cybercongress.ai/docs/cyberd/run_validator/)  
- Clone repository:
```bash 
git clone https://github.com/Snedashkovsky/cyberdBot
```
- Install requirements 
```bash
make install_venv
sudo apt-get install expect
```
- Add your Telegram Bot Token, cyberd key name and cyberd passphrase into `.env`
## Run
### Main Bot
```bash  
# Development Mode
make start_dev_mode_main
# Production mode
make start_main
```
### Monitoring Scheduler
```bash
# Development Mode
make start_dev_mode_scheduler
# Production mode
make start_scheduler
```
## Test
```
make test
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
Python 3.9 or higher

## Data for the Bostrom Genesis 
[Bot user addresses with the number of created cyberlinks](https://ipfs.io/ipfs/QmWLoxH5F1tFvoiMEq8JEGjHsrT7JSkRxzhUGV1Lrn1GWk) as of 10/08/2021.
