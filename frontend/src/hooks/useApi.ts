import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import type { DashboardData, KPIData, ThemeData, SentimentData, FeedbackItem, DataProcessingResponse } from '../types/api';

// Query keys
export const queryKeys = {
  dashboard: ['dashboard'] as const,
  kpis: ['kpis'] as const,
  themes: ['themes'] as const,
  sentiment: ['sentiment'] as const,
  feedback: ['feedback'] as const,
  health: ['health'] as const,
};

// Dashboard data hook
export function useDashboardData() {
  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: api.getDashboardData,
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    staleTime: 2 * 60 * 1000, // Consider data fresh for 2 minutes
  });
}

// KPIs hook
export function useKPIs() {
  return useQuery({
    queryKey: queryKeys.kpis,
    queryFn: api.getKPIs,
    refetchInterval: 5 * 60 * 1000,
    staleTime: 2 * 60 * 1000,
  });
}

// Themes hook
export function useThemes(limit: number = 10) {
  return useQuery({
    queryKey: [...queryKeys.themes, limit],
    queryFn: () => api.getThemes(limit),
    refetchInterval: 5 * 60 * 1000,
    staleTime: 2 * 60 * 1000,
  });
}

// Sentiment hook
export function useSentiment() {
  return useQuery({
    queryKey: queryKeys.sentiment,
    queryFn: api.getSentiment,
    refetchInterval: 5 * 60 * 1000,
    staleTime: 2 * 60 * 1000,
  });
}

// Feedback hook
export function useFeedback(params?: {
  limit?: number;
  theme?: string;
  sentiment?: string;
  source?: string;
}) {
  return useQuery({
    queryKey: [...queryKeys.feedback, params],
    queryFn: () => api.getFeedback(params),
    refetchInterval: 5 * 60 * 1000,
    staleTime: 2 * 60 * 1000,
  });
}

// Health check hook
export function useHealthCheck() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: api.healthCheck,
    refetchInterval: 30 * 1000, // Check every 30 seconds
    staleTime: 15 * 1000, // Consider fresh for 15 seconds
  });
}

// Refresh data mutation
export function useRefreshData() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.refreshData,
    onSuccess: () => {
      // Invalidate and refetch all data queries
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
      queryClient.invalidateQueries({ queryKey: queryKeys.kpis });
      queryClient.invalidateQueries({ queryKey: queryKeys.themes });
      queryClient.invalidateQueries({ queryKey: queryKeys.sentiment });
      queryClient.invalidateQueries({ queryKey: queryKeys.feedback });
    },
  });
}

// Download report mutation
export function useDownloadReport() {
  return useMutation({
    mutationFn: api.downloadReport,
    onSuccess: (blob) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `insight-report-${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    },
  });
}

// Export data mutation
export function useExportData() {
  return useMutation({
    mutationFn: api.exportData,
    onSuccess: (blob) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `feedback-data-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    },
  });
}
