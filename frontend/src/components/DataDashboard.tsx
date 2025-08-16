import React, { useState, useEffect } from 'react';

type KPIData = {
  total_items: number;
  average_sentiment: string;
  top_theme: string;
  high_impact_count: number;
};

type FeedbackItem = {
  source: string;
  theme: string;
  sentiment: string;
  impact_score: number;
  content?: string;
};

type ThemeData = {
  theme: string;
  impact: number;
  count: number;
};

export function DataDashboard() {
  const [kpis, setKpis] = useState<KPIData | null>(null);
  const [feedback, setFeedback] = useState<FeedbackItem[]>([]);
  const [themes, setThemes] = useState<ThemeData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch KPIs
        const kpiResponse = await fetch('http://localhost:8000/api/kpis');
        if (kpiResponse.ok) {
          const kpiData = await kpiResponse.json();
          setKpis(kpiData);
        }

        // Fetch recent feedback
        const feedbackResponse = await fetch('http://localhost:8000/api/feedback?limit=10');
        if (feedbackResponse.ok) {
          const feedbackData = await feedbackResponse.json();
          setFeedback(feedbackData);
        }

        // Fetch themes
        const themesResponse = await fetch('http://localhost:8000/api/themes?limit=5');
        if (themesResponse.ok) {
          const themesData = await themesResponse.json();
          setThemes(themesData);
        }

        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const refreshData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/refresh', {
        method: 'POST'
      });
      if (response.ok) {
        window.location.reload(); // Simple refresh for now
      }
    } catch (err) {
      console.error('Failed to refresh data:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your feedback data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error: {error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Advanced Trade Insight Engine
            </h1>
            <p className="text-gray-600">
              Customer feedback analysis from your CSV data
            </p>
          </div>
          <button 
            onClick={refreshData}
            className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg"
          >
            Refresh Data
          </button>
        </div>

        {/* KPI Cards */}
        {kpis && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">Total Feedback</h3>
              <p className="text-2xl font-bold text-gray-900">{kpis.total_items.toLocaleString()}</p>
              <p className="text-xs text-gray-500 mt-1">Records processed</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">Average Sentiment</h3>
              <p className={`text-2xl font-bold ${
                kpis.average_sentiment === 'Positive' ? 'text-green-600' :
                kpis.average_sentiment === 'Negative' ? 'text-red-600' : 'text-yellow-600'
              }`}>
                {kpis.average_sentiment}
              </p>
              <p className="text-xs text-gray-500 mt-1">Weighted by impact</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">Top Theme</h3>
              <p className="text-lg font-bold text-gray-900">{kpis.top_theme}</p>
              <p className="text-xs text-gray-500 mt-1">Highest impact</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">High Impact Issues</h3>
              <p className="text-2xl font-bold text-orange-600">{kpis.high_impact_count}</p>
              <p className="text-xs text-gray-500 mt-1">Need attention</p>
            </div>
          </div>
        )}

        {/* Theme Rankings */}
        {themes.length > 0 && (
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Theme Impact Rankings</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {themes.map((theme, index) => (
                  <div key={theme.theme} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium mr-3 ${
                        index === 0 ? 'bg-red-500' : 
                        index === 1 ? 'bg-orange-500' : 
                        index === 2 ? 'bg-yellow-500' : 'bg-gray-500'
                      }`}>
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{theme.theme}</p>
                        <p className="text-sm text-gray-500">{theme.count} feedback items</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-gray-900">{theme.impact.toFixed(1)}</p>
                      <p className="text-sm text-gray-500">Impact Score</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Recent Feedback Table */}
        {feedback.length > 0 && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Recent High-Impact Feedback</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Source
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Theme
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Sentiment
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Impact Score
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {feedback.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.source}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.theme}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          item.sentiment === 'positive' 
                            ? 'bg-green-100 text-green-800'
                            : item.sentiment === 'negative'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {item.sentiment.charAt(0).toUpperCase() + item.sentiment.slice(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {item.impact_score.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
