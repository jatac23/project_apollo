#!/usr/bin/env python3
"""
Setup validation script for Apollo blockchain address labeling pipeline.
Run this script to verify your environment is properly configured.
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'google.cloud.bigquery',
        'pandas',
        'numpy',
        'dotenv'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n💡 Install missing packages with: pip install -r requirements.txt")
        return False
    return True


def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Copy .env.example to .env and configure your credentials:")
        print("   cp .env.example .env")
        return False

    print("✅ .env file exists")

    # Check required variables
    required_vars = [
        'GOOGLE_APPLICATION_CREDENTIALS',
        'GOOGLE_CLOUD_PROJECT'
    ]

    missing_vars = []
    with open(env_file) as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)

    if missing_vars:
        print(
            f"❌ Missing required variables in .env: {', '.join(missing_vars)}")
        return False

    print("✅ Required environment variables are set")
    return True


def check_credentials_file():
    """Check if credentials file exists and is readable."""
    try:
        from dotenv import load_dotenv
        load_dotenv()

        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path:
            print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
            return False

        if creds_path == '/path/to/your/service-account-key.json':
            print("❌ GOOGLE_APPLICATION_CREDENTIALS still has placeholder value")
            print("💡 Update .env file with your actual credentials file path")
            return False

        if not os.path.exists(creds_path):
            print(f"❌ Credentials file not found: {creds_path}")
            print("💡 Check the path in your .env file")
            return False

        print(f"✅ Credentials file exists: {creds_path}")
        return True

    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
        return False


def check_project_structure():
    """Check if project structure is intact."""
    required_files = [
        'main.py',
        'config.py',
        'requirements.txt',
        '.env.example',
        'src/labeling_pipeline.py',
        'src/bigquery_client.py',
        'src/models.py',
        'src/labelers/whale.py'
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False

    print("✅ Project structure is intact")
    return True


def main():
    """Run all validation checks."""
    print("🔍 Apollo Setup Validation")
    print("=" * 40)

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Environment File", check_env_file),
        ("Credentials File", check_credentials_file)
    ]

    results = []
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results.append(False)

    print("\n" + "=" * 40)
    if all(results):
        print("🎉 All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run the pipeline: python main.py")
        print("2. Check the output in the 'output/' directory")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nFor detailed setup instructions, see SETUP.md")

    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
