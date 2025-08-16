#!/usr/bin/env python3
"""
Deployment Script for Advanced Trade Insight Engine

This script helps prepare and deploy the insight engine in different environments.
It handles dependency installation, configuration validation, and system checks.
"""

import sys
import os
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime
import argparse


class DeploymentManager:
    """Manages deployment of the insight engine"""
    
    def __init__(self, target_env='development'):
        self.target_env = target_env
        self.project_root = Path(__file__).parent
        self.deployment_log = []
        
    def log(self, message, level='INFO'):
        """Log deployment messages"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)
    
    def check_python_version(self):
        """Check Python version compatibility"""
        self.log("Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.log(f"❌ Python {version.major}.{version.minor} is not supported. Requires Python 3.8+", 'ERROR')
            return False
        
        self.log(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        self.log("Checking dependencies...")
        
        required_packages = [
            'pandas', 'streamlit', 'fpdf2', 'plotly', 'pytest'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('fpdf2', 'fpdf'))
                self.log(f"✅ {package} is available")
            except ImportError:
                missing_packages.append(package)
                self.log(f"❌ {package} is missing", 'WARNING')
        
        if missing_packages:
            self.log(f"Missing packages: {', '.join(missing_packages)}", 'WARNING')
            return False
        
        self.log("✅ All dependencies are available")
        return True
    
    def install_dependencies(self, force=False):
        """Install required dependencies"""
        self.log("Installing dependencies...")
        
        requirements_file = self.project_root / 'requirements.txt'
        
        if not requirements_file.exists():
            self.log("❌ requirements.txt not found", 'ERROR')
            return False
        
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)]
            if force:
                cmd.append('--force-reinstall')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Dependencies installed successfully")
                return True
            else:
                self.log(f"❌ Failed to install dependencies: {result.stderr}", 'ERROR')
                return False
                
        except Exception as e:
            self.log(f"❌ Error installing dependencies: {e}", 'ERROR')
            return False
    
    def validate_data_directory(self):
        """Validate data directory and files"""
        self.log("Validating data directory...")
        
        data_dir = self.project_root / 'csv_mock_data'
        
        if not data_dir.exists():
            self.log("❌ csv_mock_data directory not found", 'ERROR')
            return False
        
        required_files = [
            'coinbase_advance_apple_reviews.csv',
            'coinbase_advanceGoogle_Play.csv',
            'coinbase_advance_internal_sales_notes.csv',
            'coinbase_advanced_twitter_mentions.csv'
        ]
        
        missing_files = []
        for filename in required_files:
            filepath = data_dir / filename
            if not filepath.exists():
                missing_files.append(filename)
            else:
                # Check file size
                size = filepath.stat().st_size
                if size == 0:
                    self.log(f"⚠️  {filename} is empty", 'WARNING')
                else:
                    self.log(f"✅ {filename} ({size:,} bytes)")
        
        if missing_files:
            self.log(f"❌ Missing data files: {', '.join(missing_files)}", 'ERROR')
            return False
        
        self.log("✅ All required data files are present")
        return True
    
    def setup_output_directory(self):
        """Setup output directory with proper permissions"""
        self.log("Setting up output directory...")
        
        output_dir = self.project_root / 'output'
        
        try:
            output_dir.mkdir(exist_ok=True)
            
            # Test write permissions
            test_file = output_dir / 'deployment_test.tmp'
            test_file.write_text('test')
            test_file.unlink()
            
            self.log("✅ Output directory is ready")
            return True
            
        except Exception as e:
            self.log(f"❌ Cannot setup output directory: {e}", 'ERROR')
            return False
    
    def validate_configuration(self):
        """Validate configuration settings"""
        self.log("Validating configuration...")
        
        try:
            # Import config to check for syntax errors
            sys.path.insert(0, str(self.project_root))
            import config
            
            # Check required configuration sections
            required_configs = [
                'CSV_FILE_PATHS', 'OUTPUT_PATHS', 'NLP_CONFIG', 
                'SOURCE_WEIGHT_CONFIG', 'DASHBOARD_CONFIG'
            ]
            
            for config_name in required_configs:
                if hasattr(config, config_name):
                    self.log(f"✅ {config_name} is configured")
                else:
                    self.log(f"❌ {config_name} is missing", 'WARNING')
            
            # Validate file paths
            for name, path in config.CSV_FILE_PATHS.items():
                if Path(path).exists():
                    self.log(f"✅ {name} path is valid")
                else:
                    self.log(f"⚠️  {name} path not found: {path}", 'WARNING')
            
            self.log("✅ Configuration validation completed")
            return True
            
        except Exception as e:
            self.log(f"❌ Configuration error: {e}", 'ERROR')
            return False
    
    def run_system_tests(self):
        """Run basic system tests"""
        self.log("Running system tests...")
        
        try:
            # Test data loading
            sys.path.insert(0, str(self.project_root / 'src'))
            from data_processing.data_loader import validate_data_directory
            
            is_valid, message = validate_data_directory(str(self.project_root / 'csv_mock_data'))
            
            if is_valid:
                self.log("✅ Data loading test passed")
            else:
                self.log(f"❌ Data loading test failed: {message}", 'ERROR')
                return False
            
            # Test basic imports
            from analysis.scoring_engine import calculate_source_weight
            from reporting.report_generator import generate_report_content
            from dashboard.dashboard import main as dashboard_main
            
            self.log("✅ All module imports successful")
            
            # Test basic functionality
            import pandas as pd
            test_record = pd.Series({'source_channel': 'iOS App Store', 'rating': 4, 'helpful_votes': 10})
            weight = calculate_source_weight(test_record)
            
            if isinstance(weight, (int, float)) and weight > 0:
                self.log("✅ Scoring engine test passed")
            else:
                self.log("❌ Scoring engine test failed", 'ERROR')
                return False
            
            self.log("✅ System tests completed successfully")
            return True
            
        except Exception as e:
            self.log(f"❌ System test error: {e}", 'ERROR')
            return False
    
    def create_deployment_package(self):
        """Create a deployment package"""
        self.log("Creating deployment package...")
        
        package_dir = self.project_root / f'deployment_package_{self.target_env}'
        
        if package_dir.exists():
            shutil.rmtree(package_dir)
        
        package_dir.mkdir()
        
        # Copy essential files
        essential_files = [
            'main.py', 'config.py', 'requirements.txt', 
            'README.md', 'TROUBLESHOOTING.md'
        ]
        
        for filename in essential_files:
            src = self.project_root / filename
            if src.exists():
                shutil.copy2(src, package_dir / filename)
                self.log(f"✅ Copied {filename}")
        
        # Copy directories
        essential_dirs = ['src', 'tests', 'csv_mock_data', 'examples']
        
        for dirname in essential_dirs:
            src_dir = self.project_root / dirname
            if src_dir.exists():
                shutil.copytree(src_dir, package_dir / dirname)
                self.log(f"✅ Copied {dirname}/ directory")
        
        # Create deployment info
        deployment_info = {
            'created_at': datetime.now().isoformat(),
            'target_environment': self.target_env,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'deployment_log': self.deployment_log
        }
        
        with open(package_dir / 'deployment_info.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        # Create deployment script
        deploy_script = f"""#!/bin/bash
