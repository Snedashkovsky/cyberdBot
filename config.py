import os
from enum import Enum
from telebot.types import ReplyKeyboardMarkup
from telebot import TeleBot
from dotenv import dotenv_values

from src.sql_utils import SQLighter

# Telegram bot token from BotFather
TELEBOT_TOKEN = dotenv_values('.env')['TELEBOT_TOKEN']
bot = TeleBot(TELEBOT_TOKEN)

# cyberdBot key name in the cyber
CYBER_KEY_NAME = dotenv_values('.env')['CYBER_KEY_NAME']

# cyber docker name and chain id
CYBER_DOCKER = dotenv_values('.env')['CYBER_DOCKER']
CYBER_CHAIN_ID = dotenv_values('.env')['CYBER_CHAIN_ID']

# Shell query for cyberLink creation
CYBERLINK_CREATION_QUERY = dotenv_values('.env')['CYBERLINK_CREATION_QUERY']

# Shell query for account creation
ACCOUNT_CREATION_QUERY = dotenv_values('.env')['ACCOUNT_CREATION_QUERY']

# Shell query for transfer main tokens to new account
TRANSFER_QUERY = dotenv_values('.env')['TRANSFER_QUERY']

# Shell query for delegate main tokens to validator
DELEGATE_QUERY = dotenv_values('.env')['DELEGATE_QUERY']
VALIDATOR_ADDRESS = dotenv_values('.env')['VALIDATOR_ADDRESS']

# Shell query for investmint stake tokens for amper or volt
INVESTMINT_QUERY = dotenv_values('.env')['INVESTMINT_QUERY']

# Shell query for unjail validator
UNJAIL_VALIDATOR_QUERY = dotenv_values('.env')['UNJAIL_VALIDATOR_QUERY']

# IPFS HOST
IPFS_HOST = dotenv_values('.env')['IPFS_HOST']

# Development mode for easy bot stop (set in start_bot.sh)
DEV_MODE = int(os.getenv('DEV_MODE', 0))

# SQLite file name and DB worker
DB_FILE = 'db_sqlite.vdb'
db_worker = SQLighter(DB_FILE)

# Cyber.page address for generate links to accounts and transactions
CYBERPAGE_URL = 'https://rebyc.cyber.page/network/bostrom'

# GraphQL host
GRAPHQL_HOST = 'https://index.bostromdev.cybernode.ai/v1/graphql'

# RPC host
RPC_HOST = 'https://rpc.bostromdev.cybernode.ai'

# LCD host
LCD_HOST = 'https://lcd.bostromdev.cybernode.ai'

# Hourly notifications
SCHEDULER_TIME = 60 * 60

TOKEN_NAME = 'BOOT'

# List of commands
COMMAND_LIST = ['cyberlink', 'ipfs', 'tweet', 'check', 'validators']

# Base Menu
BASE_MENU = ['Create cyberLink', 'Upload to IPFS', 'Sign up',
             'Jail check', 'Validator list', 'Jail check settings']
BASE_KEYBOARD = ReplyKeyboardMarkup(True, True)
BASE_KEYBOARD.add(BASE_MENU[0], BASE_MENU[1], BASE_MENU[2])
BASE_KEYBOARD.add(BASE_MENU[3], BASE_MENU[4], BASE_MENU[5])

# BASE Menu after Sign up
BASE_AFTER_SIGN_UP_MENU = ['Create cyberLink', 'Upload to IPFS', 'Tweet',
                           'Jail check', 'Validator list', 'Jail check settings']
BASE_AFTER_SIGN_UP_KEYBOARD = ReplyKeyboardMarkup(True, True)
BASE_AFTER_SIGN_UP_KEYBOARD.add(BASE_AFTER_SIGN_UP_MENU[0], BASE_AFTER_SIGN_UP_MENU[1], BASE_AFTER_SIGN_UP_MENU[2])
BASE_AFTER_SIGN_UP_KEYBOARD.add(BASE_AFTER_SIGN_UP_MENU[3], BASE_AFTER_SIGN_UP_MENU[4], BASE_AFTER_SIGN_UP_MENU[5])

BASE_MENU_LOWER = set(map(str.lower, BASE_MENU + BASE_AFTER_SIGN_UP_MENU + ['/' + item for item in COMMAND_LIST]))

# Jail Monitoring Menu
MONITORING_MENU = ['Add validator moniker', 'Reset validator moniker',
                   'Jail check', 'Hourly check', 'Validator list',
                   'Back to Main']
MONITORING_MENU_LOWER = list(map(str.lower, MONITORING_MENU))
MONITORING_KEYBOARD = ReplyKeyboardMarkup(True, True)
MONITORING_KEYBOARD.add(MONITORING_MENU[0], MONITORING_MENU[1])
MONITORING_KEYBOARD.add(MONITORING_MENU[2], MONITORING_MENU[3], MONITORING_MENU[4])
MONITORING_KEYBOARD.add(MONITORING_MENU[5])

# Tweet Menu
TWEETER_MENU = ['New Tweet', 'Back to Main']
TWEETER_MENU_LOWER = list(map(str.lower, TWEETER_MENU))
TWEETER_KEYBOARD = ReplyKeyboardMarkup(True, True)
TWEETER_KEYBOARD.add(TWEETER_MENU[0], TWEETER_MENU[1])

TWEET_HASH = 'QmbdH2WBamyKLPE5zu4mJ9v49qvY8BFfoumoVPMR5V4Rvx'


# default status class
class States(Enum):
    S_START = 0  # Start a position
    S_UPLOAD_IPFS = 1  # Upload a content to IPFS
    S_STARTPOINT_CYBERLINK = 2  # Set a starting point of cyberlink
    S_ENDPOINT_CYBERLINK = 3  # Set a endpoint of cyberlink
    S_MONITORING = 4  # Jail checker
    S_SIGNUP = 5  # Sign up a new cyberd account
    S_NEW_TWEET = 6  # Upload a New Tweet
