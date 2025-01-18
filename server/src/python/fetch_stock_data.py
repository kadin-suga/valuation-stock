from flask import Flask, request, jsonify
import logging
logging.basicConfig(level=logging.DEBUG)
import pandas as pd
import yfinance as yf
from flask_cors import CORS
import get_edgar, gemini_api, get_valuation

# Instantiate the Flask app
app = Flask(__name__)
CORS(app)

def extract_number(period):
    """Extract a number from the period string."""
    number = ''.join(filter(str.isdigit, period))
    if not number:
        raise ValueError(f"No number found in the input period: {period}")
    return int(number)


def book_value(ticker):
    # Get the balance sheet data
    balance_sheet = ticker.balance_sheet

    # Extract total assets and total liabilities
    total_assets = balance_sheet.loc['Total Assets'][0]
    total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest'][0]

    # Get the number of outstanding shares
    shares_outstanding = ticker.info.get('sharesOutstanding')

    if total_assets and total_liabilities and shares_outstanding:
        # Calculate book value per share
        book_value = (total_assets - total_liabilities) / shares_outstanding
        return book_value
    else:
        print("Required data for Book Value per Share calculation is not available.")

    

def market_value_added(ticker):
    """Calculate Market Value Added."""
    try:
        market_cap_value = ticker.info.get('marketCap')
        book_value_of_equity = book_value(ticker) 
        return market_cap_value - book_value_of_equity if market_cap_value and book_value_of_equity else None
    except Exception as e:
        return {'error': str(e)}
    
    
def market_to_book(ticker):
    try:
        market_cap_value = ticker.info.get('marketCap')
        book_value_of_equity = book_value(ticker)
        if not isinstance(market_cap_value, (int, float)) or not isinstance(book_value_of_equity, (int, float)):
            raise ValueError("Market Cap or Book Value is not a number.")
        return market_cap_value / book_value_of_equity
    except Exception as e:
        return {'error': str(e)}




def fetch_stock_data(ticker, year):
    """Fetch various stock data points."""
    try:
        logging.debug("Enter fetched stock data")
        
        liquidity_data = {
            "Total debt data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.total_debt, year) or 'Total issue 1',
            "Debt ratio data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.debt_ratio, year) or 'Total issue 2',
            "Times interest earned data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.times_interest_earned, year)or 'Total issue 3',
            "Net working capital ratio data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.networking_capital_to_assets, year) or 'Total issue 4',
            "Current ratio data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.current_ratio, year) or 'Total issue 5',
            "Quick ratio data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.quick_ratio, year) or 'Total issue 6',
        }
        logging.debug("Liquidity stock data")

        profit_data = {
            "Profit Margin data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.profit_margin, year) or 'Total issue 7',
            "Growth Rate data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.growth_rate, year) or 'Total issue 8',
            "Return on Capital data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.return_on_capital, year) or 'Total issue 9',
            "Return on Equity data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.return_on_equity, year) or 'Total issue 10',
            "Return on Asset data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.return_on_asset, year) or 'Total issue 11',
        }
        logging.debug("Profit stock data")

        price = ticker.history(period='1d')

        # Check if price data exists and is non-empty
        if not price.empty:
            price_change = price['Close'].pct_change().dropna() * 100  # Avoid nulls
            price_change_list = price_change.tolist()  # Convert Series to a list
            price_value = price['Close'].iloc[0]  # Get the first close price
        else:
            price_change_list = []
            price_value = 0.0

        market_data = {
            "Price": price_value,
            "Price change": price_change_list,  # Use the converted list
            "Market Cap": ticker.info.get('marketCap', 0),
            "Market value added": market_value_added(ticker),
            "Market to book": market_to_book(ticker),
        }

        logging.debug("Market stock data")
        cyclical_data = {
            "Operating Cycle data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.operating_cycle, year) or 'Total issue 12',
            "Cash Cycle data": get_edgar.save_df_call_method(ticker.ticker, get_edgar.cash_cycle, year) or 'Total issue 13'
        }
        logging.debug("Cyclical stock data")

        return liquidity_data, profit_data, market_data, cyclical_data
    except Exception as e:
        return {'error': str(e)}



