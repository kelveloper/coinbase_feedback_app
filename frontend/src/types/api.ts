// API types
export type KPIData = {
  total_items: number;
  average_sentiment: string;
  top_theme: string;
  high_impact_count: number;
};

export type ThemeData = {
  theme: string;
  impact: number;
  count: number;
};

export type SentimentData = {
  sentiment: string;
  count: number;
  percentage: number;
};

export type FeedbackItem = {
  source: string;
  theme: string;
  sentiment: string;
  impact_score: number;
  content?: string;
};

export type DashboardData = {
  kpis: KPIData;
  theme_rankings: ThemeData[];
  sentiment_distribution: SentimentData[];
  recent_feedback: FeedbackItem[];
};

export type DataProcessingResponse = {
  success: boolean;
  message: string;
  records_processed: number;
  processing_time: number;
};
