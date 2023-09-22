from binance.client import Client
from datetime import datetime, timezone
import time
from bson import ObjectId
from utils.logger_module import setup_logger

logger = setup_logger(__name__, 'my_app.log')


class BinanceUtils:
    def __init__(self, api_key, api_secret, mongo):
        self.mongo = mongo
        self.client = Client(api_key=api_key, api_secret=api_secret)
        self.positions_cache = None
        self.positions_dict = {}
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
        position = next((item for item in self.client.futures_account()['positions'] if item["symbol"] == symbol and float(item['positionAmt']) != 0), None)
        return position

    def close_short_position(self, transaction_id, symbol, quantity, account_number, last_transaction_number, position_status):
        """
        Close a short position by buying.
        """
        position = self.get_position_for_symbol(symbol)
        flag_closing = self.mongo.get_transaction_state(transaction_id)
        logger.info(f"Trying to close, position: {position}, closing: {flag_closing}")
        if position and not flag_closing:
            logger.info(f'Closing: {account_number}_{symbol}_{last_transaction_number}_{position_status}_safety')
            self.client.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=quantity,
                                         newClientOrderId=f'{account_number}_{symbol}_{last_transaction_number}_{position_status}_safety')
            time.sleep(1)
        else:
            logger.info(f"No short position for {symbol}. No action taken.")

    def close_long_position(self, transaction_id, symbol, quantity, account_number, last_transaction_number, position_status):
        """
        Close a long position by selling.
        """
        position = self.get_position_for_symbol(symbol)
        flag_closing = self.mongo.get_transaction_state(transaction_id)
        logger.info(f"Trying to close, position: {position}, closing: {flag_closing}")
        if position and not flag_closing:
            logger.info(f'Closing: {account_number}_{symbol}_{last_transaction_number}_{position_status}_safety')
            self.client.futures_create_order(symbol=symbol, side='SELL', type='MARKET', quantity=quantity,
                                         newClientOrderId=f'{account_number}_{symbol}_{last_transaction_number}_{position_status}_safety')
            time.sleep(1)
        else:
            logger.info(f"No long position for {symbol}. No action taken")

    def get_all_open_positions(self, force_update=False):
        """
        Fetch all open positions. Use cached data if available and not stale.
        """
        now = datetime.now(timezone.utc)
        cache_duration = now - self.last_cache_update

        if not self.positions_cache or cache_duration.total_seconds() > 60 or force_update:
            logger.info("Start refreshing cache...")

            positions = self.client.futures_account()['positions']
            fresh_positions_cache = [position for position in positions if float(position['positionAmt']) != 0]
            cache_before_copy = self.positions_cache

            # Use a dictionary for easier checking and updates
            cache_dict = {pos['order_id']: pos for pos in self.positions_cache} if self.positions_cache else {}

            new_cache_dict = {}

            for position in fresh_positions_cache:
                transaction = self.mongo.get_most_recent_transaction_for_symbol(position['symbol'],
                                                                                ObjectId('64d623cafa0a150e2234a500'))
                position['order_id'] = transaction['order_id']

                # Check if 'order_id' already exists in the cache
                if position['order_id'] not in cache_dict:
                    position['transaction_id'] = transaction['_id']
                    position['orderParams'] = self.mongo.get_order_for_transaction(transaction['order_id'])
                    position['accountNumber'], position[
                        'lastTransactionNumber'] = self.mongo.get_account_and_transaction_number(
                        transaction['account_id'])
                    position['status'] = 'OPEN'
                    logger.info(f"Adding new {position['symbol']} position to cache: {position}")

                    # Add to the dictionary
                    cache_dict[position['order_id']] = position
                else:
                    position = cache_dict[position['order_id']]
                    if position['status'] in ['C_SL', 'C_13', 'C_23', 'C_TP3']:
                        logger.info(f"Cache ignoring the following {position['symbol']} position: {position}, status: {position['status']}")
                        continue

                new_cache_dict[position['order_id']] = position

            # Convert back to list format for consistency
            self.positions_cache = list(new_cache_dict.values())
            self.last_cache_update = now

            if(force_update):
                logger.info(f"Forced refresh cache, positions fetched: {fresh_positions_cache}, cache before: {cache_before_copy}, cache after: {self.positions_cache}")
            else:
                logger.info(f"Refresh cache, positions fetched: {fresh_positions_cache}, cache before: {cache_before_copy}, cache after: {self.positions_cache}")

            # If there are no open positions, wait for 2 seconds
            if not self.positions_cache:
                time.sleep(2)

        return self.positions_cache

# Usage example:
# binance = BinanceUtils(BINANCE_API_KEY, BINANCE_API_SECRET)
# current_price = binance.get_current_price('BTCUSDT')
# print(current_price)
