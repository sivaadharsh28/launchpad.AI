#!/bin/bash
echo "🚀 Activating LaunchPad.AI virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated!"
echo "📝 To run the app: python run.py"
echo "📝 To deploy AWS: python deploy.py"
exec "$SHELL"
