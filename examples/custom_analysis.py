#!/usr/bin/env python3
"""
Custom Analysis Examples for Advanced Trade Insight Engine

This script demonstrates advanced analysis techniques and custom reporting
capabilities that can be built on top of the core insight engine.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import json
from datetime import datetime, timedelta

# Add src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))


class CustomAnalyzer:
    """Custom analyzer for advanced feedback analysis"""
    
    def __init__(self, data_path=None):
        """Initialize with processed data"""
        if data_path is None:
            data_path = project_root / 'output' / 'processed_feedback_data.csv'
        
        if not data_path.exists():
            raise FileNotFoundError(f"Processed data not found at {data_path}. Run main.py first.")
        
        self.df = pd.read_csv(data_path)
        if 'timestamp' in self.df.columns:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        
        print(f"📊 Loaded {len(self.df)} feedback records for analysis")
    
    def sentiment_trend_analysis(self):
        """Analyze sentiment trends over time"""
        print("\n📈 Sentiment Trend Analysis")
        print("-" * 40)
        
        if 'timestamp' not in self.df.columns:
            print("⚠️  No timestamp data available for trend analysis")
            return
        
        # Group by date and calculate sentiment metrics
        daily_sentiment = self.df.groupby(self.df['timestamp'].dt.date).agg({
            'sentiment': [
                lambda x: (x == 'positive').sum(),
                lambda x: (x == 'negative').sum(),
                lambda x: (x == 'neutral').sum(),
                'count'
            ],
            'impact_score': 'mean'
        }).round(4)
        
        daily_sentiment.columns = ['positive', 'negative', 'neutral', 'total', 'avg_impact']
        
        # Calculate sentiment ratios
        daily_sentiment['positive_ratio'] = daily_sentiment['positive'] / daily_sentiment['total']
        daily_sentiment['negative_ratio'] = daily_sentiment['negative'] / daily_sentiment['total']
        
        print("Daily Sentiment Summary:")
        print(daily_sentiment.head())
        
        # Identify trend patterns
        if len(daily_sentiment) >= 3:
            recent_negative = daily_sentiment['negative_ratio'].tail(3).mean()
            overall_negative = daily_sentiment['negative_ratio'].mean()
            
            if recent_negative > overall_negative * 1.2:
                print("🔴 Alert: Recent increase in negative sentiment detected")
            elif recent_negative < overall_negative * 0.8:
                print("🟢 Positive: Recent improvement in sentiment detected")
            else:
                print("🟡 Stable: Sentiment remains consistent")
        
        return daily_sentiment
    
    def competitive_theme_analysis(self):
        """Analyze themes that might indicate competitive issues"""
        print("\n🏆 Competitive Theme Analysis")
        print("-" * 40)
        
        # Define competitive indicators
        competitive_keywords = [
            'competitor', 'alternative', 'switch', 'better', 'worse',
            'robinhood', 'binance', 'kraken', 'ftx', 'gemini'
        ]
        
        # Find feedback mentioning competitors
        competitive_feedback = self.df[
            self.df['feedback_text'].str.contains('|'.join(competitive_keywords), case=False, na=False)
        ]
        
        if len(competitive_feedback) == 0:
            print("No competitive mentions found in feedback")
            return
        
        print(f"Found {len(competitive_feedback)} items with competitive mentions")
        
        # Analyze competitive themes
        comp_themes = competitive_feedback.groupby('theme').agg({
            'impact_score': ['count', 'mean', 'sum'],
            'sentiment': lambda x: (x == 'negative').sum() / len(x)
        }).round(4)
        
        comp_themes.columns = ['count', 'avg_impact', 'total_impact', 'negative_ratio']
        comp_themes = comp_themes.sort_values('total_impact', ascending=False)
        
        print("\nCompetitive Themes by Impact:")
        print(comp_themes.head())
        
        # Identify high-risk areas
        high_risk = comp_themes[
            (comp_themes['negative_ratio'] > 0.5) & 
            (comp_themes['avg_impact'] > self.df['impact_score'].median())
        ]
        
        if len(high_risk) > 0:
            print("\n⚠️  High-Risk Competitive Areas:")
            for theme, row in high_risk.iterrows():
                print(f"  • {theme}: {row['negative_ratio']:.1%} negative, Impact: {row['avg_impact']:.4f}")
        
        return competitive_feedback
    
    def customer_segment_analysis(self):
        """Analyze feedback by customer segments"""
        print("\n👥 Customer Segment Analysis")
        print("-" * 40)
        
        # Segment by source channel (proxy for customer type)
        segments = {
            'iOS App Store': 'Mobile Users',
            'Google Play Store': 'Mobile Users', 
            'Twitter (X)': 'Social Media Users',
            'Internal Sales Notes': 'Enterprise Customers'
        }
        
        self.df['customer_segment'] = self.df['source_channel'].map(segments)
        
        # Analyze by segment
        segment_analysis = self.df.groupby('customer_segment').agg({
            'impact_score': ['count', 'mean', 'sum'],
            'sentiment': [
                lambda x: (x == 'positive').sum() / len(x),
                lambda x: (x == 'negative').sum() / len(x)
            ]
        }).round(4)
        
        segment_analysis.columns = ['count', 'avg_impact', 'total_impact', 'positive_ratio', 'negative_ratio']
        
        print("Segment Performance:")
        print(segment_analysis)
        
        # Identify segment-specific issues
        print("\n🎯 Segment-Specific Insights:")
        for segment, group in self.df.groupby('customer_segment'):
            top_themes = group.groupby('theme')['impact_score'].sum().sort_values(ascending=False).head(2)
            negative_pct = (group['sentiment'] == 'negative').mean() * 100
            
            print(f"\n{segment}:")
            print(f"  • Negative Sentiment: {negative_pct:.1f}%")
            print(f"  • Top Concerns: {', '.join(top_themes.index)}")
        
        return segment_analysis
    
    def strategic_goal_roi_analysis(self):
        """Analyze ROI potential by strategic goal"""
        print("\n💰 Strategic Goal ROI Analysis")
        print("-" * 40)
        
        # Calculate metrics by strategic goal
        goal_analysis = self.df.groupby('strategic_goal').agg({
            'impact_score': ['count', 'mean', 'sum'],
            'sentiment': [
                lambda x: (x == 'negative').sum(),
                lambda x: (x == 'positive').sum()
            ]
        }).round(4)
        
        goal_analysis.columns = ['feedback_count', 'avg_impact', 'total_impact', 'negative_count', 'positive_count']
        
        # Calculate ROI indicators
        goal_analysis['improvement_potential'] = (
            goal_analysis['negative_count'] * goal_analysis['avg_impact']
        )
        goal_analysis['satisfaction_score'] = (
            goal_analysis['positive_count'] / goal_analysis['feedback_count']
        )
        
        # Rank by improvement potential
        goal_analysis = goal_analysis.sort_values('improvement_potential', ascending=False)
        
        print("Strategic Goal Analysis:")
        print(goal_analysis)
        
        # Recommendations
        print("\n💡 Strategic Recommendations:")
        
        # Highest improvement potential
        top_opportunity = goal_analysis.index[0]
        top_potential = goal_analysis.loc[top_opportunity, 'improvement_potential']
        print(f"  1. Priority Investment: {top_opportunity} (Improvement Potential: {top_potential:.2f})")
        
        # Highest satisfaction but low volume
        high_satisfaction = goal_analysis[goal_analysis['satisfaction_score'] > 0.7]
        if len(high_satisfaction) > 0:
            low_volume_high_sat = high_satisfaction[high_satisfaction['feedback_count'] < goal_analysis['feedback_count'].median()]
            if len(low_volume_high_sat) > 0:
                expand_goal = low_volume_high_sat.index[0]
                print(f"  2. Expansion Opportunity: {expand_goal} (High satisfaction, low volume)")
        
        # Underperforming areas
        low_satisfaction = goal_analysis[goal_analysis['satisfaction_score'] < 0.3]
        if len(low_satisfaction) > 0:
            fix_goal = low_satisfaction.index[0]
            print(f"  3. Urgent Fix Needed: {fix_goal} (Low satisfaction)")
        
        return goal_analysis
    
    def anomaly_detection(self):
        """Detect anomalies in feedback patterns"""
        print("\n🔍 Anomaly Detection")
        print("-" * 40)
        
        # Statistical anomalies in impact scores
        q1 = self.df['impact_score'].quantile(0.25)
        q3 = self.df['impact_score'].quantile(0.75)
        iqr = q3 - q1
        
        # Define outliers
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = self.df[
            (self.df['impact_score'] < lower_bound) | 
            (self.df['impact_score'] > upper_bound)
        ]
        
        print(f"Statistical Outliers: {len(outliers)} items")
        
        if len(outliers) > 0:
            print("\nHigh Impact Outliers:")
            high_outliers = outliers[outliers['impact_score'] > upper_bound].nlargest(3, 'impact_score')
            for _, row in high_outliers.iterrows():
                print(f"  • {row['theme']} ({row['sentiment']}) - Impact: {row['impact_score']:.4f}")
        
        # Theme frequency anomalies
        theme_counts = self.df['theme'].value_counts()
        rare_themes = theme_counts[theme_counts <= 2]
        
        if len(rare_themes) > 0:
            print(f"\nRare Themes ({len(rare_themes)} themes with ≤2 mentions):")
            for theme, count in rare_themes.items():
                avg_impact = self.df[self.df['theme'] == theme]['impact_score'].mean()
                print(f"  • {theme}: {count} mentions, Avg Impact: {avg_impact:.4f}")
        
        # Sentiment-impact mismatches
        positive_high_impact = self.df[
            (self.df['sentiment'] == 'positive') & 
            (self.df['impact_score'] > self.df['impact_score'].quantile(0.8))
        ]
        
        negative_low_impact = self.df[
            (self.df['sentiment'] == 'negative') & 
            (self.df['impact_score'] < self.df['impact_score'].quantile(0.2))
        ]
        
        print(f"\nSentiment-Impact Mismatches:")
        print(f"  • Positive sentiment, high impact: {len(positive_high_impact)} items")
        print(f"  • Negative sentiment, low impact: {len(negative_low_impact)} items")
        
        return {
            'statistical_outliers': outliers,
            'rare_themes': rare_themes,
            'positive_high_impact': positive_high_impact,
            'negative_low_impact': negative_low_impact
        }
    
    def generate_executive_briefing(self):
        """Generate a concise executive briefing"""
        print("\n📋 Executive Briefing")
        print("=" * 50)
        
        # Key metrics
        total_feedback = len(self.df)
        avg_impact = self.df['impact_score'].mean()
        negative_pct = (self.df['sentiment'] == 'negative').mean() * 100
        
        # Top issues
        top_negative_themes = self.df[self.df['sentiment'] == 'negative'].groupby('theme')['impact_score'].sum().sort_values(ascending=False).head(3)
        
        # Top successes
        top_positive_themes = self.df[self.df['sentiment'] == 'positive'].groupby('theme')['impact_score'].sum().sort_values(ascending=False).head(3)
        
        # Strategic alignment
        strategic_distribution = self.df['strategic_goal'].value_counts(normalize=True) * 100
        
        briefing = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'summary': {
                'total_feedback': total_feedback,
                'average_impact_score': round(avg_impact, 4),
                'negative_sentiment_percentage': round(negative_pct, 1),
                'data_sources': self.df['source_channel'].nunique()
            },
            'top_concerns': {theme: round(score, 2) for theme, score in top_negative_themes.items()},
            'top_successes': {theme: round(score, 2) for theme, score in top_positive_themes.items()},
            'strategic_alignment': {goal: round(pct, 1) for goal, pct in strategic_distribution.items()}
        }
        
        # Display briefing
        print(f"📅 Report Date: {briefing['date']}")
        print(f"\n📊 Key Metrics:")
        print(f"  • Total Feedback: {briefing['summary']['total_feedback']:,}")
        print(f"  • Average Impact Score: {briefing['summary']['average_impact_score']}")
        print(f"  • Negative Sentiment: {briefing['summary']['negative_sentiment_percentage']}%")
        print(f"  • Data Sources: {briefing['summary']['data_sources']}")
        
        print(f"\n⚠️  Top 3 Concerns:")
        for i, (theme, score) in enumerate(briefing['top_concerns'].items(), 1):
            print(f"  {i}. {theme} (Impact: {score})")
        
        print(f"\n🎉 Top 3 Successes:")
        for i, (theme, score) in enumerate(briefing['top_successes'].items(), 1):
            print(f"  {i}. {theme} (Impact: {score})")
        
        print(f"\n🎯 Strategic Alignment:")
        for goal, pct in briefing['strategic_alignment'].items():
            print(f"  • {goal}: {pct}%")
        
        # Save briefing as JSON
        output_dir = project_root / 'output'
        briefing_file = output_dir / f"executive_briefing_{briefing['date']}.json"
        
        with open(briefing_file, 'w') as f:
            json.dump(briefing, f, indent=2)
        
        print(f"\n💾 Briefing saved to: {briefing_file}")
        
        return briefing


def main():
    """Run custom analysis examples"""
    print("🔬 Advanced Trade Insight Engine - Custom Analysis")
    print("=" * 60)
    
    try:
        # Initialize analyzer
        analyzer = CustomAnalyzer()
        
        # Run analyses
        print("\n🚀 Running Custom Analyses...")
        
        # 1. Sentiment trends
        analyzer.sentiment_trend_analysis()
        
        # 2. Competitive analysis
        analyzer.competitive_theme_analysis()
        
        # 3. Customer segments
        analyzer.customer_segment_analysis()
        
        # 4. Strategic ROI
        analyzer.strategic_goal_roi_analysis()
        
        # 5. Anomaly detection
        analyzer.anomaly_detection()
        
        # 6. Executive briefing
        analyzer.generate_executive_briefing()
        
        print("\n" + "=" * 60)
        print("✅ Custom analysis completed!")
        print("=" * 60)
        
        print("\n💡 Next Steps:")
        print("  1. Review the executive briefing JSON file")
        print("  2. Use insights to prioritize product improvements")
        print("  3. Set up automated monitoring for key metrics")
        print("  4. Share findings with relevant stakeholders")
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("Please run 'python3 main.py' first to generate processed data.")
    except Exception as e:
        print(f"❌ Error in custom analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()