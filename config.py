import os
from enum import Enum
from telebot.types import ReplyKeyboardMarkup
from telebot import TeleBot

from src.sql_utils import SQLighter

# Telegram bot token from BotFather
TELEBOT_TOKEN = os.getenv('TELEBOT_TOKEN')

# cyberdBot key name in the cyberd
CYBERD_KEY_NAME = os.getenv('CYBERD_KEY_NAME')

# Shell query for get validators state data
VALIDATOR_QUERY = os.getenv('VALIDATOR_QUERY', 'cyberdcli query staking validators --trust-node=true')

# Shell query for cyberLink creation
CYBERLINK_CREATION_QUERY = os.getenv('CYBERLINK_CREATION_QUERY', './src/create_cyberlink.sh')

# Shell query for account creation
ACCOUNT_CREATION_QUERY = os.getenv('ACCOUNT_CREATION_QUERY', './src/create_account.sh')

# Shell query for transfer main tokens to new account
TRANSFER_QUERY = os.getenv('TRANSFER_QUERY', './src/transfer_tokens.sh')

# Shell query for unjail validator
UNJAIL_VALIDATOR_QUERY = os.getenv('UNJAIL_VALIDATOR_QUERY', './src/unjail_validator.sh')

# Development mode for easy bot stop
DEV_MODE = int(os.getenv('DEV_MODE', 0))

# SQLLite file name
DB_FILE = os.getenv('DB_FILE', 'db_sqlite.vdb')

# IPFS HOST
IPFS_HOST = os.getenv('IPFS_HOST', 'http://localhost:5001')

CYBERPAGE_URL = 'https://rebyc.cyber.page/network/bostrom'

GRAPHQL_HOST = 'https://index.bostromdev.cybernode.ai/v1/graphql'

bot = TeleBot(TELEBOT_TOKEN)

db_worker = SQLighter(DB_FILE)

# Hourly notifications
SCHEDULER_TIME = 60 * 60

TOKEN_NAME = 'BOOT'

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

BASE_MENU_LOWER = set(map(str.lower, BASE_MENU + BASE_AFTER_SIGN_UP_MENU))

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
