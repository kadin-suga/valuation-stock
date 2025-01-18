import React from 'react';
import { useLocation } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Financials = () => {
  const location = useLocation();
  const financialData = location.state?.data || {};

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString();
  };

  // Enhanced data processing for nested structures
  const processChartData = (data) => {
    if (!data) return [];
    if (typeof data === 'object' && !Array.isArray(data)) {
      return Object.entries(data).map(([date, value]) => ({
        date: formatDate(date),
        value: typeof value === 'number' ? value : 0
      }));
    }
    return [];
  };

  // Updated nested data processing
  const processNestedData = (data, key = 'value') => {
    if (!data) return [];
    if (typeof data === 'object' && !Array.isArray(data)) {
      return Object.entries(data).map(([date, value]) => ({
        date: formatDate(date),
        [key]: typeof value === 'number' ? value : 0
      }));
    }
    return [];
  };

  const ChartComponent = ({ title, data, height = 300 }) => {
    if (!data || data.length === 0) return null;

    return (
      <div className="w-full">
        <h4 className="text-lg font-medium mb-2 text-gray-700">{title}</h4>
        <div style={{ height: `${height}px` }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  const DataSection = ({ title, data }) => {
    if (!data) return null;

    return (
      <Card className="w-full mb-8">
        <CardHeader>
          <CardTitle className='text-black text-xl'>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {Object.entries(data).map(([key, chartData]) => (
              <ChartComponent
                key={key}
                title={key.replace(/_/g, ' ').replace(/data/i, '').trim()}
                data={chartData}
              />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  // Updated data processing logic with correct paths
  const processFinancialData = (rawData) => {
    if (!rawData || Object.keys(rawData).length === 0) return null;

    return {
      cyclicalData: {
        title: "Cyclical Analysis",
        data: {
          "Cash Conversion Cycle": processChartData(rawData?.["Cyclical data"]?.["Cash Cycle data"]?.["Cash conversion cycle"]),
          "Operating Cycle": processChartData(rawData?.["Cyclical data"]?.["Operating Cycle data"]?.["operating cycle"]),
          "Accounts Payable": processChartData(rawData?.["Cyclical data"]?.["Cash Cycle data"]?.["Account payable data"]?.["Accounts Payable period"]),
          "Average Days to Pay": processChartData(rawData?.["Cyclical data"]?.["Cash Cycle data"]?.["Account payable data"]?.["Average days to pay"]),
          "Asset Turnover": processChartData(rawData?.["Cyclical data"]?.["Operating Cycle data"]?.["operating work"]?.["asset turnover data"]?.["Inventory turnover"]),
          "Average Days in Inventory": processChartData(rawData?.["Cyclical data"]?.["Operating Cycle data"]?.["operating work"]?.["asset turnover data"]?.["Average days in inventory"]),
          "Receivable Turnover": processChartData(rawData?.["Cyclical data"]?.["Operating Cycle data"]?.["operating work"]?.["receivable turnover data"]?.["Receivable turnover"]),
          "Average Collection Period": processChartData(rawData?.["Cyclical data"]?.["Operating Cycle data"]?.["operating work"]?.["receivable turnover data"]?.["Average collection period"])
        }
      },
      liquidityData: {
        title: "Liquidity Analysis",
        data: {
          "Current Ratio": processChartData(rawData?.["Liquidity data"]?.["Current ratio data"]),
          "Quick Ratio": processChartData(rawData?.["Liquidity data"]?.["Quick ratio data"]?.["Quick Ratio"]),
          "Net Working Capital": processChartData(rawData?.["Liquidity data"]?.["Net working capital ratio data"]?.["Net working Capital"]),
          "Net Working Capital to Assets": processChartData(rawData?.["Liquidity data"]?.["Net working capital ratio data"]?.["Net working capital to Assets"]),
          "Times Interest Earned": processChartData(rawData?.["Liquidity data"]?.["Times interest earned data"]?.["Times Interest Earned"]),
          "Total Debt Ratio": processChartData(rawData?.["Liquidity data"]?.["Total debt data"]?.["Total debt"]),
          "Long Term Debt Ratio": processChartData(rawData?.["Liquidity data"]?.["Debt ratio data"]?.["Long term debt ratio"]),
          "Long Term Debt-Equity Ratio": processChartData(rawData?.["Liquidity data"]?.["Debt ratio data"]?.["Long term debt-equity ratio"])
        }
      },
      profitabilityData: {
        title: "Profitability Analysis",
        data: {
          "Profit Margin": processChartData(rawData?.["Profit data"]?.["Profit Margin data"]?.["Profit margin"]),
          "Operating Profit Margin": processChartData(rawData?.["Profit data"]?.["Profit Margin data"]?.["Operating profit margin"]),
          "Return on Assets": processChartData(rawData?.["Profit data"]?.["Return on Asset data"]?.["Return on Asset"]),
          "Return on Equity": processChartData(rawData?.["Profit data"]?.["Return on Equity data"]?.["Return on Equity"]),
          "Return on Capital": processChartData(rawData?.["Profit data"]?.["Return on Capital data"]?.["Return on Capital"]),
          "Internal Growth Rate": processChartData(rawData?.["Profit data"]?.["Growth Rate data"]?.["Internal Growth Rate"]),
          "Sustainable Growth Rate": processChartData(rawData?.["Profit data"]?.["Growth Rate data"]?.["Sustainable Growth Rate"])
        }
      }
    };
  };

  const sections = processFinancialData(financialData);

  if (!sections) {
    return (
      <div className="max-w-7xl mx-auto p-4">
        <Card>
          <CardContent className="p-8">
            <p className="text-center text-gray-600">No financial data available</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-8">
      <h2 className="text-3xl font-bold mb-8">Financial Analysis Dashboard</h2>
      {Object.entries(sections).map(([key, section]) => (
        <DataSection
          key={key}
          title={section.title}
          data={section.data}
        />
      ))}
    </div>
  );
};

export default Financials;