# Deployment script for {self.target_env} environment
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo "🚀 Deploying Advanced Trade Insight Engine to {self.target_env}"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create output directory
echo "📁 Setting up directories..."
mkdir -p output

# Run system validation
echo "🔍 Running validation..."
python3 -c "
import sys
sys.path.insert(0, 'src')
from data_processing.data_loader import validate_data_directory
is_valid, msg = validate_data_directory('csv_mock_data')
if is_valid:
    print('✅ Validation passed')
else:
    print(f'❌ Validation failed: {{msg}}')
    sys.exit(1)
"

# Test basic execution
echo "🧪 Testing basic execution..."
python3 main.py --help

echo "✅ Deployment completed successfully!"
echo "💡 Next steps:"
echo "  1. Run: python3 main.py"
echo "  2. Launch dashboard: streamlit run src/dashboard/dashboard.py"
"""
        
        deploy_script_path = package_dir / 'deploy.sh'
        deploy_script_path.write_text(deploy_script)
        deploy_script_path.chmod(0o755)
        
        self.log(f"✅ Deployment package created: {package_dir}")
        return package_dir
    
    def generate_deployment_report(self):
        """Generate deployment report"""
        self.log("Generating deployment report...")
        
        report = {
            'deployment_summary': {
                'timestamp': datetime.now().isoformat(),
                'target_environment': self.target_env,
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'project_root': str(self.project_root)
            },
            'validation_results': {
                'python_compatible': self.check_python_version(),
                'dependencies_available': self.check_dependencies(),
                'data_files_present': self.validate_data_directory(),
                'output_directory_ready': self.setup_output_directory(),
                'configuration_valid': self.validate_configuration(),
                'system_tests_passed': self.run_system_tests()
            },
            'deployment_log': self.deployment_log
        }
        
        # Save report
        report_file = self.project_root / f'deployment_report_{self.target_env}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"✅ Deployment report saved: {report_file}")
        
        # Display summary
        print("\n" + "=" * 60)
        print("📋 DEPLOYMENT SUMMARY")
        print("=" * 60)
        
        all_passed = all(report['validation_results'].values())
        status = "✅ READY FOR DEPLOYMENT" if all_passed else "❌ DEPLOYMENT ISSUES FOUND"
        
        print(f"Status: {status}")
        print(f"Environment: {self.target_env}")
        print(f"Python Version: {report['deployment_summary']['python_version']}")
        
        print("\nValidation Results:")
        for check, result in report['validation_results'].items():
            icon = "✅" if result else "❌"
            print(f"  {icon} {check.replace('_', ' ').title()}")
        
        if not all_passed:
            print("\n⚠️  Please resolve the issues above before deployment")
        else:
            print("\n🎉 System is ready for deployment!")
        
        return report


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='Deploy Advanced Trade Insight Engine')
    parser.add_argument('--env', choices=['development', 'staging', 'production'], 
                       default='development', help='Target environment')
    parser.add_argument('--install-deps', action='store_true', 
                       help='Install dependencies automatically')
    parser.add_argument('--force-install', action='store_true',
                       help='Force reinstall dependencies')
    parser.add_argument('--create-package', action='store_true',
                       help='Create deployment package')
    parser.add_argument('--run-tests', action='store_true',
                       help='Run system tests')
    
    args = parser.parse_args()
    
    print("🚀 Advanced Trade Insight Engine - Deployment Manager")
    print("=" * 60)
    
    # Initialize deployment manager
    deployer = DeploymentManager(args.env)
    
    try:
        # Check Python version
        if not deployer.check_python_version():
            return 1
        
        # Install dependencies if requested
        if args.install_deps:
            if not deployer.install_dependencies(args.force_install):
                return 1
        
        # Check dependencies
        if not deployer.check_dependencies():
            if not args.install_deps:
                deployer.log("💡 Use --install-deps to install missing packages", 'INFO')
                return 1
        
        # Validate environment
        deployer.validate_data_directory()
        deployer.setup_output_directory()
        deployer.validate_configuration()
        
        # Run tests if requested
        if args.run_tests:
            if not deployer.run_system_tests():
                return 1
        
        # Create package if requested
        if args.create_package:
            package_dir = deployer.create_deployment_package()
            deployer.log(f"📦 Package created at: {package_dir}")
        
        # Generate final report
        deployer.generate_deployment_report()
        
        return 0
        
    except KeyboardInterrupt:
        deployer.log("⏹️  Deployment interrupted by user", 'WARNING')
        return 1
    except Exception as e:
        deployer.log(f"❌ Unexpected deployment error: {e}", 'ERROR')
        return 1


if __name__ == "__main__":
    sys.exit(main())