@app.route("/bulk_stock_data")
def get_stock_data():
    try:
        logging.debug("Fetching symbol from request args")
        symbol = request.args.get('symbol', default="AAPL")
        time_period = "1y"

        ticker = yf.Ticker(symbol)
        logging.debug("Ticker object created")
        hist = ticker.history(period=time_period)
        logging.debug("Historical data fetched")

        hist.fillna(0, inplace=True)
        hist_dict = hist.reset_index().to_dict(orient="records")

        period = 1
        logging.debug("Fetching stock data")
        liquidity_data, profit_data, market_data, cyclical_data = fetch_stock_data(ticker, period)
        logging.debug("Stock data fetched")
        
        # logging.debug("Symbol: %s", jsonify(symbol))
        # logging.debug("Information: %s", jsonify(get_edgar.get_description(ticker.ticker)))
        # logging.debug("Market data: %s", (market_data))
        # logging.debug("Profit data: %s", jsonify(profit_data))
        logging.debug("Profit data: %s", (cyclical_data))
        # logging.debug("Profit data: %s", jsonify(cyclical_data["Cash Cycle data"]))
        # logging.debug("Profit data: %s", jsonify(cyclical_data["Cash Cycle data"]["operating cycle"]))
        # logging.debug("Cyclical data: %s", jsonify(cyclical_data))
        # logging.debug("Cyclical data json: %s", jsonify(cyclical_data))
        # logging.debug("Liquidity data: %s", jsonify(liquidity_data))
        # logging.debug("History: %s", jsonify(hist_dict))

        data = {
            
            "Symbol": symbol,
            "Information": get_edgar.get_description(ticker.ticker),
            "Market data": market_data,
            "Profit data": profit_data,
            "Cyclical data": cyclical_data,
            "Liquidity data": liquidity_data,
            "History": hist_dict,
        }
        # logging.debug("Data: %s", (data))
        # logging.debug("Data json: %s", jsonify(data))
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error in get_stock_data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/cur_stock_price")
def get_stock_price():
    try:
        symbol = request.args.get('symbol', default="AAPL")
        ticker = yf.Ticker(symbol)
        
        price = ticker.history(period='1d')

            # Check if price data exists and is non-empty
        if not price.empty:
            price_change = price['Close'].pct_change().dropna() * 100  # Avoid nulls
            price_change_list = price_change.tolist()  # Convert Series to a list
            price_value = price['Close'].iloc[0]  # Get the first close price
        else:
            price_change_list = []
            price_value = 0.0
        
        price_data = {
            "Current price": price_value,
            "Price change": price_change_list
        }
        
        return jsonify(price_data)
    except  Exception as e:
        logging.error(f"Error in get_stock_data: {e}")
        return jsonify({"error": str(e)}), 500
    


@app.route("/stock_history")
def get_more_history():
    try:
        symbol = request.args.get('symbol', default="AAPL")
        time_period = request.args.get('timePeriod')

        ticker = yf.Ticker(symbol)
        logging.debug("Ticker object created")
        hist = ticker.history(period=time_period)
        logging.debug("Historical data fetched")

        hist.fillna(0, inplace=True)
        hist_dict = hist.reset_index().to_dict(orient="records")

        hist_data= {
            "History": hist_dict
        }

        return jsonify(hist_data)

    except Exception as e:
        logging.error(f"Error in get_stock_data: {e}")
        return jsonify({"error": str(e)}), 500



    
@app.route('/valuate')
def value_stock():
    try:
        symbol = request.args.get('symbol', default="AAPL")
        logging.debug("Ticker object created 1")
        time_period = request.args.get('timePeriod', default="1y")
        logging.debug("Ticker object created 2")
        sec_file = request.args.get('file', default="10-Q")
        logging.debug("Ticker object created 3")
        growth_type = request.args.get('growthType', default="historical")
        logging.debug("Ticker object created 4")
        type_analyze = request.args.get('analyze', default="peg")
        logging.debug("Ticker object created 5")

        ticker = yf.Ticker(symbol)
        logging.debug("Ticker object")
        hist = ticker.history(period=time_period)
        logging.debug("Ticker object hist")

        # Fill NaN values with 0
        hist.fillna(0, inplace=True)
        valuation = 'earningsGrowth'
        logging.debug("Ticker object valuation")

        if growth_type == "historical":
            growth_data = get_valuation.calculate_historical_growth(hist,time_period, ticker, valuation, sec_file)
        elif growth_type == "forward":
            growth_data = get_valuation.calculate_forward_growth(hist,time_period, ticker, valuation, sec_file)
        else:
            growth_data = {"error": "Invalid growth type specified."}


        logging.debug("Ticker object Growth %s", growth_data["Price to Equity"])

        # growth_array =  []
        # types_growth_array = ['revenueGrowth','earningsGrowth','incomeGrowth', 'dividendGrowth','priceGrowth']
        # for valuation in types_growth_array:
        #     growth_rate = get_valuation.calculate_growth_rate(hist, time_period, ticker, valuation) 
        #     growth_rate_data = {
        #         f"Growth rate for {valuation}" : growth_rate
        #     }
        #     growth_array.append(growth_rate_data)
        
        logging.debug("Ticker object Growth array")

        if type_analyze == "PEG":
            analyze_data = get_valuation.calculate_price_earn(growth_data['Price to Equity'], growth_data['Growth rate data']["growth rate"], "Earnings to growth")
            logging.debug("Ticker object Growth array 2")
        elif type_analyze == "PEGY":
            analyze_data = get_valuation.calculate_price_earn_dividend(growth_data, ticker)

        logging.debug(f"Ticker object stock analyze {analyze_data}")
        data= {
            "Growth data": growth_data,
            # "Various Growths": growth_array,
            "Analysis of stock": analyze_data
        }
        # logging.debug("Ticker object data %s", type(data))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/analyze')
def getLLMCall():
    """Analyze stock data using the Gemini API."""
    symbol = request.args.get('symbol', default="AAPL")
    ticker = yf.Ticker(symbol)
    year = 1
    liquidity_data, profit_data, market_data, cyclical_data = fetch_stock_data(ticker, year)

    if not liquidity_data or not profit_data or not market_data or not cyclical_data:
        return jsonify({"error": "Missing data fields"}), 400

    # Run the model with the provided data
    analysis = gemini_api.run_gemini(ticker, liquidity_data, profit_data, market_data, cyclical_data)

    # Return the analysis as JSON response

    print(analysis)
    return jsonify({"LLM analysis": analysis})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
