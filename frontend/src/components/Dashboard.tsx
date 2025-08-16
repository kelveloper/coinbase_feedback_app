import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useDashboardData, useRefreshData, useDownloadReport, useExportData } from '../hooks/useApi';
import { Loader2, RefreshCw, Download, FileDown, AlertCircle } from 'lucide-react';

export function Dashboard() {
  const { data: dashboardData, isLoading, error, isError } = useDashboardData();
  const refreshMutation = useRefreshData();
  const downloadReportMutation = useDownloadReport();
  const exportDataMutation = useExportData();

  // Handle loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  // Handle error state
  if (isError) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="h-8 w-8 text-destructive mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Failed to Load Dashboard</h2>
          <p className="text-muted-foreground mb-4">
            {error instanceof Error ? error.message : 'An unexpected error occurred'}
          </p>
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  if (!dashboardData) return null;

  const { kpis, theme_rankings, sentiment_distribution, recent_feedback } = dashboardData;

  // Transform sentiment data for chart
  const sentimentChartData = sentiment_distribution.map(item => ({
    name: item.sentiment.charAt(0).toUpperCase() + item.sentiment.slice(1),
    value: item.percentage,
    count: item.count,
    color: item.sentiment === 'positive' ? '#10b981' : 
           item.sentiment === 'negative' ? '#ef4444' : '#6b7280'
  }));

  // Transform theme data for chart
  const themeChartData = theme_rankings.map(item => ({
    theme: item.theme,
    impact: item.impact,
    count: item.count
  }));

  const handleRefresh = async () => {
    try {
      await refreshMutation.mutateAsync();
    } catch (error) {
      console.error('Failed to refresh data:', error);
    }
  };

  const handleDownloadReport = async () => {
    try {
      await downloadReportMutation.mutateAsync();
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  const handleExportData = async () => {
    try {
      await exportDataMutation.mutateAsync();
    } catch (error) {
      console.error('Failed to export data:', error);
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Advanced Trade Insight Engine</h1>
            <p className="text-muted-foreground">
              Customer feedback analysis dashboard for Coinbase Advanced Trading
            </p>
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              onClick={handleExportData}
              disabled={exportDataMutation.isPending}
            >
              {exportDataMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <FileDown className="h-4 w-4 mr-2" />
              )}
              Export CSV
            </Button>
            <Button 
              variant="outline" 
              onClick={handleDownloadReport}
              disabled={downloadReportMutation.isPending}
            >
              {downloadReportMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Download className="h-4 w-4 mr-2" />
              )}
              Download Report
            </Button>
            <Button 
              onClick={handleRefresh}
              disabled={refreshMutation.isPending}
            >
              {refreshMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Refresh Data
            </Button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Feedback Items
              </CardTitle>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                className="h-4 w-4 text-muted-foreground"
              >
                <path d="M12 2v20m8-10H4" />
              </svg>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{kpis.total_items.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                Total feedback records
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Average Sentiment
              </CardTitle>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                className="h-4 w-4 text-muted-foreground"
              >
                <circle cx="12" cy="12" r="10"/>
                <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                <line x1="9" y1="9" x2="9.01" y2="9"/>
                <line x1="15" y1="9" x2="15.01" y2="9"/>
              </svg>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{kpis.average_sentiment}</div>
              <p className="text-xs text-muted-foreground">
                Weighted by impact score
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Top Theme
              </CardTitle>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                className="h-4 w-4 text-muted-foreground"
              >
                <rect width="20" height="14" x="2" y="5" rx="2" />
                <path d="M2 10h20" />
              </svg>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{kpis.top_theme}</div>
              <p className="text-xs text-muted-foreground">
                Highest impact theme
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                High Impact Issues
              </CardTitle>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                className="h-4 w-4 text-muted-foreground"
              >
                <path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{kpis.high_impact_count}</div>
              <p className="text-xs text-muted-foreground">
                Require immediate attention
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Theme Impact Rankings</CardTitle>
              <CardDescription>
                Themes ranked by total impact score
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={themeChartData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="theme" type="category" width={120} />
                    <Tooltip 
                      formatter={(value, name) => [
                        typeof value === 'number' ? value.toFixed(2) : value, 
                        name === 'impact' ? 'Impact Score' : name
                      ]}
                    />
                    <Legend />
                    <Bar dataKey="impact" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Sentiment Distribution</CardTitle>
              <CardDescription>
                Overall sentiment breakdown
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={sentimentChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name} ${value.toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {sentimentChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value}%`, 'Percentage']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Data Table */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Feedback</CardTitle>
            <CardDescription>
              Latest customer feedback with impact scores
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-hidden rounded-md border">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="px-4 py-3 text-left">Source</th>
                    <th className="px-4 py-3 text-left">Theme</th>
                    <th className="px-4 py-3 text-left">Sentiment</th>
                    <th className="px-4 py-3 text-right">Impact Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {recent_feedback.map((item, index) => (
                    <tr key={index}>
                      <td className="px-4 py-3">{item.source}</td>
                      <td className="px-4 py-3">{item.theme}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                          item.sentiment === 'positive' 
                            ? 'bg-green-50 text-green-700' 
                            : item.sentiment === 'negative'
                            ? 'bg-red-50 text-red-700'
                            : 'bg-yellow-50 text-yellow-700'
                        }`}>
                          {item.sentiment.charAt(0).toUpperCase() + item.sentiment.slice(1)}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right font-medium">{item.impact_score.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}