#!/usr/bin/env python3
"""
Enhanced Feedback Dashboard Launcher

This script launches the enhanced feedback dashboard that showcases
the unified feedback data from the feedback enhancement system.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    required_packages = ['streamlit', 'plotly', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_data_file():
    """Check if the enhanced feedback data file exists."""
    data_file = Path("output/enriched_feedback_master.csv")
    
    if not data_file.exists():
        print("❌ Enhanced feedback data not found!")
        print(f"Expected file: {data_file}")
        print("\nTo generate the data, run:")
        print("python3 feedback_enhancement_system.py")
        return False
    
    print(f"✅ Enhanced feedback data found: {data_file}")
    return True

def main():
    """Launch the enhanced feedback dashboard."""
    print("🚀 Enhanced Feedback Dashboard Launcher")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check data file
    if not check_data_file():
        sys.exit(1)
    
    # Launch dashboard
    dashboard_path = "src/dashboard/enhanced_feedback_dashboard.py"
    
    if not Path(dashboard_path).exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        sys.exit(1)
    
    print(f"🎯 Launching Enhanced Feedback Dashboard...")
    print(f"📊 Dashboard will open in your browser")
    print(f"🔗 URL: http://localhost:8501")
    print("\nPress Ctrl+C to stop the dashboard")
    print("=" * 50)
    
    try:
        # Launch Streamlit dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path,
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()