#!/usr/bin/env python3
"""
Local development server for AI Image Editor
Run this file to start the application on your local machine
"""

import os
import sys
from pathlib import Path

def main():
    """Start the Flask application for local development"""
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ Loaded environment variables from .env file")
    except ImportError:
        print("! python-dotenv not installed. Using system environment variables.")
    except Exception as e:
        print(f"! Could not load .env file: {e}")
    
    # Check for required environment variables
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("\n❌ ERROR: GEMINI_API_KEY not found!")
        print("Please set up your .env file with your Gemini API key.")
        print("See LOCAL_SETUP.md for instructions.")
        return
    
    print(f"✓ Gemini API key found (length: {len(api_key)})")
    
    # Import and run the Flask app
    try:
        from app import app
        
        print("\n🚀 Starting AI Image Editor...")
        print("📱 Open your browser to: http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop the server")
        print("\n" + "="*50)
        
        # Run the Flask development server
        app.run(
            host='127.0.0.1',  # Local only
            port=5000,
            debug=True,        # Enable debug mode for development
            use_reloader=True  # Auto-reload on code changes
        )
        
    except ImportError as e:
        print(f"\n❌ ERROR: Could not import Flask app: {e}")
        print("Make sure you have installed all dependencies:")
        print("pip install -r requirements-local.txt")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == '__main__':
    main()