import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import Result from '../ui/Result';
import StockAnalysis from '../ui/Result';
import PuffLoader from "react-spinners/PuffLoader";


const Valuation = () => {
  const location = useLocation();
  const { stockName, stockTicker } = location.state || {};

  const [analysis, setAnalysis] = useState('PEG');
  const [growthType, setGrowthType] = useState('historical');
  const [timePeriod, setTimePeriod] = useState('1y');
  const [SEC_filing, setSEC_filing] = useState('10-k');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false)
  
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    setError(null);
    setResult(null);
    try {
      setLoading(true)
      if (!stockTicker) {
        setError('Please enter a valid stock ticker.');
        return;
      }

      const url = `http://127.0.0.1:5000/valuate?symbol=${stockTicker}&file=${SEC_filing}&growthType=${growthType}&timePeriod=${timePeriod}&analyze=${analysis}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const backendError = await response.text();
        throw new Error(backendError || 'Error fetching stock data');
      }

      const data = await response.json();
      setLoading(false)
      setResult(data);
    } catch (error) {
      setLoading(false)
      setError('Could not fetch stock data. Please try again.');
    }
  };

  return (
    <div className="space-y-8 text-gray-800 w-full max-w-7xl mx-auto">
      {/* Main Analysis Card */}
      {loading && (
        <div className="absolute inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <PuffLoader color="#4A90E2" size={60} />
        </div>
      )}
      <div className="bg-white rounded-lg shadow p-8">
        <h3 className="text-2xl font-semibold mb-6">Valuation Analysis</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left Column */}
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Valuation Style
              </label>
              <select
                value={analysis}
                onChange={(e) => setAnalysis(e.target.value)}
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              >
                <option value="PEG">PEG valuation</option>
                <option value="PEGY">PEGY valuation</option>
              </select>
            </div>

          </div>

          {/* Right Column */}
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Growth Type
              </label>
              <select
                value={growthType}
                onChange={(e) => setGrowthType(e.target.value)}
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              >
                <option value="historical">Historical</option>
                <option value="forward">Forward</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Time Period
              </label>
              <select
                value={timePeriod}
                onChange={(e) => setTimePeriod(e.target.value)}
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
              >
                <option value="6mo">6 Months</option>
                <option value="1y">1 Year</option>
                <option value="5y">5 Years</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                SEC Filing Report <span className="text-red-500">*</span>
              </label>
              <div className="flex space-x-6 bg-gray-50 p-4 rounded-lg border border-gray-300">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="radio"
                    value="10-Q" 
                    checked={SEC_filing === "10-Q"}
                    onChange={(e) => setSEC_filing(e.target.value)}
                    className="w-4 h-4 text-blue-500 border-gray-300 focus:ring-blue-500"
                    required
                  />
                  <span className="text-gray-700">10-Q Report</span>
                </label>
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="radio"
                    value="10-K"
                    checked={SEC_filing === "10-K"}
                    onChange={(e) => setSEC_filing(e.target.value)}
                    className="w-4 h-4 text-blue-500 border-gray-300 focus:ring-blue-500"
                    required
                  />
                  <span className="text-gray-700">10-K Report</span>
                </label>
              </div>
              {!SEC_filing && <p className="text-red-500 text-sm mt-1">Please select a SEC filing report</p>}
            </div>
          </div>
        </div>

        {/* Analysis Button */}
        <div className="mt-8 flex justify-center">
          <button
            onClick={handleSearch}
            disabled={!SEC_filing}
            className={`px-8 py-4 text-white font-semibold rounded-lg shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200 ${
              SEC_filing 
                ? 'bg-blue-500 hover:bg-blue-600' 
                : 'bg-gray-400 cursor-not-allowed'
            }`}
          >
            Analyze Stock
          </button>
        </div>
      </div>

      {/* Error Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
          {error}
        </div>
      )}

      {/* Results Section */}
      {result && !result.error && (
        <div className="bg-white rounded-lg shadow p-8">
          <StockAnalysis
            name={stockName}
            ticker={stockTicker}
            data={result}
            valuation={analysis}
            timePeriod={timePeriod}
            SEC_filing={SEC_filing}
          />
        </div>
      )}

      {result?.error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
          Backend Error: {result.error}
        </div>
      )}
    </div>
  );
};

export default Valuation;