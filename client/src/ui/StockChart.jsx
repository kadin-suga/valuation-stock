import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import ChartGenerate from './ChartGenerate';

function StockChart() {
    const location = useLocation();
    const { stockName, stockTicker } = location.state || {};
    const [timePeriod, setTimePeriod] = useState("1y");
    const [chartData, setChartData] = useState(null);

    // Function to fetch stock data based on the selected time period
    const fetchStockData = async () => {
        try {
            if (!stockTicker) {
                console.error('Please enter a valid stock ticker.');
                return;
            }

            const url = `http://127.0.0.1:5000/stock_history?symbol=${stockTicker}&timePeriod=${timePeriod}`;
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });

            if (!response.ok) {
                const backendError = await response.text();
                throw new Error(backendError || 'Error fetching stock data');
            }

            const fetchedData = await response.json();
            // Transform the history data into a dictionary suitable for ChartGenerate
            const transformedData = fetchedData?.History.reduce((acc, entry) => {
                acc[entry.Date] = entry.Close;
                return acc;
            }, {});

            setChartData(transformedData);
        } catch (error) {
            console.error('Could not fetch stock data. Please try again.', error);
        }
    };

    // Fetch stock data whenever `timePeriod` changes
    useEffect(() => {
        if (stockTicker) {
            fetchStockData();
        }
    }, [timePeriod, stockTicker]);

    return (
        <div className="mt-8 w-full max-w-4xl bg-white rounded-lg shadow-md p-6">
            <div>
                {chartData ? (
                    <ChartGenerate
                        chartId={stockName}
                        chartLabel={`${stockName} History (${timePeriod})`}
                        chartData={chartData}
                    />
                ) : (
                    <p>Loading chart...</p>
                )}
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                    Change time period
                </label>
                <select
                    value={timePeriod}
                    onChange={(e) => setTimePeriod(e.target.value)}
                    className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
                >
                    <option value="6mo">6 Months</option>
                    <option value="1y">1 Year</option>
                    <option value="2y">2 Years</option>
                    <option value="5y">5 Years</option>
                </select>
            </div>
        </div>
    );
}

export default StockChart;
