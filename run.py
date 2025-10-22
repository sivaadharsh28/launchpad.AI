#!/usr/bin/env python3
"""
LaunchPad.AI Application Runner

This script initializes and runs the LaunchPad.AI career copilot application.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils import setup_logging, get_default_error_message
from config import get_config

def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logging('INFO')
        logger = logging.getLogger(__name__)
        
        logger.info("Starting LaunchPad.AI Career Copilot...")
        
        # Load configuration
        config = get_config()
        if not config.validate_config():
            logger.warning("Some configuration values are missing. Using defaults.")
        
        # Import and run the Gradio app
        from app import demo
        
        logger.info(f"Launching Gradio interface on {config.GRADIO_SERVER_NAME}:{config.GRADIO_SERVER_PORT}")
        
        demo.launch(
            server_name=config.GRADIO_SERVER_NAME,
            server_port=config.GRADIO_SERVER_PORT,
            share=config.GRADIO_SHARE,
            show_error=True,
            show_api=True,
        )
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Please install required dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Application Error: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
