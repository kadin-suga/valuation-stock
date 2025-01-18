import React from 'react';
import { useLocation } from 'react-router-dom';

const Description = () => {
  const location = useLocation();
  const { data } = location.state || {};

  // Helper function to format large numbers
  const formatNumber = (num) => {
    if (!num) return 'N/A';
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${num.toLocaleString()}`;
  };

  return (
    <div className="space-y-6 text-gray-800">
      {/* Company Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-semibold mb-3">Company Description</h3>
        <p className="text-gray-600 leading-relaxed">
          {data?.['Information']['description'] || 'No description available'}
        </p>
        <div className='mt-3'>
            <p className="text-sm font-semibold text-gray-500 mb-1">Former Names</p>
            {data?.["Information"]?.["former names"]?.length > 0 ? (
              <ul className="list-disc list-inside text-gray-600">
                {data["Information"]["former names"].map((item, index) => (
                  <li key={index}>{item.name}</li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-600">No former names available</p>
            )}
          </div>
      </div>

      {/* Market Metrics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-semibold mb-4">Market Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Market Cap</p>
            <p className="text-lg font-medium">
              {formatNumber(data?.['Market data']?.['Market Cap'])}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Market Value Added</p>
            <p className="text-lg font-medium">
              {formatNumber(data?.['Market data']?.['Market value added']) || 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Market to Book</p>
            <p className="text-lg font-medium">
              {formatNumber(data?.['Market data']?.['Market to book']) || 'N/A'}
            </p>
          </div>
        </div>
      </div>

      {/* Company Details */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-semibold mb-4">Sector Details</h3>
        <div className="space-y-3">
          <div>
            <p className="text-sm text-gray-500">Sector Description</p>
            <p className="text-gray-600 leading-relaxed">
              {data?.["Information"]['sector description'] || 'No sector description available'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Sector id</p>
            <p className="text-lg font-medium">{data?.["Information"]['sector'] || 'N/A'}</p>
          </div>
          
        </div>
      </div>

      {/* Insider Transactions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-semibold mb-4">Insider Details</h3>
        <div className="space-y-2">
          {data?.["Information"]['insider transaction'] ? (
            <div className="text-gray-600">
              {typeof data["Information"]['insider transaction'] === 'string' 
                ? data["Information"]['insider transaction']
                : `Insider transaction data available`}
                <p className='mt-2 text-gray-600'>Total number of transactions: {data["Information"]['insider transaction']}</p>
            </div>
          ) : (
            <p className="text-gray-500">No insider transaction data available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Description;