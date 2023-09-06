from db.mongo_utils import MongoUtils
from trading.binance_utils import BinanceUtils
from utils.logger_module import setup_logger
from utils.position_utils import check_and_close_position
import os
import time
from dotenv import load_dotenv


logger = setup_logger(__name__, 'my_app.log')

# Load the .env file
load_dotenv()

# Access the variables
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

# Initialize MongoDB and Binance utilities
mongo = MongoUtils(MONGODB_URI, MONGODB_DATABASE)
binance = BinanceUtils(BINANCE_API_KEY, BINANCE_API_SECRET, mongo)

while True:
    logger.info("Starting a new iteration...")
    open_positions = binance.get_all_open_positions()

    for position in open_positions:
        try:
            check_and_close_position(position, mongo, binance)
        except Exception as e:
            logger.error(f"Error while checking and closing position: {e}")

    time.sleep(0.2)  # Wait
