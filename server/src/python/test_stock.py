import yfinance as yf
import logging

import get_edgar

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_stock_data(tickers):
    """
    Fetch stock data for a list of tickers, with logging and error handling.
    """
    stock_data = {}
    for ticker_symbol in tickers:
        logging.info(f"Fetching data for {ticker_symbol}...")
        try:
            # Download ticker data
            ticker = yf.Ticker(ticker_symbol)
            
            # Fetch basic data
            # info = ticker.info
            # history = ticker.history(period='1y')  # 1 year of historical data
            
            # Example fields
            # market_cap = info.get('marketCap', 'N/A')
            # forward_pe = info.get('forwardPE', 'N/A')
            # book_value = info.get('bookValue', 'N/A')
            # current_price = info.get('currentPrice', 'N/A')
            

            # Log the data fetched
            # logging.debug(f"{ticker_symbol} - Market Cap: {market_cap}, Forward PE: {forward_pe}, "
            #               f"Book Value: {book_value}, Current Price: {current_price}")
            # stock_data[ticker_symbol] = {
            #     'market_cap': market_cap,
            #     'forward_pe': forward_pe,
            #     'book_value': book_value,
            #     'current_price': current_price,
            #     'price_history': history.to_dict() if not history.empty else "No Data"
            # }
            year = 1
            # liquidity, profit, market, cyclical = stock_data.fetch_stock_data(ticker.ticker, year)
            # df = annual_facts("TEM", headers=headers)  # Call the function to get the DataFrame
            # save_dataframe_to_csv(df, "csv", "TEM", "10-k", "1-year")  # Pass the DataFrame
            Operating_cycle = get_edgar.save_df_call_method(ticker.ticker, get_edgar.operating_cycle, year) 
            logging.debug("Operating cycle, %s", Operating_cycle)

            # Store results
            stock_data[ticker_symbol] = {
            "Operating Cycle data":  Operating_cycle,
            }
        except Exception as e:
            logging.error(f"Error fetching data for {ticker_symbol}: {e}")
            stock_data[ticker_symbol] = {'error': str(e)}
    return stock_data

# List of tickers to fetch
tickers_to_test = ['TSLA', 'GOOGL','X']  # Add more tickers if needed

# Fetch data
stock_results = fetch_stock_data(tickers_to_test)

# Print the fetched data
for ticker, data in stock_results.items():
    print(f"\n{ticker} Data:")
    for key, value in data.items():
        print(f"  {key}: {value}")


#. .venv/bin/activate && python3 src/python/test_stock.py