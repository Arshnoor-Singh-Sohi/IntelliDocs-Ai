#!/usr/bin/env python3
"""
IntelliDocs AI - Simple Run Script
Just run this file to start the application!
"""

import os
import sys
import subprocess
import webbrowser
import time

def check_file_exists(filename, description):
    if not os.path.exists(filename):
        print(f"❌ {description} not found: {filename}")
        return False
    print(f"✅ {description} found")
    return True

def check_api_key():
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
        if 'GOOGLE_API_KEY=your_google_api_key_here' in content:
            print("❌ Please set your GOOGLE_API_KEY in the .env file")
            print("   Get your API key from: https://makersuite.google.com/app/apikey")
            return False
        elif 'GOOGLE_API_KEY=' in content and len(content.split('GOOGLE_API_KEY=')[1].split('\n')[0].strip()) > 10:
            print("✅ API key appears to be set")
            return True
        else:
            print("❌ GOOGLE_API_KEY not properly set in .env file")
            return False

def install_dependencies():
    print("🔄 Installing dependencies...")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def run_streamlit():
    print("🚀 Starting IntelliDocs AI...")
    print("   Opening in your browser...")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:8501')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run Streamlit
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py', '--server.headless=true'])
    except KeyboardInterrupt:
        print("\n👋 IntelliDocs AI stopped")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")

def main():
    print("🧠 IntelliDocs AI - Starting Up")
    print("=" * 40)
    
    # Check if required files exist
    if not check_file_exists('app.py', 'Main application'):
        return
    
    if not check_file_exists('requirements.txt', 'Requirements file'):
        return
    
    # Check API key
    if not check_api_key():
        print("\n💡 To fix this:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Open the .env file")
        print("3. Replace 'your_google_api_key_here' with your actual API key")
        print("4. Run this script again")
        return
    
    # Try to import streamlit
    try:
        import streamlit
        print("✅ Streamlit is available")
    except ImportError:
        print("❌ Streamlit not found, installing dependencies...")
        if not install_dependencies():
            return
    
    # All checks passed, run the app
    print("\n🎉 All checks passed!")
    print("=" * 40)
    run_streamlit()

if __name__ == "__main__":
    main()