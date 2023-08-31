from binance.client import Client
from datetime import datetime, timezone


class BinanceUtils:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key=api_key, api_secret=api_secret)

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

        self.client.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=quantity, newClientOrderId=f'{account_number}_{symbol}_{last_transaction_number}_safety')

    def close_long_position(self, symbol, quantity, account_number, last_transaction_number):
        """
        Close a long position by selling.
        """
        self.client.futures_create_order(symbol=symbol, side='SELL', type='MARKET', quantity=quantity, newClientOrderId=f'{account_number}_{symbol}_{last_transaction_number}_safety')

    def get_all_open_positions(self):
        """
        Fetch all open positions.
        """
        positions = self.client.futures_account()['positions']
        open_positions = [position for position in positions if float(position['positionAmt']) != 0]
        return open_positions

    def get_open_position_time(self, symbol, position_amount):
        """
        Fetch the time at which a position was opened for a given symbol.
        """
        trades = self.client.futures_account_trades(symbol=symbol)
        for trade in trades:
            if position_amount > 0 and trade['buyer'] == True:
                timestamp = int(trade['time']) / 1000  # Convert to seconds
                dt_object = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                return dt_object.isoformat()
            elif position_amount < 0 and trade['buyer'] == False:
                timestamp = int(trade['time']) / 1000  # Convert to seconds
                dt_object = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                return dt_object.isoformat()
        return None

# Usage example:
# binance = BinanceUtils(BINANCE_API_KEY, BINANCE_API_SECRET)
# current_price = binance.get_current_price('BTCUSDT')
# print(current_price)
