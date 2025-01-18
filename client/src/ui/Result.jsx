import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/Card';
import StockChart from './StockChart';

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
  });
};

const StockAnalysis = ({ data, name, ticker, growthType, valuation, timePeriod }) => {
  if (!data) {
    return (
      <Card className="w-full max-w-3xl mx-auto">
        <CardContent className="p-6">
          <p className="text-center text-gray-500">No data available</p>
        </CardContent>
      </Card>
    );
  }

  // Process earnings data for the chart
  const earningsData = Object.entries(
    (data['Growth_data'] &&
      data['Growth_data']['Growth_rate_data'] &&
      data['Growth_data']['Growth_rate_data']['earnings_data']) || {}
  )
    .map(([date, value]) => ({
      date: formatDate(date),
      earnings: value,
    }))
    .sort((a, b) => new Date(a.date) - new Date(b.date));

  const renderRatio = (type, value, description) => (
    <div className="relative group bg-gray-50 p-4 rounded-lg">
      <p className="text-sm text-gray-500 cursor-pointer">{type} Ratio</p>
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64 p-2 text-sm text-white bg-gray-800 rounded-md shadow-lg hidden group-hover:block">
        {description}
      </div>
      <p
        className={`text-2xl font-bold ${
          value <= 1 ? 'text-green-400' : 'text-red-400'
        }`}
      >
        {value?.toFixed(2) || 'N/A'}
      </p>
    </div>
  );

  return (
    <div className="space-y-6 w-full max-w-3xl mx-auto">
      {/* Main Analysis Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Stock Analysis Result</CardTitle>
          <CardDescription>
            <div className="grid grid-cols-2 gap-4 mt-2">
              <div>
                <span className="font-medium">Company:</span> {name || 'N/A'}
              </div>
              <div>
                <span className="font-medium">Symbol:</span> {ticker || 'N/A'}
              </div>
            </div>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-2 gap-4">
              {data['Analysis of stock']?.['Type'] === false
                ? renderRatio(
                    'PEG',
                    data['Analysis of stock']['Price / Earnings to growth'],
                    'The PEG ratio is used to determine a stock\'s value (Price to earning) while also factoring in the company\'s expected earnings growth.'
                  )
                : renderRatio(
                    'PEGY',
                    data['Analysis of stock']['Price / Earnings to Growth and Dividend yield'],
                    'PEGY ratio takes into consideration the stock\'s potential for future earnings growth and dividend payments.'
                  )}
              <div className="bg-gray-50 p-4 rounded-lg relative group">
                <p className="text-sm text-gray-500">P/E Ratio</p>
                <p
                  className={`text-2xl font-bold ${
                    parseFloat(data['Growth data']?.['Price to Equity']) < 15
                      ? 'text-green-500' // Undervalued
                      : parseFloat(data['Growth data']?.['Price to Equity']) <= 25
                      ? 'text-orange-500' // Fairly valued
                      : 'text-red-500' // Overvalued
                  }`}
                >
                  {data['Growth data']?.['Price to Equity']?.toFixed(2) || 'N/A'}
                </p>

                {/* Tooltip */}
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-72 p-2 text-sm text-white bg-gray-800 rounded-md shadow-lg hidden group-hover:block">
                  {(() => {
                    const peRatio = parseFloat(data['Growth data']?.['Price to Equity']);
                    if (peRatio < 15) {
                      return (
                        <>
                          <strong>Low P/E (Below 15):</strong>
                          <br />
                          The stock might be <strong>undervalued</strong> or facing challenges. 
                          Often seen in mature, slow-growing companies or cyclical industries during downturns.
                          <br />
                          <strong>Risk:</strong> Could indicate problems with the company or market pessimism.
                        </>
                      );
                    } else if (peRatio <= 25) {
                      return (
                        <>
                          <strong>Average P/E (15-25):</strong>
                          <br />
                          The stock is <strong>fairly valued</strong> based on historical norms. 
                          Often seen in companies with steady growth and moderate market expectations.
                        </>
                      );
                    } else if (peRatio > 25) {
                      return (
                        <>
                          <strong>High P/E (Above 25):</strong>
                          <br />
                          The stock might be <strong>overvalued</strong> or reflect high growth expectations.
                          Often seen in growth-oriented companies, especially in tech or emerging industries.
                          <br />
                          <strong>Risk:</strong> Could be expensive, and if growth expectations aren’t met, the price could fall.
                        </>
                      );
                    } else {
                      return 'P/E Ratio data is unavailable.';
                    }
                  })()}
                </div>
              </div>

            </div>

            {/* Earnings Chart */}
            {/* <div className="h-64 mt-6">
              <p className="text-sm font-medium mb-2">Earnings Growth Trend</p>
              <ResponsiveContainer width="100%" height="100%">
                <StockChart
                  chartId="2345678"
                  chartlabel="Earnings Growth"
                  chartData={
                    data?.['Growth data']?.['Growth rate data']?.['earnings data']
                  }
                />
              </ResponsiveContainer>
            </div> */}

            {/* Growth Analysis */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="text-lg">Growth Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose">
                  <p>
                    {growthType === 'forward'
                      ? 'Forward Growth: Based on analyst projections and company guidance, providing insights into expected future performance.'
                      : `Historical Growth: Reflects the compound annual growth rate (CAGR) over ${timePeriod}, showing actual past performance.`}
                  </p>
                  <p className="mt-2">
                    Growth Rate:{' '}
                    {data['Growth data']?.['Growth rate data']?.['growth rate']?.toFixed(2)}
                    %
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default StockAnalysis;
