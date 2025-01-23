from datetime import datetime, timedelta
from logging import debug
import logging

from flask import jsonify
import pandas as pd
import edgar_api
import math


def get_description(stock):
    data = edgar_api.data_parser_submission(stock,only_filings_df=False)
    stock_inform = {
        "former names": data['formerNames'],
        "description": data['description'],
        "sector": data['sic'],
        "sector description": data['sicDescription'],
        "insider transaction": data['insiderTransactionForIssuerExists'],
    } 
    return stock_inform


def calculate_growth(stock, years, metric_type, underYear=False, quarterly=True):
    """
    Calculate growth rate for a given financial metric.

    Args:
        stock (str): Stock ticker symbol
        years (int): Number of years to look back
        metric_type (str): Type of metric to analyze ('revenue', 'income', or 'earnings')
        underYear (bool): If True, calculate 6-month growth instead of yearly
        quarterly (bool): If True, use 10-Q reports, else use 10-K reports

    Returns:
        dict: Contains growth rate and historical data
    """
    print(f"{str(metric_type.capitalize())} Growth")

    METRIC_MAPPINGS = {
        'revenue': 'Revenue from Contract with Customer, Excluding Assessed Tax',
        'income': 'Comprehensive Income (Loss), Net of Tax, Attributable to Parent',
        'earnings': 'Earnings Per Share, Diluted'
    }

    if metric_type not in METRIC_MAPPINGS:
        raise ValueError(f"Invalid metric type. Must be one of: {', '.join(METRIC_MAPPINGS.keys())}")

    fact = edgar_api.annual_facts(stock) if quarterly else edgar_api.quarterly_facts(stock)

    if fact.empty:
        return "Financial data not available."

    report_type = "[10-K]"  if quarterly else "[10-Q]"
    print(report_type, "report")
    edgar_api.save_dataframe_to_csv(fact, "csv", stock, report_type, years)

    try:
        df = pd.read_csv(f"./src/python/csv/{stock}/{report_type}_{years}.csv")
        dates = [datetime.strptime(col, '%Y-%m-%d') for col in df.columns[1:]]

        metric_row = df[df['fact'] == METRIC_MAPPINGS[metric_type]]
        if metric_row.empty:
            return f"{str(metric_type.capitalize())} data not available."

        metric_data = metric_row.iloc[0, 1:].astype(float)
        metric_data.index = pd.to_datetime(dates)
        metric_data = metric_data.sort_index(ascending=False)

        print(f"{str(metric_type.capitalize())} Data:", metric_data)

        current_date = metric_data.index[0]
        current_value = metric_data.iloc[0]

        if not underYear:
            if quarterly:
                # Calculate average of the past 4 quarters
                if len(metric_data) < 4:
                    return "Not enough data for 4 quarters."

                recent_4_quarters = metric_data.iloc[:4]
                current_value = recent_4_quarters.mean()
                print(f"Average of the most recent 4 quarters: {current_value}")

                target_quarter_end_date = current_date - pd.DateOffset(years=years)
                past_4_quarters = metric_data[metric_data.index <= target_quarter_end_date].iloc[:4]

                if len(past_4_quarters) < 4:
                    return "Not enough historical data for 4 quarters."

                growth_rate = past_4_quarters.mean() * 100
                print(f"Average of the past 4 quarters {years} years ago: {growth_rate}")
            else:
                target_year = current_date.year - years
                historical_data = metric_data[metric_data.index.year == target_year]

                if historical_data.empty:
                    return f"Historical {metric_type} data not available for the specified period."

                old_value = historical_data.iloc[0]
                growth_rate = ((current_value - old_value) / old_value) * 100
        else:
            if not quarterly:
                return print("Unable to search for data under a year")
            else:
                date_of_interest = current_date - timedelta(days=180)
                historical_data = metric_data[metric_data.index <= date_of_interest]

                if historical_data.empty:
                    return f"Historical {metric_type} data not available for the specified period."

                old_value = historical_data.iloc[0]

        # print(f"old_value: {old_value}, current value: {current_value}")

        metric_data_dict = metric_data.to_dict()
        serialized_data = {str(date): value for date, value in metric_data_dict.items()}

        return {
            'growth rate': float(growth_rate),
            f'{metric_type} data': pd.Series(serialized_data)
        }

    finally:
        edgar_api.delete_csv("csv", stock, report_type, years)


