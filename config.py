import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

MY_WALLET = os.getenv('MY_WALLET')
MY_WALLET_PRIVATE_KEY = os.getenv('MY_WALLET_PRIVATE_KEY')

TETHER_API_KEY = os.getenv('TETHER_API_KEY')
TETHER_API_SECRET = os.getenv('TETHER_API_SECRET')

TRONSCAN_API_KEY = os.getenv('TRONSCAN_API_KEY')
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')
