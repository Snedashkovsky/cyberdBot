import os
from enum import Enum
from telebot.types import ReplyKeyboardMarkup
from telebot import TeleBot

from src.sql_utils import SQLighter

# Telegram bot token from BotFather
TELEBOT_TOKEN = os.getenv('TELEBOT_TOKEN')

# Shell query for get validators state data
VALIDATOR_QUERY = os.getenv('VALIDATOR_QUERY', 'cyberdcli query staking validators --trust-node=true')

# Shell query for cyberLink creation
CYBERLINK_CREATION_QUERY = os.getenv('CYBERLINK_CREATION_QUERY', './src/create_cyberlink.sh')

# Shell query for account creation
ACCOUNT_CREATION_QUERY = os.getenv('ACCOUNT_CREATION_QUERY', './src/create_account.sh')

# Shell query for transfer EUL tokens to new account
TRANSFER_EUL_QUERY = os.getenv('TRANSFER_EUL_QUERY', './src/transfer_eul_tokens.sh')

# Development mode for easy bot stop
DEV_MODE = int(os.getenv('DEV_MODE', 0))

# SQLLite file name
DB_FILE = os.getenv('DB_FILE', 'db_sqlite.vdb')

# IPFS HOST
IPFS_HOST = os.getenv('IPFS_HOST', 'http://localhost:5001')

bot = TeleBot(TELEBOT_TOKEN)

db_worker = SQLighter(DB_FILE)

# Hourly notifications
SCHEDULER_TIME = 60 * 60

# Base Menu
BASE_MENU = ['Create cyberLink', 'Upload to IPFS', 'Sign up',
             'Jail check', 'Validator list', 'Jail check settings'
             ]
BASE_MENU_LOWER = list(map(str.lower, BASE_MENU))
BASE_KEYBOARD = ReplyKeyboardMarkup(True, True)
BASE_KEYBOARD.add(BASE_MENU[0], BASE_MENU[1], BASE_MENU[2])
BASE_KEYBOARD.add(BASE_MENU[3], BASE_MENU[4], BASE_MENU[5])

# Jail Monitoring Menu
MONITORING_MENU = ['Add validator moniker', 'Reset validator moniker',
                   'Jail check', 'Hourly check', 'Validator list',
                   'Back to Main']
MONITORING_MENU_LOWER = list(map(str.lower, MONITORING_MENU))
MONITORING_KEYBOARD = ReplyKeyboardMarkup(True, True)
MONITORING_KEYBOARD.add(MONITORING_MENU[0], MONITORING_MENU[1])
MONITORING_KEYBOARD.add(MONITORING_MENU[2], MONITORING_MENU[3], MONITORING_MENU[4])
MONITORING_KEYBOARD.add(MONITORING_MENU[5])


# default status class
class States(Enum):
    S_START = 0  # Start position
    S_UPLOAD_IPFS = 1  # Upload content to IPFS
    S_STARTPOINT_CYBERLINK = 2  # Set starting point of cyberlink
    S_ENDPOINT_CYBERLINK = 3  # Set endpoint of cyberlink
    S_MONITORING = 4  # Jail checker
    S_SIGNUP = 5  # Sign up new cyberd account
