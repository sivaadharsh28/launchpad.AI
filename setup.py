#!/usr/bin/env python3
"""
Setup script for LaunchPad.AI
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("🔧 Installing required packages...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Successfully installed all requirements!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_environment():
    """Setup environment file"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        print("📝 Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("⚠️  Please update the .env file with your AWS credentials!")
    elif env_file.exists():
        print("✅ Environment file already exists")
    else:
        print("⚠️  No environment template found")

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        import boto3
        
        # Try to create a session
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials is None:
            print("⚠️  AWS credentials not found!")
            print("Please configure AWS credentials using one of these methods:")
            print("1. AWS CLI: aws configure")
            print("2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
            print("3. IAM roles (if running on EC2)")
            return False
        else:
            print("✅ AWS credentials found")
            return True
            
    except ImportError:
        print("⚠️  boto3 not installed - cannot check AWS credentials")
        return False
    except Exception as e:
        print(f"⚠️  Error checking AWS credentials: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up LaunchPad.AI...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed - could not install requirements")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Check AWS credentials
    check_aws_credentials()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your AWS credentials")
    print("2. Run: python deploy.py (to setup AWS infrastructure)")
    print("3. Run: python run.py (to start the application)")

if __name__ == "__main__":
    main()
