import yfinance as yf
import logging

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
            info = ticker.info
            history = ticker.history(period='1y')  # 1 year of historical data
            
            # Example fields
            market_cap = info.get('marketCap', 'N/A')
            forward_pe = info.get('forwardPE', 'N/A')
            book_value = info.get('bookValue', 'N/A')
            current_price = info.get('currentPrice', 'N/A')
            
            # Log the data fetched
            logging.debug(f"{ticker_symbol} - Market Cap: {market_cap}, Forward PE: {forward_pe}, "
                          f"Book Value: {book_value}, Current Price: {current_price}")
            
            # Store results
            stock_data[ticker_symbol] = {
                'market_cap': market_cap,
                'forward_pe': forward_pe,
                'book_value': book_value,
                'current_price': current_price,
                'price_history': history.to_dict() if not history.empty else "No Data"
            }
        except Exception as e:
            logging.error(f"Error fetching data for {ticker_symbol}: {e}")
            stock_data[ticker_symbol] = {'error': str(e)}
    return stock_data

# List of tickers to fetch
tickers_to_test = ['NVDA', 'AAPL', 'TSLA', 'MSFT', 'GOOGL']  # Add more tickers if needed

# Fetch data
stock_results = fetch_stock_data(tickers_to_test)

# Print the fetched data
for ticker, data in stock_results.items():
    print(f"\n{ticker} Data:")
    for key, value in data.items():
        print(f"  {key}: {value}")
