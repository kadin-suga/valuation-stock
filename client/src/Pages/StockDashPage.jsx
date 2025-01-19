import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Description from '../ui/description';
import Financials from '../ui/Financials';
import Valuation from '../ui/Valuation';
import Summary from '../ui/Summary';
import StockChart from '../ui/StockChart';
import { IoIosRefresh } from "react-icons/io";
import PuffLoader from "react-spinners/PuffLoader";

function StockDash() {
  const navigate = useNavigate();
  const location = useLocation();

  const { stockName, stockTicker, data } = location.state || {};
  const [currPrice, setCurrPrice] = useState(data?.['Market data']?.['Price']?.toFixed(2) || 'N/A');
  const [currPriceChange, setCurrPriceChange] = useState(data?.['Market data']?.['Price change'] || '0.00');
  const [currPriceChangePercent, setCurrPriceChangePercent] = useState(data?.['Market data']?.['Price change percent'] || '0.00');
  const [activeTab, setActiveTab] = useState(0);
  const [aiResponse, setAiResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const tabs = ['Description', 'Chart', 'Financials', 'Valuations', 'AI Summary'];
  const contents = [<Description />, <StockChart />, <Financials />, <Valuation />, <Summary aiResponse={aiResponse} />];

  const sendBackend = async () => {
    try {
      setLoading(true);
      setError(null); // Clear previous errors
      if (!stockTicker) {
        setError('Please enter a valid stock ticker.');
        setLoading(false);
        return null;
      }

      const url = `http://127.0.0.1:5000/analyze?symbol=${stockTicker}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        const backendError = await response.text();
        throw new Error(backendError || 'Error fetching stock data');
      }

      const data = await response.json();
      setLoading(false);
      return data;
    } catch (error) {
      setError('Could not fetch AI analysis. Please try again.');
      setLoading(false);
      return null;
    }
  };

  const updateStock = async () => {
    try {
      setLoading(true);
      setError(null);
      if (!stockTicker) {
        setError('Please enter a valid stock ticker.');
        setLoading(false);
        return null;
      }

      const url = `http://127.0.0.1:5000/cur_stock_price?symbol=${stockTicker}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        const backendError = await response.text();
        throw new Error(backendError || 'Error fetching stock data');
      }

      const data = await response.json();
      setCurrPrice(data?.['Current price']?.toFixed(2) || 'N/A');
      setCurrPriceChange(data?.['Price change']?.[0]?.toFixed(2) || '0.00');
      setCurrPriceChangePercent(data?.['Price change']?.[1]?.toFixed(2) || '0.00');
      setLoading(false);
    } catch (error) {
      setError('Could not fetch stock data. Please try again.');
      setLoading(false);
    }
  };

  // Fetch AI response when the AI Summary tab is active
  useEffect(() => {
    const fetchAiResponse = async () => {
      if (activeTab === 4 && !aiResponse) {
        const data = await sendBackend();
        setAiResponse(data);
      }
    };

    fetchAiResponse();
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-gray-100 relative">
      {/* Overlay for loader */}
      {loading && (
        <div className="absolute inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <PuffLoader color="#4A90E2" size={60} />
        </div>
      )}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="mb-4">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center px-4 py-2 text-sm font-medium text-white bg-gray-700 rounded-md hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              ← Back
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
                {stockName}
              </h1>
              <p className="text-xl text-gray-400 mt-2">{stockTicker}</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-100 flex items-center">
                <button
                  onClick={updateStock}
                  className="mr-2 p-2 bg-gray-700 hover:bg-gray-600 rounded-full"
                  title="Refresh Price"
                >
                  <IoIosRefresh />
                </button>
                ${currPrice}
              </div>
              <div
                className={`text-lg mt-1 ${
                  parseFloat(currPriceChange) >= 0 ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {currPriceChange} ({currPriceChangePercent}%)
              </div>
            </div>
          </div>
        </div>
        {/* Tabs */}
        <div className="pt-14">
          <div className="flex gap-3 justify-center items-center">
            {tabs.map((tab, index) => (
              <button
                key={`tab_${index}`}
                onClick={() => setActiveTab(index)}
                className={`px-4 border ${
                  activeTab === index ? 'bg-gray-600' : ''
                } text-white py-3 hover:bg-gray-700`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
        {/* Content */}
        <div className="w-full mx-auto px-4 py-12 my-2 bg-gray-400">
          <div className="flex flex-col mx-auto">
            {contents.map((content, index) =>
              activeTab === index ? <div key={`content_${index}`}>{content}</div> : null
            )}
          </div>
        </div>
        {/* Display error if present */}
        {error && <div className="text-red-500 mt-4 text-center">{error}</div>}
      </div>
    </div>
  );
}

export default StockDash;
