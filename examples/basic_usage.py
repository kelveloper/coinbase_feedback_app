#!/usr/bin/env python3
"""
Basic Usage Example for Advanced Trade Insight Engine

This script demonstrates the most common usage patterns for the insight engine.
Run this script to see how to use the system programmatically.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

def example_1_basic_pipeline():
    """Example 1: Run the complete pipeline programmatically"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Pipeline Execution")
    print("=" * 60)
    
    try:
        # Import main pipeline components
        from data_processing.data_loader import load_all_csv_files
        from data_processing.data_normalizer import normalize_and_unify_data
        from analysis.nlp_models import enrich_dataframe_with_nlp
        from analysis.scoring_engine import enrich_dataframe_with_scores
        
        # Step 1: Load data
        print("📁 Loading CSV data...")
        data_dir = project_root / 'csv_mock_data'
        loaded_data = load_all_csv_files(str(data_dir))
        print(f"✅ Loaded {len(loaded_data)} data sources")
        
        # Step 2: Normalize data
        print("🔄 Normalizing data...")
        normalized_df = normalize_and_unify_data(loaded_data)
        print(f"✅ Normalized {len(normalized_df)} records")
        
        # Step 3: Apply NLP processing
        print("🧠 Applying NLP analysis...")
        enriched_df = enrich_dataframe_with_nlp(normalized_df)
        print(f"✅ Processed {len(enriched_df)} records")
        
        # Step 4: Calculate impact scores
        print("📊 Calculating impact scores...")
        scored_df = enrich_dataframe_with_scores(enriched_df)
        print(f"✅ Scored {len(scored_df)} records")
        
        # Display results
        print("\n📈 Results Summary:")
        print(f"Total Records: {len(scored_df)}")
        print(f"Impact Score Range: {scored_df['impact_score'].min():.4f} - {scored_df['impact_score'].max():.4f}")
        print(f"Average Impact: {scored_df['impact_score'].mean():.4f}")
        
        # Show top 3 highest impact items
        print("\n🔥 Top 3 Highest Impact Items:")
        top_items = scored_df.nlargest(3, 'impact_score')[['theme', 'sentiment', 'impact_score', 'source_channel']]
        for i, (_, row) in enumerate(top_items.iterrows(), 1):
            print(f"  {i}. {row['theme']} ({row['sentiment']}) - Impact: {row['impact_score']:.4f} - Source: {row['source_channel']}")
        
        return scored_df
        
    except Exception as e:
        print(f"❌ Error in basic pipeline: {e}")
        return None


def example_2_custom_analysis():
    """Example 2: Custom analysis of specific themes"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Custom Theme Analysis")
    print("=" * 60)
    
    try:
        # Run basic pipeline first
        df = example_1_basic_pipeline()
        if df is None:
            return
        
        # Analyze by theme
        print("\n🎯 Theme Analysis:")
        theme_analysis = df.groupby('theme').agg({
            'impact_score': ['count', 'mean', 'sum'],
            'sentiment': lambda x: (x == 'negative').sum()
        }).round(4)
        
        theme_analysis.columns = ['Count', 'Avg_Impact', 'Total_Impact', 'Negative_Count']
        theme_analysis = theme_analysis.sort_values('Total_Impact', ascending=False)
        
        print(theme_analysis.head(5))
        
        # Find themes with highest negative sentiment
        print("\n⚠️  Themes with Most Negative Feedback:")
        negative_themes = theme_analysis[theme_analysis['Negative_Count'] > 0].sort_values('Negative_Count', ascending=False)
        for theme, row in negative_themes.head(3).iterrows():
            print(f"  • {theme}: {int(row['Negative_Count'])} negative items (Avg Impact: {row['Avg_Impact']:.4f})")
        
    except Exception as e:
        print(f"❌ Error in custom analysis: {e}")


def example_3_source_comparison():
    """Example 3: Compare feedback across different sources"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Source Channel Comparison")
    print("=" * 60)
    
    try:
        # Load processed data if available, otherwise run pipeline
        output_file = project_root / 'output' / 'processed_feedback_data.csv'
        
        if output_file.exists():
            import pandas as pd
            df = pd.read_csv(output_file)
            print("📁 Loaded existing processed data")
        else:
            print("📁 No processed data found, running pipeline...")
            df = example_1_basic_pipeline()
            if df is None:
                return
        
        # Compare sources
        print("\n📊 Source Channel Comparison:")
        source_analysis = df.groupby('source_channel').agg({
            'impact_score': ['count', 'mean', 'sum'],
            'sentiment': [
                lambda x: (x == 'positive').sum(),
                lambda x: (x == 'negative').sum(),
                lambda x: (x == 'neutral').sum()
            ]
        }).round(4)
        
        source_analysis.columns = ['Count', 'Avg_Impact', 'Total_Impact', 'Positive', 'Negative', 'Neutral']
        
        for source, row in source_analysis.iterrows():
            print(f"\n🔹 {source}:")
            print(f"  Records: {int(row['Count'])}")
            print(f"  Average Impact: {row['Avg_Impact']:.4f}")
            print(f"  Total Impact: {row['Total_Impact']:.2f}")
            print(f"  Sentiment: {int(row['Positive'])} pos, {int(row['Negative'])} neg, {int(row['Neutral'])} neutral")
        
        # Calculate sentiment percentages
        print("\n📈 Sentiment Distribution by Source:")
        for source, group in df.groupby('source_channel'):
            sentiment_pct = group['sentiment'].value_counts(normalize=True) * 100
            print(f"  {source}:")
            for sentiment, pct in sentiment_pct.items():
                print(f"    {sentiment}: {pct:.1f}%")
        
    except Exception as e:
        print(f"❌ Error in source comparison: {e}")


