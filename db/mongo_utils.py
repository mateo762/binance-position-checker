from pymongo import MongoClient
from bson.objectid import ObjectId


class MongoUtils:
    def __init__(self, uri, database_name):
        self.client = MongoClient(uri)
        self.db = self.client[database_name]
        self.transactions_collection = self.db['transactions']
        self.orders_collection = self.db['orders']
        self.accounts_collection = self.db['accounts']

    def get_recent_transactions(self, account_id, transaction_state='OPEN'):
        """
        Fetch the most recent transactions for a specified account_id and transactionState.
        """
        return self.transactions_collection.find({
            'account_id': ObjectId(account_id),
            'transactionState': transaction_state
        }).sort('transactionDate', -1)

    def get_order_by_id(self, order_id):
        """
        Fetch an order by its ID.
        """
        return self.orders_collection.find_one({'_id': order_id})

    def get_stop_loss_for_order(self, order_id):
        """
        Extract the stopLoss from an order using its ID.
        """
        order = self.get_order_by_id(order_id)
        return order['params']['stopLoss']

    def get_operation_value_for_order(self, order_id, field_name):
        """
        Fetch the value of the specified field from the operation collection for a given order_id.
        """
        order = self.orders_collection.find_one({'_id': order_id})
        return order['params'].get(field_name)

    def get_account_and_transaction_number(self, account_id):
        account = self.accounts_collection.find_one({'_id': account_id})
        return account['accountNumber'], account['lastTransactionNumber']

    def get_most_recent_transaction_for_symbol(self, symbol, account_id):
        """
        Fetch the most recent transaction for a given symbol and account_id.
        """
        transaction = self.transactions_collection.find({
            'symbol': symbol,
            'account_id': account_id
        }).sort('transactionDate', -1).limit(1)

        return transaction[0] if transaction else None

    def get_order_for_transaction(self, order_id):
        order = self.orders_collection.find_one({'_id': order_id})
        return order['params']

# Usage example:
# mongo = MongoUtils(MONGODB_URI, MONGODB_DATABASE)
# recent_transactions = mongo.get_recent_transactions('64d623cafa0a150e2234a500')
# for transaction in recent_transactions:
#     stop_loss = mongo.get_stop_loss_for_order(transaction['order_id'])
#     print(stop_loss)
