#!/usr/bin/env python3
"""
IntelliDocs AI - Quick Start
Run this if you're having setup issues or want to start quickly
"""

import os
import sys
import webbrowser
import time

def print_status(message, status="info"):
    colors = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    print(f"{colors.get(status, 'ℹ️')} {message}")

def check_environment():
    """Check if environment is ready"""
    print("🔍 Checking your setup...")
    print("-" * 40)
    
    # Check Python version
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_status(f"Python {version.major}.{version.minor}.{version.micro}", "success")
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Need 3.8+", "error")
        return False
    
    # Check if app.py exists
    if os.path.exists('app.py'):
        print_status("app.py found", "success")
    else:
        print_status("app.py not found", "error")
        return False
    
    # Check if we can import required modules
    required_modules = ['streamlit', 'google.generativeai', 'langchain', 'PyPDF2']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print_status(f"{module} available", "success")
        except ImportError:
            print_status(f"{module} missing", "error")
            missing_modules.append(module)
    
    if missing_modules:
        print("\n" + "="*50)
        print("❌ MISSING DEPENDENCIES")
        print("="*50)
        print("Run this command to install missing packages:")
        print(f"pip install -r requirements.txt")
        return False
    
    # Check .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            if 'GOOGLE_API_KEY=your_google_api_key_here' in content:
                print_status(".env file exists but API key not set", "warning")
                return "api_key_needed"
            elif 'GOOGLE_API_KEY=' in content:
                api_key = content.split('GOOGLE_API_KEY=')[1].split('\n')[0].strip()
                if len(api_key) > 20:  # Basic check for valid API key
                    print_status("API key appears to be set", "success")
                    return True
                else:
                    print_status("API key appears invalid", "warning")
                    return "api_key_needed"
    else:
        print_status(".env file not found", "warning")
        return "env_needed"
    
    return True

def create_env_file():
    """Create .env file with template"""
    env_content = """# Google AI API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# Model Configuration
MODEL_NAME=gemini-2.0-flash-exp
TEMPERATURE=0.3

# File Processing
MAX_FILE_SIZE_MB=50
CHUNK_SIZE=10000
CHUNK_OVERLAP=1000
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print_status(".env file created", "success")

def get_api_key_instructions():
    """Show API key setup instructions"""
    print("\n" + "="*50)
    print("🔑 API KEY SETUP NEEDED")
    print("="*50)
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Click 'Create API Key'")
    print("3. Copy the generated API key")
    print("4. Open the .env file in this folder")
    print("5. Replace 'your_google_api_key_here' with your actual API key")
    print("6. Save the file and run this script again")
    print("\n💡 The API key should look like: AIzaSyD...")

def start_streamlit():
    """Start the Streamlit application"""
    print("\n" + "="*50)
    print("🚀 STARTING INTELLIDOCS AI")
    print("="*50)
    print("Opening in your browser...")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(3)
        try:
            webbrowser.open('http://localhost:8501')
        except:
            pass  # Browser opening might fail, but that's ok
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Streamlit
    try:
        import subprocess
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py', '--server.headless=true'])
    except KeyboardInterrupt:
        print("\n👋 IntelliDocs AI stopped")
    except Exception as e:
        print(f"\n❌ Error starting Streamlit: {e}")
        print("\nTry running manually: streamlit run app.py")

def main():
    print("🧠 IntelliDocs AI - Quick Start")
    print("================================\n")
    
    # Check if everything is ready
    status = check_environment()
    
    if status is True:
        # Everything is ready!
        print("\n" + "="*50)
        print("🎉 READY TO GO!")
        print("="*50)
        start_streamlit()
        
    elif status == "api_key_needed":
        get_api_key_instructions()
        
    elif status == "env_needed":
        create_env_file()
        get_api_key_instructions()
        
    else:
        # Some other issue
        print("\n" + "="*50)
        print("🔧 SETUP HELP")
        print("="*50)
        print("Try these commands:")
        print("1. pip install -r requirements.txt")
        print("2. python quick_start.py")
        print("\nOr run manually:")
        print("streamlit run app.py")

if __name__ == "__main__":
    main()