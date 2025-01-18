import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Dash from './Pages/DashPage';
import StockDash from './Pages/StockDashPage'; // Update the path as necessary

function App() {
  return (
    <Routes>
      {/* Route for the dashboard */}
      <Route path="/" element={<Dash />} />

      {/* Route for stock details with dynamic ticker */}
      <Route path="/:stockTicker" element={<StockDash />} />
    </Routes>
  );
}

export default App;
