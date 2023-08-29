# Binance Position Checker

## Overview

This project aims to periodically monitor open positions in a Binance account and ensure that transactions are not falling below their specified stop-loss values. If a transaction is detected below its stop-loss, the position is automatically closed to prevent further losses.

## Structure

The project is structured into several key components:

- **main.py**: This is the main entry point of the application. It initializes the necessary utilities, fetches open positions, and checks them against their stop-loss values.
- **.env**: Contains environment variables that are crucial for the application, such as database connection details and Binance API keys. (Note: This file should be kept private and not committed to public repositories.)
- **requirements.txt**: Lists all the Python packages required to run the application.
- **my_app.log**: This is where the application logs are stored, providing insights into the operations and any potential issues.

### Directories:

- **db**:
  - **mongo_utils.py**: Contains utility functions to interact with the MongoDB database, fetch transactions, and retrieve operation values for orders.

- **trading**:
  - **binance_utils.py**: Provides utility functions to interact with the Binance API. It can fetch current prices, retrieve open positions, and close positions when necessary.

- **utils**:
  - **email_module.py**: (Assuming based on the name) Contains functions to send emails, possibly for notifications or alerts.
  - **logger_module.py**: Sets up the logging configuration for the application, ensuring that operations are logged both to the console and to a file.
  - **position_utils.py**: (Assuming based on the name) Contains utility functions related to position management or calculations.

## How to Run

1. Ensure you have Python installed.
2. Clone the repository.
3. Navigate to the project directory.
4. Install the required packages with `pip install -r requirements.txt`.
5. Update the `.env` file with your MongoDB and Binance credentials.
6. Run the application with `python main.py`.

## Note

Remember to keep your `.env` file secure and not expose sensitive information like API keys or database credentials.