# Wrapper functions to maintain backward compatibility
def revenue_growth(stock, years, underYear=False, quarterly=True):
    return calculate_growth(stock, years, 'revenue', underYear, quarterly)

def income_growth(stock, years, underYear=False, quarterly=True):
    return calculate_growth(stock, years, 'income', underYear, quarterly)

def earnings_growth(stock, years, underYear=False, quarterly=True):
    return calculate_growth(stock, years, 'earnings', underYear, quarterly)

def sanitize_series(series):
    """
    Ensures a pandas Series contains only numeric values.
    Converts non-numeric values to NaN, then fills with 0.
    """
    return pd.to_numeric(series, errors='coerce').fillna(0)


def read_df_return_fact(stock, report_type, years, metrics):
    """
    Reads financial data from a CSV file and retrieves the requested metric(s).
    Sanitizes the data to ensure it is numeric.
    """
    try:
        # Read the CSV file
        csv_path = f"./src/python/csv/{stock}/{report_type}_{years}.csv"
        df = pd.read_csv(csv_path, parse_dates=False)

        # Parse dates from column headers (assuming all date columns are after the first one)
        dates = [datetime.strptime(col, '%Y-%m-%d') for col in df.columns[1:]]

        for metric in metrics:
            # Check if the metric exists in the DataFrame
            metric_row = df[df['fact'] == metric]
            if not metric_row.empty:
                # Extract the row and sanitize the data
                metric_data = metric_row.iloc[0, 1:].astype(str).apply(pd.to_numeric, errors='coerce').fillna(0)
                metric_data.index = pd.to_datetime(dates)  # Assign date index
                metric_data = metric_data.sort_index(ascending=False)  # Sort by date descending
                
                # Serialize the Series to a sanitized dictionary
                metric_data_dict = metric_data.to_dict()
                sanitized_data = {
                    str(date): value if isinstance(value, (int, float)) else 0
                    for date, value in metric_data_dict.items()
                }
                return sanitized_data

        # If none of the metrics are found, return an error
        return {"error": "None of the specified metrics are available in the dataset."}

    except FileNotFoundError:
        return {"error": f"CSV file not found for stock: {stock}, report_type: {report_type}, years: {years}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


def asset_turnover(stock, report_type, years):
    """
    Calculates inventory turnover and average days in inventory.
    Sanitizes input data to ensure no unsupported operand errors.
    """
    target_cogs_data = read_df_return_fact(stock, report_type, years, ["Cost of Goods and Services Sold"])
    target_inventory_data = read_df_return_fact(stock, report_type, years, ["Inventory, Net"])

    # Convert to Series and sanitize
    target_cogs_series = sanitize_series(pd.Series(target_cogs_data))
    target_inventory_series = sanitize_series(pd.Series(target_inventory_data))

    # Calculate metrics
    inventory_turnover = target_cogs_series / target_inventory_series
    avg_days = (target_inventory_series / (target_cogs_series / 365))

    # Convert back to dict
    turnover_data = {
        'Inventory turnover': inventory_turnover.to_dict(),
        'Average days in inventory': avg_days.to_dict()
    }
    return turnover_data


def receivable_turnover(stock, report_type, years):
    """
    Calculates receivable turnover and average collection period.
    Sanitizes input data to ensure no unsupported operand errors.
    """
    target_sales_data = read_df_return_fact(stock, report_type, years, ["Revenue from Contract with Customer, Excluding Assessed Tax"])
    target_rec_data = read_df_return_fact(stock, report_type, years, ["Increase (Decrease) in Accounts Receivable"])

    # Convert to Series and sanitize
    target_sales_series = sanitize_series(pd.Series(target_sales_data))
    target_rec_series = sanitize_series(pd.Series(target_rec_data))

    # Calculate metrics
    receivable_return = target_sales_series / target_rec_series
    avg_collection = (target_rec_series / (target_sales_series / 365))

    turnover_data = {
        'Receivable turnover': receivable_return.to_dict(),
        'Average collection period': avg_collection.to_dict()
    }
    return turnover_data

def operating_cycle(stock, report_type, years):
    # Fetch the data
    asset_data = asset_turnover(stock, report_type, years)
    receivable_data = receivable_turnover(stock, report_type, years)

    # Ensure the expected keys exist in both asset_data and receivable_data
    if 'Average days in inventory' in asset_data and 'Average collection period' in receivable_data:
        asset_value = asset_data['Average days in inventory']
        receivable_value = receivable_data['Average collection period']

        # Handle missing or NaN values by filling with a default value (e.g., 0)
        asset_value = {k: v if isinstance(v, (int, float)) and not pd.isna(v) else 0 for k, v in asset_value.items()}
        receivable_value = {k: v if isinstance(v, (int, float)) and not pd.isna(v) else 0 for k, v in receivable_value.items()}

        # Handle negative values (if you want to ignore them or treat as invalid)
        asset_value = {k: v if v >= 0 else 0 for k, v in asset_value.items()}
        receivable_value = {k: v if v >= 0 else 0 for k, v in receivable_value.items()}

        # Ensure the date ranges match between both datasets
        common_dates = asset_value.keys() & receivable_value.keys()

        # Sum values for the common dates
        cycle_length = {
            date: asset_value[date] + receivable_value[date] 
            for date in common_dates
        }

        # If no valid dates, return an error
        if not cycle_length:
            print("Error: No valid dates for operating cycle calculation.")
            data = {'error': 'No valid dates for operating cycle calculation.'}
        else:
            operating_data = {
                'asset turnover data': asset_data,
                'receivable turnover data': receivable_data
            }
            data = {
                'operating cycle': cycle_length,
                'operating cycle length': {date: f"{value} days" for date, value in cycle_length.items()},
                'operating work': operating_data
            }
    else:
        print("Error: Missing expected keys in asset_data or receivable_data.")
        data = {
            'error': "Could not calculate operating cycle due to missing or invalid data"
        }

    return data

    

def account_payable_period(stock, report_type, years):
    
    target_cogs_data = read_df_return_fact(stock, report_type, years, ["Cost of Goods and Services Sold"])
    target_account_data = read_df_return_fact(stock, report_type, years, ["Accounts Payable, Current", "Accounts Payable and Accrued Liabilities, Current"])
    logging.debug("Account, %s", target_account_data)

    # Convert to Series
    target_cogs_series = sanitize_series(pd.Series(target_cogs_data))
    target_account_series = pd.Series(target_account_data)
    logging.debug("COGS, %s", target_cogs_series)
    logging.debug("Accoun 3, %s", target_account_series)

    payable_period = target_account_series / target_cogs_series
    avg_days = (target_cogs_series / (target_account_series / 365))
    logging.debug("Payable, %s", payable_period.to_dict())
    logging.debug("avg, %s", avg_days.to_dict())

    payable_data = {
        'Accounts Payable period': payable_period.to_dict(),
        'Average days to pay': avg_days.to_dict()
    }
    return payable_data

def cash_cycle(stock, report_type, years):
    # Fetch the data for operating cycle and accounts payable period
    operating_data = operating_cycle(stock, report_type, years)
    logging.debug("Operated %s", operating_data)
    account_payable = account_payable_period(stock, report_type, years)
    logging.debug("Account %s", account_payable)

    # Ensure 'operating cycle' and 'Accounts Payable period' keys exist
    if 'operating cycle' in operating_data and 'Accounts Payable period' in account_payable:
        operating_cycle_data = operating_data['operating cycle']
        accounts_payable_data = account_payable['Accounts Payable period']
        logging.debug("Operating %s", operating_cycle_data)
        logging.debug("Account pay %s", accounts_payable_data)

        # Handle missing or NaN values in both datasets
        operating_cycle_data = {
            k: v if isinstance(v, (int, float)) and not pd.isna(v) else 0
            for k, v in operating_cycle_data.items()
        }
        accounts_payable_data = {
            k: v if isinstance(v, (int, float)) and not pd.isna(v) else 0
            for k, v in accounts_payable_data.items()
        }

        # Handle negative values in both datasets (if you want to ignore them or treat as invalid)
        operating_cycle_data = {k: v if v >= 0 else 0 for k, v in operating_cycle_data.items()}
        accounts_payable_data = {k: v if v >= 0 else 0 for k, v in accounts_payable_data.items()}

        # Ensure the date ranges match between both datasets
        common_dates = operating_cycle_data.keys() & accounts_payable_data.keys()

        # Calculate the cash conversion cycle for the common dates
        cash_cycle_data = {
            date: operating_cycle_data[date] - accounts_payable_data[date]
            for date in common_dates
        }
        logging.debug("Cash cycle %s", cash_cycle_data)
        # If no valid dates for calculation, return an error
        if not cash_cycle_data:
            print("Error: No valid dates for cash cycle calculation.")
            cash_data = {'error': 'No valid dates for cash cycle calculation.'}
        else:
            cash_data = {
                "Cash conversion cycle": cash_cycle_data,
                "Cash conversion cycle length": {date: f"{value} days" for date, value in cash_cycle_data.items()},
                "Account payable data": account_payable
            }
    else:
        print("Error: Missing expected keys in operating_data or account_payable.")
        cash_data = {'error': 'Could not calculate cash cycle due to missing or invalid data'}

    return cash_data

    

def debt_ratio(stock, report_type, years):
    target_liability_data = read_df_return_fact(stock, report_type, years, ["Liabilities, Noncurrent"])
    target_equity_data = read_df_return_fact(stock, report_type, years, ["Stockholders' Equity Attributable to Parent"])

    # Convert to Series
    target_liability_series = pd.Series(target_liability_data)
    target_equity_series = pd.Series(target_equity_data)

    long_term_debt = (target_liability_series / (target_liability_series + target_equity_series))
    long_term_debt_equity = target_liability_series / target_equity_series

    data = {
        'Long term debt ratio': long_term_debt.to_dict(),
        'Long term debt-equity ratio': long_term_debt_equity.to_dict()
    }
    return data
    
def total_debt(stock, report_type, years):
    target_asset_data = read_df_return_fact(stock, report_type, years, ["Assets"])
    target_liab_data = read_df_return_fact(stock, report_type, years, ["Liabilities"])

    # Convert to Series
    target_asset_series = pd.Series(target_asset_data)
    target_liab_series = pd.Series(target_liab_data)

    total_debt_ratio = target_liab_series / target_asset_series

    data = {
        'Total debt': total_debt_ratio.to_dict()
    }
    return data

def times_interest_earned(stock, report_type, years):
    target_income_data = read_df_return_fact(stock, report_type, years, ["Net Income (Loss) Attributable to Parent"])
    target_interest_data = read_df_return_fact(stock, report_type, years, ["Nonoperating Income (Expense)"])
    target_tax_data = read_df_return_fact(stock, report_type, years, ["Income Tax Expense (Benefit)"])

    # Convert to Series
    target_income_series = pd.Series(target_income_data)
    target_interest_series = pd.Series(target_interest_data)
    target_tax_series = pd.Series(target_tax_data)

    # Calculate EBIT
    ebit = target_income_series + target_interest_series + target_tax_series

    if target_interest_series.empty or (target_interest_series == 0).all():
        raise ValueError("Interest expense is zero or undefined. Cannot calculate TIE.")
    
    tie_ratio = ebit / target_interest_series

    data = {
        "Times Interest Earned": tie_ratio.to_dict()
    }
    return data

def networking_capital(liability, asset):
    return  asset - liability

def networking_capital_to_assets(stock, report_type, years):
    target_liab_data = read_df_return_fact(stock, report_type, years, ["Liabilities, Current"])
    target_asset_curr_data = read_df_return_fact(stock, report_type, years, ["Assets, Current"])
    target_asset_data = read_df_return_fact(stock, report_type, years, ["Assets"])

    # Convert to Series
    target_liab_series = pd.Series(target_liab_data)
    target_asset_curr_series = pd.Series(target_asset_curr_data)
    target_asset_series = pd.Series(target_asset_data)

    networking_capital_series = target_asset_curr_series - target_liab_series
    is_liquid = (networking_capital_series > 0).astype(int)
    networking_capital_ratio = networking_capital_series / target_asset_series

    data = {
        'Net working capital to Assets': networking_capital_ratio.to_dict(),
        'Net working Capital': networking_capital_series.to_dict(),
        'Is it liquid': is_liquid.to_dict()
    }
    return data

def current_ratio(stock, report_type, years):
    target_liab_data = read_df_return_fact(stock, report_type, years, ["Liabilities, Current"])
    target_asset_data = read_df_return_fact(stock, report_type, years, ["Assets, Current"])

    # Convert to Series
    target_liab_series = pd.Series(target_liab_data)
    target_asset_series = pd.Series(target_asset_data)

    current_ratio_series = target_asset_series / target_liab_series
    
    return current_ratio_series.to_dict()

def quick_ratio(stock, report_type, years):
    target_cash_data = read_df_return_fact(stock, report_type, years, ["Cash and Cash Equivalents, at Carrying Value"])
    target_market_curr_data = read_df_return_fact(stock, report_type, years, ["Marketable Securities, Current"])
    target_liab_data = read_df_return_fact(stock, report_type, years, ["Liabilities, Current"])
    target_receiv_data = read_df_return_fact(stock, report_type, years, ["Nontrade Receivables, Current"])

    # Convert to Series
    target_cash_series = pd.Series(target_cash_data)
    target_market_curr_series = pd.Series(target_market_curr_data)
    target_liab_series = pd.Series(target_liab_data)
    target_receiv_series = pd.Series(target_receiv_data)

    quick_ratio_value = ((target_cash_series + target_market_curr_series + target_receiv_series) / 
                        target_liab_series)

    data = {
        "Quick Ratio": quick_ratio_value.to_dict()
    }
    return data



def after_tax_interest_expense(stock, report_type, years):
    target_tax_data = read_df_return_fact(stock, report_type, years, ["Income Tax Expense (Benefit)"])
    target_income_data = read_df_return_fact(stock, report_type, years, ["Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest"])

    target_tax_series = pd.Series(target_tax_data)
    target_income_series = pd.Series(target_income_data)

    return target_tax_series / target_income_series


def return_on_capital(stock, report_type, years):
    target_interest_data = after_tax_interest_expense(stock, report_type, years)
    target_income_data = read_df_return_fact(stock, report_type, years, ["Net Income (Loss) Attributable to Parent"])
    target_liab_data = read_df_return_fact(stock, report_type, years, ["Liabilities"])
    target_equity_data = read_df_return_fact(stock, report_type, years, ["Stockholders' Equity Attributable to Parent"])

    # Convert to Series
    target_interest_series = pd.Series(target_interest_data)
    target_income_series = pd.Series(target_income_data)
    target_liab_series = pd.Series(target_liab_data)
    target_equity_series = pd.Series(target_equity_data)

    target_capital_series = target_equity_series + target_liab_series
    return_on_capital_series = ((target_interest_series + target_income_series) / target_capital_series)

    data = {
        "Return on Capital": return_on_capital_series.to_dict()
    }
    return data

def return_on_equity(stock, report_type, years):
    target_income_data = read_df_return_fact(stock, report_type, years, ["Net Income (Loss) Attributable to Parent"])
    target_equity_data = read_df_return_fact(stock, report_type, years, ["Stockholders' Equity Attributable to Parent"])
    
    # Convert to Series
    target_income_series = pd.Series(target_income_data)
    target_equity_series = pd.Series(target_equity_data)
    
    ROE_series = target_income_series / target_equity_series
    
    data = {
        "Return on Equity": ROE_series.to_dict()
    }
    return data

def return_on_asset(stock, report_type, years):
    target_income_data = read_df_return_fact(stock, report_type, years, ["Net Income (Loss) Attributable to Parent"])
    target_asset_data = read_df_return_fact(stock, report_type, years, ["Assets"])
    target_tax_data = after_tax_interest_expense(stock, report_type, years)

    # Convert to Series
    target_income_series = pd.Series(target_income_data)
    target_asset_series = pd.Series(target_asset_data)
    target_tax_series = pd.Series(target_tax_data)

    ROA_series = ((target_tax_series + target_income_series) / target_asset_series)
    
    data = {
        "Return on Asset": ROA_series.to_dict()
    }
    return data


def growth_rate(stock, report_type, years):
    target_income_data = read_df_return_fact(stock, report_type, years, ["Net Income (Loss) Attributable to Parent"])
    target_retain_data = read_df_return_fact(stock, report_type, years, ["Retained Earnings (Accumulated Deficit)"])
    target_stockholder_data = read_df_return_fact(stock, report_type, years, ["Stockholders' Equity Attributable to Parent"])
    target_dividend_data = read_df_return_fact(stock, report_type, years, ["Dividends"])

    # Convert to Series
    target_income_series = pd.Series(target_income_data)
    target_retain_series = pd.Series(target_retain_data)
    target_stockholder_series = pd.Series(target_stockholder_data)
    target_dividend_series = pd.Series(target_dividend_data)

    return_on_equity = target_income_series / target_stockholder_series
    retention_ratio_1 = target_retain_series / target_income_series
    retention_ratio_2 = 1 - (target_dividend_series / target_income_series)

    internal_growth_rate = return_on_equity * retention_ratio_1
    sustainable_growth_rate = return_on_equity * retention_ratio_2

    data = {
        "Internal Growth Rate": internal_growth_rate.to_dict(),
        "Sustainable Growth Rate": sustainable_growth_rate.to_dict()
    }
    return data



def profit_margin(stock, report_type, years):
    """
    Calculates profit margin and operating profit margin.
    Sanitizes input data to ensure no unsupported operand errors.
    """
    # Read and sanitize data
    target_income_data = read_df_return_fact(stock, report_type, years, ["Net Income (Loss) Attributable to Parent"])
    target_revenue_data = read_df_return_fact(stock, report_type, years, ["Revenue from Contract with Customer, Excluding Assessed Tax"])
    target_tax_data = after_tax_interest_expense(stock, report_type, years)
    target_cogs_data = read_df_return_fact(stock, report_type, years, ["Cost of Goods and Services Sold"])

    # Convert to Series and sanitize
    target_income_series = sanitize_series(pd.Series(target_income_data))
    target_revenue_series = sanitize_series(pd.Series(target_revenue_data))
    target_tax_series = sanitize_series(pd.Series(target_tax_data))
    target_cogs_series = sanitize_series(pd.Series(target_cogs_data))

    # Perform calculations
    profit_margin_data = (target_revenue_series - target_cogs_series) / target_revenue_series
    operating_profit_data = (target_tax_series + target_income_series) / target_revenue_series

    # Convert results back to dictionaries for JSON serialization
    data = {
        'Profit margin': profit_margin_data.to_dict(),
        'Operating profit margin': operating_profit_data.to_dict()
    }

    return data
def is_negative_zero(x):
    return x == 0 and math.copysign(1, x) == -1

def sanitize_data(data):
    """
    Recursively sanitize data to make it JSON-compliant:
    - Replace NaN, Infinity, and -Infinity with 0.
    - Convert negative zero to 0.
    - Ensure all keys in dictionaries are strings.
    """
    if isinstance(data, dict):
        # Convert all keys to strings and recursively sanitize values
        return {str(k): sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        # Recursively sanitize each element in the list
        return [sanitize_data(v) for v in data]
    elif isinstance(data, float):
        # Replace non-finite numbers with 0
        if math.isnan(data) or math.isinf(data) or is_negative_zero(data):
            return 0
        return data
    elif isinstance(data, int):
        # Handle edge cases for integers (no-op, included for completeness)
        return data
    else:
        # Return the value as is (for str, bool, None, etc.)
        return data

    
def save_df_call_method(stock, method, years):
    try:
        # Get financial data
        fact = edgar_api.annual_facts(stock)
        if fact.empty:
            return {"error": "Financial data not available."}
        
        # Save the data to a CSV file
        report_type = "[10-K]"
        edgar_api.save_dataframe_to_csv(fact, "csv", stock, report_type, years)
        
        # Call the method to get the result
        result = method(stock, report_type, years)
        result = sanitize_data(result)
        # Check and handle the result based on its type
        if isinstance(result, pd.DataFrame):
            # For DataFrame: Replace NaN values with 0
            result.fillna(0, inplace=True)
        elif isinstance(result, pd.Series):
            # For Series: Replace NaN values with 0 and convert to dictionary
            result = result.fillna(0).to_dict()
        
        
        # Delete the CSV file after processing
        edgar_api.delete_csv("csv", stock, report_type, years)
        
        # Return the cleaned result
        return result
    except Exception as e:
        return {"error": str(e)}





# print( save_df_call_method("AAPL", cash_cycle, 1)) 
# print(jsonify(save_df_call_method("AAPL", profit_margin, 1))) 
# print(jsonify(save_df_call_method("AMZN", profit_margin, 1))) 
#  python3 src/python/get_edgar.py
# Cost of capital not working on    
# def economic_value_add(stock, report_type, years):
#     target_interest_data = after_tax_interest_expense(stock, report_type, years)
#     target_income_data = read_df_return_fact(stock, report_type, years, "Net Income (Loss) Attributable to Parent")
#     target_liab_data = read_df_return_fact(stock, report_type, years, "Liabilities")
#     target_equity_data = read_df_return_fact(stock,report_type, years, "Stockholders' Equity Attributable to Parent")
#     target_capital_data = target_equity_data + target_liab_data



#     pass