def example_4_generate_custom_report():
    """Example 4: Generate a custom report with specific insights"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Custom Report Generation")
    print("=" * 60)
    
    try:
        # Load or generate data
        output_file = project_root / 'output' / 'processed_feedback_data.csv'
        
        if output_file.exists():
            import pandas as pd
            df = pd.read_csv(output_file)
        else:
            df = example_1_basic_pipeline()
            if df is None:
                return
        
        # Generate custom insights
        print("\n📋 Custom Report: Key Insights")
        print("-" * 40)
        
        # 1. Overall metrics
        total_feedback = len(df)
        avg_impact = df['impact_score'].mean()
        high_impact_threshold = df['impact_score'].quantile(0.8)
        high_impact_count = (df['impact_score'] >= high_impact_threshold).sum()
        
        print(f"📊 Overall Metrics:")
        print(f"  • Total Feedback Items: {total_feedback:,}")
        print(f"  • Average Impact Score: {avg_impact:.4f}")
        print(f"  • High Impact Items (top 20%): {high_impact_count}")
        
        # 2. Strategic goal alignment
        print(f"\n🎯 Strategic Goal Distribution:")
        strategic_dist = df['strategic_goal'].value_counts()
        for goal, count in strategic_dist.items():
            pct = (count / total_feedback) * 100
            avg_impact_goal = df[df['strategic_goal'] == goal]['impact_score'].mean()
            print(f"  • {goal}: {count} items ({pct:.1f}%) - Avg Impact: {avg_impact_goal:.4f}")
        
        # 3. Top concerns (negative sentiment + high impact)
        print(f"\n⚠️  Top Concerns (Negative + High Impact):")
        concerns = df[(df['sentiment'] == 'negative') & (df['impact_score'] >= high_impact_threshold)]
        if len(concerns) > 0:
            concern_themes = concerns.groupby('theme')['impact_score'].agg(['count', 'mean']).sort_values('mean', ascending=False)
            for theme, row in concern_themes.head(3).iterrows():
                print(f"  • {theme}: {int(row['count'])} items, Avg Impact: {row['mean']:.4f}")
        else:
            print("  • No high-impact negative feedback found")
        
        # 4. Success stories (positive sentiment + high impact)
        print(f"\n🎉 Success Stories (Positive + High Impact):")
        successes = df[(df['sentiment'] == 'positive') & (df['impact_score'] >= high_impact_threshold)]
        if len(successes) > 0:
            success_themes = successes.groupby('theme')['impact_score'].agg(['count', 'mean']).sort_values('mean', ascending=False)
            for theme, row in success_themes.head(3).iterrows():
                print(f"  • {theme}: {int(row['count'])} items, Avg Impact: {row['mean']:.4f}")
        else:
            print("  • No high-impact positive feedback found")
        
        # 5. Recommendations
        print(f"\n💡 Recommendations:")
        
        # Find theme with highest negative impact
        negative_impact = df[df['sentiment'] == 'negative'].groupby('theme')['impact_score'].sum().sort_values(ascending=False)
        if len(negative_impact) > 0:
            top_negative_theme = negative_impact.index[0]
            print(f"  • Priority Fix: Address '{top_negative_theme}' (highest negative impact)")
        
        # Find underperforming source
        source_sentiment = df.groupby('source_channel')['sentiment'].apply(lambda x: (x == 'negative').sum() / len(x))
        if len(source_sentiment) > 0:
            worst_source = source_sentiment.idxmax()
            worst_pct = source_sentiment.max() * 100
            print(f"  • Source Focus: Improve '{worst_source}' experience ({worst_pct:.1f}% negative)")
        
        # Find strategic opportunity
        strategic_impact = df.groupby('strategic_goal')['impact_score'].mean().sort_values(ascending=False)
        if len(strategic_impact) > 0:
            top_strategic = strategic_impact.index[0]
            print(f"  • Strategic Opportunity: Leverage '{top_strategic}' alignment (highest avg impact)")
        
    except Exception as e:
        print(f"❌ Error in custom report: {e}")


def example_5_dashboard_data_prep():
    """Example 5: Prepare data for custom dashboard visualizations"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Dashboard Data Preparation")
    print("=" * 60)
    
    try:
        # Load processed data
        output_file = project_root / 'output' / 'processed_feedback_data.csv'
        
        if output_file.exists():
            import pandas as pd
            df = pd.read_csv(output_file)
            print("📁 Loaded processed data for dashboard")
        else:
            print("❌ No processed data found. Run main.py first.")
            return
        
        # Prepare dashboard-ready datasets
        print("\n📊 Preparing Dashboard Datasets:")
        
        # 1. KPI Summary
        kpis = {
            'total_items': len(df),
            'avg_sentiment_score': df['impact_score'].mean(),
            'top_theme': df.groupby('theme')['impact_score'].sum().idxmax(),
            'negative_percentage': (df['sentiment'] == 'negative').mean() * 100,
            'sources_count': df['source_channel'].nunique()
        }
        
        print("  📈 KPI Summary:")
        for key, value in kpis.items():
            if isinstance(value, float):
                print(f"    {key}: {value:.2f}")
            else:
                print(f"    {key}: {value}")
        
        # 2. Time series data (if timestamp available)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            daily_metrics = df.groupby(df['timestamp'].dt.date).agg({
                'impact_score': ['count', 'mean'],
                'sentiment': lambda x: (x == 'negative').sum()
            })
            print(f"  📅 Time Series: {len(daily_metrics)} days of data")
        
        # 3. Chart data
        chart_data = {
            'theme_impact': df.groupby('theme')['impact_score'].sum().sort_values(ascending=False).head(10),
            'source_distribution': df['source_channel'].value_counts(),
            'sentiment_by_source': df.groupby(['source_channel', 'sentiment']).size().unstack(fill_value=0)
        }
        
        print("  📊 Chart Datasets:")
        print(f"    Theme Impact: Top {len(chart_data['theme_impact'])} themes")
        print(f"    Source Distribution: {len(chart_data['source_distribution'])} sources")
        print(f"    Sentiment by Source: {chart_data['sentiment_by_source'].shape[0]} sources x {chart_data['sentiment_by_source'].shape[1]} sentiments")
        
        # 4. Export sample datasets for external tools
        export_dir = project_root / 'output' / 'dashboard_exports'
        export_dir.mkdir(exist_ok=True)
        
        # Export theme summary
        theme_summary = df.groupby('theme').agg({
            'impact_score': ['count', 'mean', 'sum'],
            'sentiment': [lambda x: (x == 'positive').sum(), lambda x: (x == 'negative').sum()]
        }).round(4)
        theme_summary.columns = ['count', 'avg_impact', 'total_impact', 'positive_count', 'negative_count']
        theme_summary.to_csv(export_dir / 'theme_summary.csv')
        
        # Export daily trends (if available)
        if 'timestamp' in df.columns:
            daily_trends = df.groupby(df['timestamp'].dt.date).agg({
                'impact_score': ['count', 'mean'],
                'sentiment': [lambda x: (x == 'positive').sum(), lambda x: (x == 'negative').sum()]
            }).round(4)
            daily_trends.columns = ['daily_count', 'daily_avg_impact', 'daily_positive', 'daily_negative']
            daily_trends.to_csv(export_dir / 'daily_trends.csv')
        
        print(f"\n💾 Exported dashboard datasets to: {export_dir}")
        print("  Files created:")
        for file in export_dir.glob('*.csv'):
            print(f"    • {file.name}")
        
    except Exception as e:
        print(f"❌ Error in dashboard prep: {e}")


def main():
    """Run all examples"""
    print("🚀 Advanced Trade Insight Engine - Usage Examples")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not (project_root / 'csv_mock_data').exists():
        print("❌ Error: csv_mock_data directory not found!")
        print(f"Please run this script from the project root directory: {project_root}")
        return
    
    try:
        # Run all examples
        example_1_basic_pipeline()
        example_2_custom_analysis()
        example_3_source_comparison()
        example_4_generate_custom_report()
        example_5_dashboard_data_prep()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        print("\n💡 Next Steps:")
        print("  1. Run the full pipeline: python3 main.py")
        print("  2. Launch the dashboard: streamlit run src/dashboard/dashboard.py")
        print("  3. Check the output directory for generated reports")
        print("  4. Modify this script to create your own custom analyses")
        
    except KeyboardInterrupt:
        print("\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the troubleshooting guide for help")


if __name__ == "__main__":
    main()