import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
