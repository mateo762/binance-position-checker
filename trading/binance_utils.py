from binance.client import Client
from datetime import datetime, timezone
import time
from bson import ObjectId


class BinanceUtils:
    def __init__(self, api_key, api_secret, mongo):
        self.mongo = mongo
        self.client = Client(api_key=api_key, api_secret=api_secret)
        self.positions_cache = None
        self.last_cache_update = datetime.min.replace(tzinfo=timezone.utc)

    def get_current_price(self, symbol):
        """
        Fetch the current price for a given symbol.
        """
        return float(self.client.futures_ticker(symbol=symbol)['lastPrice'])

    def get_position_for_symbol(self, symbol):
        """
        Fetch the position for a given symbol.
        """
        position = next((item for item in self.client.futures_account()['positions'] if item["symbol"] == symbol), None)
        return position

    def close_short_position(self, symbol, quantity, account_number, last_transaction_number):
        """
        Close a short position by buying.
        """

        self.client.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=quantity,
                                         newClientOrderId=f'{account_number}_{symbol}_{last_transaction_number}_safety')

    def close_long_position(self, symbol, quantity, account_number, last_transaction_number):
        """
        Close a long position by selling.
        """

        self.client.futures_create_order(symbol=symbol, side='SELL', type='MARKET', quantity=quantity,
                                         newClientOrderId=f'{account_number}_{symbol}_{last_transaction_number}_safety')

    def get_all_open_positions(self, force_update=False):
        """
        Fetch all open positions. Use cached data if available and not stale.
        """
        now = datetime.now(timezone.utc)
        cache_duration = now - self.last_cache_update

        if not self.positions_cache or cache_duration.total_seconds() > 5 or force_update:
            positions = self.client.futures_account()['positions']
            self.positions_cache = [position for position in positions if float(position['positionAmt']) != 0]
            self.last_cache_update = now
            for position in self.positions_cache:
                transaction = self.mongo.get_most_recent_transaction_for_symbol(position['symbol'], ObjectId('64d623cafa0a150e2234a500'))
                position['orderParams'] = self.mongo.get_order_for_transaction(transaction['order_id'])
            # If there are no open positions, wait for 2 seconds
            if not self.positions_cache:
                time.sleep(2)

        print(self.positions_cache)
        return self.positions_cache

# Usage example:
# binance = BinanceUtils(BINANCE_API_KEY, BINANCE_API_SECRET)
# current_price = binance.get_current_price('BTCUSDT')
# print(current_price)
