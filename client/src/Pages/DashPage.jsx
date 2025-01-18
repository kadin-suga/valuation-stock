import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Dash() {
  const navigate = useNavigate();
  const [stockName, setStockName] = useState('');
  const [stockTicker, setStockTicker] = useState('');
  const [error, setError] = useState(null);

  const sendBackend = async () => {
    try {
      if (!stockTicker) {
        setError('Please enter a valid stock ticker.');
        return null;
      }

      const url = `http://127.0.0.1:5000/bulk_stock_data?symbol=${stockTicker}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        const backendError = await response.text();
        throw new Error(backendError || 'Error fetching stock data');
      }

      return await response.json();
    } catch (error) {
      setError('Could not fetch stock data. Please try again.');
      return null;
    }
  };

  const handleSearch = async () => {
    if (stockTicker) {
      const data = await sendBackend();
      if (data) {
        navigate(`/${stockTicker}`, { state: { stockName, stockTicker, data } });
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-gray-100">
      <div className="max-w-md mx-auto px-4 py-24">
        {/* Header Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
            Stock Analysis
          </h1>
          <p className="text-gray-400 text-lg">
            Enter a stock to begin your analysis
          </p>
        </div>

        {/* Search Card */}
        <div className="bg-gray-800 rounded-2xl shadow-2xl border border-gray-700 p-8">
          <div className="space-y-6">
            {/* Stock Name Input */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Stock Name
              </label>
              <input
                type="text"
                value={stockName}
                onChange={(e) => setStockName(e.target.value)}
                placeholder="Apple"
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              />
            </div>

            {/* Stock Ticker Input */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Stock Ticker
              </label>
              <input
                type="text"
                value={stockTicker}
                onChange={(e) => setStockTicker(e.target.value.toUpperCase())}
                placeholder="AAPL"
                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-gray-100 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              />
            </div>


            {/* Search Button */}
            <button
              onClick={handleSearch}
              disabled={!stockTicker}
              className="w-full px-8 py-4 bg-gradient-to-r from-blue-500 to-emerald-500 text-white font-semibold rounded-xl shadow-lg hover:from-blue-600 hover:to-emerald-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 transition duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              Search
            </button>

            {/* Error Display */}
            {error && <p className="text-red-500 text-sm mt-4">{error}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dash;
