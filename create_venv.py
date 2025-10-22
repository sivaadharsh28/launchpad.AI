#!/usr/bin/env python3
"""
Virtual Environment Setup Script for LaunchPad.AI
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def create_virtual_environment():
    """Create a virtual environment for the project"""
    venv_path = Path("venv")
    
    print("🔧 Creating virtual environment...")
    
    if venv_path.exists():
        print("⚠️  Virtual environment already exists at 'venv'")
        response = input("Do you want to recreate it? (y/N): ").lower().strip()
        if response != 'y':
            print("✅ Using existing virtual environment")
            return True
        else:
            print("🗑️  Removing existing virtual environment...")
            import shutil
            shutil.rmtree(venv_path)
    
    try:
        # Create virtual environment
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created successfully!")
        
        # Determine activation script path
        if sys.platform == "win32":
            activate_script = venv_path / "Scripts" / "activate"
            pip_path = venv_path / "Scripts" / "pip"
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            activate_script = venv_path / "bin" / "activate"
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"
        
        print(f"📍 Virtual environment created at: {venv_path.absolute()}")
        print(f"🐍 Python executable: {python_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_requirements_in_venv():
    """Install requirements in the virtual environment"""
    venv_path = Path("venv")
    
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
    else:
        pip_path = venv_path / "bin" / "pip"
    
    print("📦 Installing requirements in virtual environment...")
    
    try:
        subprocess.check_call([
            str(pip_path), "install", "-r", "requirements.txt"
        ])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Virtual environment not found at {pip_path}")
        return False

def create_activation_script():
    """Create convenient activation scripts"""
    if sys.platform == "win32":
        # Windows batch file
        script_content = """@echo off
echo 🚀 Activating LaunchPad.AI virtual environment...
call venv\\Scripts\\activate.bat
echo ✅ Virtual environment activated!
echo 📝 To run the app: python run.py
echo 📝 To deploy AWS: python deploy.py
cmd /k
"""
        script_path = Path("activate_venv.bat")
    else:
        # Unix shell script
        script_content = """#!/bin/bash
echo "🚀 Activating LaunchPad.AI virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated!"
echo "📝 To run the app: python run.py"
echo "📝 To deploy AWS: python deploy.py"
exec "$SHELL"
"""
        script_path = Path("activate_venv.sh")
    
    try:
        script_path.write_text(script_content)
        if not sys.platform == "win32":
            os.chmod(script_path, 0o755)
        print(f"✅ Created activation script: {script_path}")
        return True
    except Exception as e:
        print(f"⚠️  Failed to create activation script: {e}")
        return False

def show_usage_instructions():
    """Show instructions for using the virtual environment"""
    print("\n" + "=" * 60)
    print("🎉 Virtual Environment Setup Complete!")
    print("=" * 60)
    
    if sys.platform == "win32":
        print("\n💻 To activate the virtual environment (Windows):")
        print("   Option 1: Double-click 'activate_venv.bat'")
        print("   Option 2: Run 'venv\\Scripts\\activate.bat'")
    else:
        print("\n💻 To activate the virtual environment (macOS/Linux):")
        print("   Option 1: Run './activate_venv.sh'")
        print("   Option 2: Run 'source venv/bin/activate'")
    
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment (see above)")
    print("2. Configure AWS credentials in .env file")
    print("3. Run: python deploy.py")
    print("4. Run: python run.py")
    
    print("\n🔧 Development commands:")
    print("   python run.py          - Start the application")
    print("   python deploy.py       - Deploy AWS infrastructure")
    print("   python setup.py        - Run setup checks")
    print("   deactivate            - Exit virtual environment")

def main():
    """Main setup function"""
    print("🚀 LaunchPad.AI Virtual Environment Setup")
    print("=" * 50)
    
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  You're already in a virtual environment!")
        print("Please deactivate it first with 'deactivate' command")
        return
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Setup failed!")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements_in_venv():
        print("❌ Failed to install requirements!")
        sys.exit(1)
    
    # Create activation script
    create_activation_script()
    
    # Show usage instructions
    show_usage_instructions()

if __name__ == "__main__":
    main()
