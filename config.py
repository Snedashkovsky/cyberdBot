import os
from enum import Enum
from telebot.types import ReplyKeyboardMarkup
from telebot import TeleBot

from src.sql_utils import SQLighter

# Telegram bot token from BotFather
TELEBOT_TOKEN = os.getenv('TELEBOT_TOKEN')

# Shell query for get validators state data
VALIDATOR_QUERY = os.getenv('VALIDATOR_QUERY', 'cyberdcli query staking validators --trust-node=true')

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

# BASE MENU
BASE_MENU = ['Add validator moniker', 'Reset validator moniker',
             'Jail check',            'Hourly check',
             'Validator list',        'Upload to IPFS']
BASE_MENU_LOWER = list(map(str.lower, BASE_MENU))
BASE_KEYBOARD = ReplyKeyboardMarkup(True, True)
BASE_KEYBOARD.add(BASE_MENU[0], BASE_MENU[1])
BASE_KEYBOARD.add(BASE_MENU[2], BASE_MENU[3], BASE_MENU[4])
BASE_KEYBOARD.add(BASE_MENU[5])


# default status class
class States(Enum):

    S_START = 0  # Start position
    S_UPLOAD_IPFS = 1
