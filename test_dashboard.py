#!/usr/bin/env python3
"""
Simple test script to verify dashboard functionality
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, 'src')

try:
    from data_processing.data_loader import load_all_csv_files
    from data_processing.data_normalizer import normalize_and_unify_data
    from analysis.scoring_engine import enrich_dataframe_with_scores
    
    print("✅ All imports successful")
    
    # Test data loading
    print("🔄 Testing data loading...")
    loaded_data = load_all_csv_files("csv_mock_data")
    
    if loaded_data:
        print(f"✅ Loaded {len(loaded_data)} data sources")
        
        # Test normalization
        print("🔄 Testing data normalization...")
        normalized_df = normalize_and_unify_data(loaded_data)
        print(f"✅ Normalized {len(normalized_df)} records")
        
        # Test scoring
        print("🔄 Testing impact scoring...")
        enriched_df = enrich_dataframe_with_scores(normalized_df)
        print(f"✅ Calculated scores for {len(enriched_df)} records")
        
        print("\n📊 Dashboard is ready to run!")
        print("Run this command to start the dashboard:")
        print("streamlit run src/dashboard/dashboard.py")
        
    else:
        print("❌ No data loaded - check CSV files")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()