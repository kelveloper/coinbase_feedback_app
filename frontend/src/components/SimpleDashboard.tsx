import React from 'react';

export function SimpleDashboard() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Advanced Trade Insight Engine
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Total Feedback</h3>
            <p className="text-2xl font-bold text-gray-900">Loading...</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Avg Sentiment</h3>
            <p className="text-2xl font-bold text-gray-900">Loading...</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Top Theme</h3>
            <p className="text-2xl font-bold text-gray-900">Loading...</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">High Impact</h3>
            <p className="text-2xl font-bold text-gray-900">Loading...</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold text-gray-900 mb-4">API Test</h2>
          <button 
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            onClick={async () => {
              try {
                const response = await fetch('http://localhost:8000/api/kpis');
                const data = await response.json();
                console.log('API Data:', data);
                alert('Check console for API data!');
              } catch (error) {
                console.error('API Error:', error);
                alert('API Error - check console');
              }
            }}
          >
            Test API Connection
          </button>
        </div>
      </div>
    </div>
  );
}
