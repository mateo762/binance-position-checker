from db.mongo_utils import MongoUtils
from trading.binance_utils import BinanceUtils
from utils.logger_module import setup_logger
from utils.position_utils import check_and_close_position
import websocket
import json
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

# Global dictionary to store the latest price for each symbol
current_prices = {}

def on_message(ws, message):
    data = json.loads(message)
    symbol = data['s']
    price = float(data['p'])
    current_prices[symbol] = price

def start_websockets(symbols):
    for symbol in symbols:
        ws_url = f"wss://fstream.binance.com/ws/{symbol}@trade"
        ws = websocket.WebSocketApp(ws_url, on_message=on_message)
        # Run the WebSocket in a separate thread so it doesn't block the main loop
        websocket.Thread(target=ws.run_forever).start()


# Get all symbols you're interested in
tracked_symbols = ['BTCUSDT', 'LTCUSDT', 'ETHUSDT', 'DOTUSDT']
start_websockets(tracked_symbols)


while True:
    logger.info("Starting a new iteration...")
    open_positions = binance.get_all_open_positions()

    for position in open_positions:
        try:
            symbol = position['symbol']
            websocket_current_price_symbol = current_prices.get(symbol, "NaN")
            check_and_close_position(position, websocket_current_price_symbol, mongo, binance)
        except Exception as e:
            logger.error(f"Error while checking and closing position: {e}")

    time.sleep(0.2)  # Wait
