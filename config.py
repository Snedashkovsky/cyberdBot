from enum import Enum
from telebot.types import ReplyKeyboardMarkup
from telebot import TeleBot
from dotenv import dotenv_values
import logging
from sys import stdout

from src.sql_utils import SQLighter

# Telegram bot token from BotFather
TELEBOT_TOKEN = dotenv_values('.env')['TELEBOT_TOKEN']
bot = TeleBot(TELEBOT_TOKEN)

SUPPORT_ACCOUNT = dotenv_values('.env')['SUPPORT_ACCOUNT']

# Set logging format
LOG_FILE = 'cyberdbot.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(stdout)
    ]
)

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

# Shell query for IPFS node restart
IPFS_RESTART_QUERY = dotenv_values('.env')['IPFS_RESTART_QUERY']

# IPFS HOST
IPFS_HOST = dotenv_values('.env')['IPFS_HOST']

# SQLite file name and DB worker
DB_FILE = 'db_sqlite.vdb'
db_worker = SQLighter(DB_FILE)

# Cyber page address for generate links to accounts and transactions
CYBERPAGE_URL = 'https://cyb.ai/network/bostrom'
CYBERPAGE_BASE_URL = 'https://cyb.ai'

# GraphQL host
GRAPHQL_HOST = 'https://index.bostrom.cybernode.ai/v1/graphql'

# RPC host
RPC_HOST = 'https://rpc.bostrom.cybernode.ai'

# LCD host
LCD_HOST = 'https://lcd.bostrom.cybernode.ai'

# Hourly notifications
SCHEDULER_TIME = 60 * 60

TOKEN_NAME = 'BOOT'

# List of commands
COMMAND_LIST = ['search', 'cyberlink', 'ipfs', 'tweet', 'check', 'validators', 'issue']

# Base Menu
BASE_MENU = ['Search', 'Create cyberLink', 'Upload to IPFS', 'Sign up',
             'Jail check', 'Validator list', 'Jail check settings']
BASE_KEYBOARD = ReplyKeyboardMarkup(True, True)
BASE_KEYBOARD.add(BASE_MENU[0])
BASE_KEYBOARD.add(BASE_MENU[1], BASE_MENU[2], BASE_MENU[3])
BASE_KEYBOARD.add(BASE_MENU[4], BASE_MENU[5], BASE_MENU[6])

# BASE Menu after Sign up
BASE_AFTER_SIGN_UP_MENU = ['Search', 'Create cyberLink', 'Upload to IPFS', 'Tweet',
                           'Jail check', 'Validator list', 'Jail check settings']
BASE_AFTER_SIGN_UP_KEYBOARD = ReplyKeyboardMarkup(True, True)
BASE_AFTER_SIGN_UP_KEYBOARD.add(BASE_AFTER_SIGN_UP_MENU[0])
BASE_AFTER_SIGN_UP_KEYBOARD.add(BASE_AFTER_SIGN_UP_MENU[1], BASE_AFTER_SIGN_UP_MENU[2], BASE_AFTER_SIGN_UP_MENU[3])
BASE_AFTER_SIGN_UP_KEYBOARD.add(BASE_AFTER_SIGN_UP_MENU[4], BASE_AFTER_SIGN_UP_MENU[5], BASE_AFTER_SIGN_UP_MENU[6])

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
AVATAR_HASH = 'Qmf89bXkJH9jw4uaLkHmZkxQ51qGKfUPtAMxA8rTwBrmTs'
FOLLOW_HASH = 'QmPLSA5oPqYxgc8F7EwrM8WS9vKrr1zPoDniSRFh8HSrxx'


# default status class
class States(Enum):
    S_START = 0  # Start a position
    S_SEARCH = 1  # Search a content
    S_UPLOAD_IPFS = 2  # Upload a content to IPFS
    S_STARTPOINT_CYBERLINK = 3  # Set a starting point of cyberlink
    S_ENDPOINT_CYBERLINK = 4  # Set a endpoint of cyberlink
    S_MONITORING = 5  # Jail checker
    S_SIGNUP = 6  # Sign up a new cyberd account
    S_NEW_TWEET = 7  # Upload a New Tweet
