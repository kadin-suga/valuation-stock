

import logging
import fetch_stock_data, get_edgar
import pandas as pd

def make_json_serializable(data):
    if isinstance(data, pd.Series):
        return data.to_dict()  # Or data.tolist() if you only need the values
    elif isinstance(data, pd.DataFrame):
        return data.to_dict(orient='records')  # Convert DataFrame to list of dicts
    elif isinstance(data, dict):
        return {k: make_json_serializable(v) for k, v in data.items()}
    else:
        return data


def calculate_dividend_growth(ticker, years, underyear):
    """Calculate the dividend growth rate (DGR)."""
    try:
        if underyear:
            period = "6mo"
            years = 0.5
        else:
            period = f"{years}y"
        
        dividends = ticker.history(period=period, actions=True)['Dividends']
        dividends = dividends[dividends != 0.0]

        if dividends.empty:
            return "No dividend data available."
        
        recent_dividend = dividends.iloc[-1]  # Most recent dividend
        oldest_dividend = dividends.iloc[0]  # Oldest dividend in the period
    
        dgr_cagr = ((recent_dividend / oldest_dividend) ** (1 / years)) - 1
        return dgr_cagr * 100  # Convert to percentage
    except Exception as e:
        return str(e)

def calculate_price_growth(stock_data):
    """Calculate the price growth rate."""
    try:
        stock_data = stock_data[['Close']].copy()
        stock_data['growth'] = stock_data['Close'].pct_change() * 100
        growth_rate = stock_data['growth'].mean()
        if pd.isna(growth_rate):
            return "Price growth data not available"
        return float(growth_rate)
    except Exception as e:
        return f"Error calculating price growth: {str(e)}"

def calculate_growth_rate(stock_data, time_period, ticker, valuation, report):
    """Calculate the growth rate based on the valuation type."""
    try:
        years = fetch_stock_data.extract_number(time_period)
        underYear = years == 6
        if underYear:
            years = 0.5
        
        report_type = True if report == "[10-Q]" else False
        print(report_type)
        
        if valuation == 'revenueGrowth':
            return get_edgar.revenue_growth(ticker.ticker, years, underYear, report_type)
        elif valuation == 'earningsGrowth':
            return get_edgar.earnings_growth(ticker.ticker, years, underYear, report_type)
        elif valuation == 'incomeGrowth':
            return get_edgar.income_growth(ticker.ticker, years, underYear, report_type)
        elif valuation == 'dividendGrowth':
            return calculate_dividend_growth(ticker, years, underYear)
        elif valuation == 'priceGrowth':
            return calculate_price_growth(stock_data)
    except Exception as e:
        return {'error': str(e)}
    
def calculate_historical_growth(stock_data, time_period, ticker, valuation, report_type):
    try:
        print("History Growth")
        growth_rate = calculate_growth_rate(stock_data, time_period, ticker, valuation, report_type)
        # print(growth_rate)
        current_price = ticker.info.get('currentPrice', None)
        # print(current_price)
        trailing_eps = ticker.info['trailingEps']
        # print(trailing_eps)
        pe_ratio = current_price / trailing_eps

        # Convert Series to scalar if necessary
        if isinstance(pe_ratio, pd.Series):
            pe_ratio = pe_ratio.iloc[0]
        if isinstance(growth_rate, pd.Series): 
            growth_rate = growth_rate.iloc[0]
            
        # print(float(pe_ratio))
        # print(growth_rate, "1")

        data = {
            'Price to Equity': float(pe_ratio), 
            'Growth rate data': make_json_serializable(growth_rate),
        }

        return data
    except Exception as e:
        return {'error': str(e)}



def calculate_forward_growth(stock_data, time_period, ticker, valuation, report_type):
    try:
        growth_rate = calculate_growth_rate(stock_data, time_period, ticker, valuation, report_type)
        current_price = ticker.info.get('currentPrice', None)
        forward_eps = ticker.info.get('forwardEps', None)
        pe_ratio = current_price / forward_eps

        # Check if `pe_ratio` or `growth_rate` are Series and convert
        if isinstance(pe_ratio, pd.Series):
            pe_ratio = pe_ratio.iloc[0]
        if isinstance(growth_rate, pd.Series):
            growth_rate = growth_rate.iloc[0]

        if forward_eps is None or current_price is None:
            return {'error': 'Data not available for growth calculation.'}
        
        data={'Price to Equity': float(pe_ratio), 
                'Growth rate': make_json_serializable(growth_rate), 
                }

        return data
    except Exception as e:
        return {'error': str(e)}


    

def calculate_price_earn(price2equity, growth_rate, growth_name):
    try:
        # Calculate PEG value
        peg_value = price2equity / growth_rate
        logging.debug("peg value %s", peg_value)

        data= {
            f"Price / {growth_name}": (peg_value),
            "Type": False  # Type is now correctly set to False here
        }
        return (data)
        # Log the type of PEG value
    except Exception as e:
        logging.error("An error occurred in calculate_price_earn: %s", e)

def calculate_price_earn_dividend(growth_data, ticker):
    try:
        price2equity = growth_data['Price to Equity']
        growth_rate = growth_data['Growth rate data']["growth rate"]

        dividends = ticker.history(period="1y", actions=True)['Dividends']
        dividends = dividends[dividends != 0.0]

        if dividends.empty:
            return "No dividend data available."
        
        recent_dividend = dividends.iloc[-1]  # Most recent dividend
        pegy_value = price2equity /( growth_rate + recent_dividend)

        data= {
            "Price / Earnings to Growth and Dividend yield": pegy_value,
            "Type": True  # Type is now correctly set to True here
        }
        return data
    except Exception as e:
        return ({"error": str(e)}), 500


    


