from bson.objectid import ObjectId
from utils.email_module import send_email
from utils.logger_module import setup_logger
import time

logger = setup_logger(__name__, 'my_app.log')

LIFE_CYCLE_MAP = {
    'PENDING': 'continue',
    'OPEN': 'stopLoss',
    'BREAK_EVEN': 'point13',
    'CANCELED': 'continue',
    'STOP_LOSS': 'stopLoss',
    'FIRST_MOVE': 'point13',
    'SECOND_MOVE': 'point23',
    'TAKE_PROFIT_2': 'point23',
    'TAKE_PROFIT_3': 'point23',
    'MANUALLY_CLOSED': 'continue',
    'BREAK_EVEN_PLUS': 'point23'
}


def check_and_close_position(position, mongo, binance):
    symbol = position['symbol']
    position_amount = float(position['positionAmt'])

    if position_amount == 0:
        return

    # Fetch the most recent transaction for this asset
    transaction = mongo.get_most_recent_transaction_for_symbol(symbol, ObjectId('64d623cafa0a150e2234a500'))
    life_cycle_last_value = transaction['lifeCycle'][-1] if transaction['lifeCycle'] else None
    operation_field = LIFE_CYCLE_MAP.get(life_cycle_last_value, 'continue')

    if operation_field == 'continue':
        return

    threshold_value = mongo.get_operation_value_for_order(transaction['order_id'], operation_field)
    take_profit_3_value = mongo.get_operation_value_for_order(transaction['order_id'], 'takeProfit3')  # Fetching the take_profit_3_value
    current_price = binance.get_current_price(symbol)

    # Determine position type
    position_type = "Short" if position_amount < 0 else "Long"

    # Logic to determine if position should be closed
    if position_type == "Long":
        would_close = current_price <= threshold_value or current_price >= take_profit_3_value
    else:  # Short position
        would_close = current_price >= threshold_value or current_price <= take_profit_3_value

    close_status = "Would Close" if would_close else "Would Not Close"

    info_account = mongo.get_account_and_transaction_number(transaction['account_id'])
    account_number = info_account[0]
    last_transaction_number = info_account[1]

    # Log the details
    logger.info(
        f"Symbol: {symbol}, Current Price: {current_price}, Last Update: {life_cycle_last_value}, {operation_field}: {threshold_value}, TP3: {take_profit_3_value}, Position Type: {position_type}, Status: {close_status}, Account Number: {account_number}, Last Transaction: {last_transaction_number}")

    if would_close:
        # Send email notification
        email_subject = f"Position Alert for {symbol}"
        email_body = f"Symbol: {symbol}, Current Price: {current_price}, Last Update: {life_cycle_last_value}, {operation_field}: {threshold_value}, TP3: {take_profit_3_value}, Position Type: {position_type}, Status: {close_status}"
        send_email(email_subject, email_body)
        if position_type == "Short":
            quantity_to_buy = abs(position_amount)
            logger.info(f"Closing short position by buying {quantity_to_buy} {symbol}")
            time.sleep(1)
            binance.close_short_position(symbol, quantity_to_buy, account_number, last_transaction_number+1)
        else:  # Long position
            logger.info(f"Closing long position by selling {position_amount} {symbol}")
            time.sleep(1)
            binance.close_long_position(symbol, position_amount, account_number, last_transaction_number+1)
