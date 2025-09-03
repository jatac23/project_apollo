"""Setup script for Apollo labeling pipeline."""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_output_directory():
    """Create output directory for results."""
    output_dir = Path("output")
    if not output_dir.exists():
        output_dir.mkdir()
        print("✅ Created output directory")
    else:
        print("✅ Output directory already exists")
    return True


def check_google_cloud_setup():
    """Check if Google Cloud is properly configured."""
    print("🔍 Checking Google Cloud configuration...")

    # Check for environment variables
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not project_id:
        print("⚠️  GOOGLE_CLOUD_PROJECT environment variable not set")
        print("   Set it with: export GOOGLE_CLOUD_PROJECT='your-project-id'")
        return False

    if not credentials:
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        print("   Set it with: export GOOGLE_APPLICATION_CREDENTIALS='path/to/service-account.json'")
        return False

    if not os.path.exists(credentials):
        print(f"⚠️  Service account file not found: {credentials}")
        return False

    print(f"✅ Google Cloud Project: {project_id}")
    print(f"✅ Service Account: {credentials}")
    return True


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")
    try:
        result = subprocess.run([sys.executable, "test_pipeline.py"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Some tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Apollo Labeling Pipeline Setup")
    print("=" * 40)

    success = True

    # Check Python version
    if not check_python_version():
        success = False

    # Install dependencies
    if not install_dependencies():
        success = False

    # Create output directory
    if not create_output_directory():
        success = False

    # Check Google Cloud setup
    google_cloud_ok = check_google_cloud_setup()
    if not google_cloud_ok:
        print("\n⚠️  Google Cloud not fully configured")
        print("   You can still run tests, but the full pipeline requires BigQuery access")

    # Run tests
    if not run_tests():
        success = False

    print("\n" + "=" * 40)
    if success and google_cloud_ok:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the pipeline: python main.py")
        print("2. Try examples: python example_usage.py")
    elif success:
        print("✅ Setup completed (Google Cloud configuration needed for full pipeline)")
        print("\nTo complete setup:")
        print("1. Set up Google Cloud credentials")
        print("2. Run: python main.py")
    else:
        print("❌ Setup encountered issues")
        print("Please resolve the errors above and try again")

    return success


if __name__ == "__main__":
    main()
