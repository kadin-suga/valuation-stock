import logging
from dataclasses import dataclass
from typing import Dict, Any, Tuple, List

import get_edgar, fetch_stock_data

@dataclass
class StockDataConfig:
    """Configuration for different types of stock data metrics"""
    liquidity_metrics = {
        "Total debt data": "total_debt",
        "Debt ratio data": "debt_ratio",
        "Times interest earned data": "times_interest_earned",
        "Net working capital ratio data": "networking_capital_to_assets",
        "Current ratio data": "current_ratio",
        "Quick ratio data": "quick_ratio"
    }
    
    profit_metrics = {
        "Profit Margin data": "profit_margin",
        "Growth Rate data": "growth_rate",
        "Return on Capital data": "return_on_capital",
        "Return on Equity data": "return_on_equity",
        "Return on Asset data": "return_on_asset"
    }
    
    cyclical_metrics = {
        "Operating Cycle data": "operating_cycle",
        "Cash Cycle data": "cash_cycle"
    }

class StockDataFetcher:
    """Class to handle fetching and processing stock data"""
    
    def __init__(self, ticker, year, edgar_client):
        self.ticker = ticker
        self.year = year
        self.edgar = edgar_client
        self.config = StockDataConfig()
    
    def _fetch_edgar_data(self, metric_name: str, error_msg: str) -> Dict:
        """Helper method to fetch data from EDGAR"""
        try:
            method = getattr(self.edgar, metric_name)
            return self.edgar.save_df_call_method(self.ticker.ticker, method, self.year) or error_msg
        except AttributeError as e:
            logging.error(f"Method not found: {metric_name}")
            return error_msg
        except Exception as e:
            logging.error(f"Error fetching {metric_name}: {str(e)}")
            return error_msg

    def _fetch_metrics(self, metrics_dict: Dict[str, str], start_issue: int) -> Dict[str, Any]:
        """Helper method to fetch a group of metrics"""
        return {
            key: self._fetch_edgar_data(method, f'Total issue {i + start_issue}')
            for i, (key, method) in enumerate(metrics_dict.items())
        }

    def _fetch_market_data(self) -> Dict[str, Any]:
        """Helper method to fetch market-related data"""
        price = self.ticker.history(period='1d')
        
        price_data = {
            'value': 0.0,
            'change_list': []
        }
        
        if not price.empty:
            price_data['value'] = price['Close'].iloc[0]
            price_data['change_list'] = (price['Close'].pct_change().dropna() * 100).tolist()

        return {
            "Price": price_data['value'],
            "Price change": price_data['change_list'],
            "Market Cap": self.ticker.info.get('marketCap', 0),
            "Market value added": fetch_stock_data.market_value_added(self.ticker),
            "Market to book": fetch_stock_data.market_to_book(self.ticker)
        }

    def fetch_stock_data(self) -> Tuple[Dict, Dict, Dict, Dict]:
        """
        Fetch various stock data points and return them in organized categories.
        
        Returns:
            Tuple containing dictionaries for liquidity, profit, market, and cyclical data
        """
        try:
            logging.debug("Enter fetched stock data")
            
            # Fetch different categories of data
            liquidity_data = self._fetch_metrics(self.config.liquidity_metrics, 1)
            logging.debug("Liquidity stock data")
            
            profit_data = self._fetch_metrics(self.config.profit_metrics, 7)
            logging.debug("Profit stock data")
            
            market_data = self._fetch_market_data()
            logging.debug("Market stock data")
            
            cyclical_data = self._fetch_metrics(self.config.cyclical_metrics, 12)
            logging.debug("Cyclical stock data %s", cyclical_data["Cash Cycle data"])
            
            return liquidity_data, profit_data, market_data, cyclical_data
            
        except Exception as e:
            logging.error(f"Error in fetch_stock_data: {str(e)}")
            return {'error': str(e)}, {}, {}, {}

def fetch_stock_data(ticker, year):
    """Wrapper function to maintain backward compatibility"""
    fetcher = StockDataFetcher(ticker, year, get_edgar)
    return fetcher.fetch_stock_data()