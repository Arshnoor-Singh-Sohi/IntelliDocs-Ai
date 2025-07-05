#!/usr/bin/env python3
"""
IntelliDocs AI Setup Script
This script helps you set up the application quickly
"""

import os
import sys
import subprocess

def print_step(step, message):
    print(f"\n{'='*50}")
    print(f"STEP {step}: {message}")
    print('='*50)

def run_command(command, description):
    print(f"\n🔄 {description}...")
    try:
        # Handle both string and list commands properly
        if isinstance(command, str):
            # For simple commands, use shell=True but escape properly
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
        else:
            # For list commands (safer for paths with spaces), don't use shell
            result = subprocess.run(command, capture_output=True, text=True)
            
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def check_python_version():
    print_step(1, "Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print("✅ Python version is compatible")
    return True

def install_dependencies():
    print_step(2, "Installing Dependencies")
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    # Install dependencies using proper command format
    return run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Installing Python packages"
    )

def setup_environment():
    print_step(3, "Setting Up Environment")
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        
        # Check if API key is set
        with open('.env', 'r') as f:
            content = f.read()
            if 'GOOGLE_API_KEY=your_google_api_key_here' in content:
                print("⚠️  Please update your GOOGLE_API_KEY in the .env file")
                print("   Get your API key from: https://makersuite.google.com/app/apikey")
                return False
            elif 'GOOGLE_API_KEY=' in content:
                print("✅ GOOGLE_API_KEY appears to be set")
                return True
    else:
        # Create .env from template
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
        
        print("✅ .env file created")
        print("⚠️  Please update your GOOGLE_API_KEY in the .env file")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        return False
    
    return True

def create_directories():
    print_step(4, "Creating Directories")
    
    directories = ['faiss_index', 'documents', 'logs']
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def test_imports():
    print_step(5, "Testing Dependencies")
    
    required_modules = [
        'streamlit',
        'google.generativeai',
        'langchain',
        'PyPDF2',
        'faiss',
        'dotenv'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Try running: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies imported successfully")
    return True

def main():
    print("🧠 IntelliDocs AI Setup")
    print("========================")
    
    steps_passed = 0
    total_steps = 5
    
    # Step 1: Check Python version
    if check_python_version():
        steps_passed += 1
    else:
        print("\n❌ Setup failed at step 1")
        return
    
    # Step 2: Install dependencies
    if install_dependencies():
        steps_passed += 1
    else:
        print("\n❌ Setup failed at step 2")
        return
    
    # Step 3: Setup environment
    env_ready = setup_environment()
    steps_passed += 1
    
    # Step 4: Create directories
    if create_directories():
        steps_passed += 1
    else:
        print("\n❌ Setup failed at step 4")
        return
    
    # Step 5: Test imports
    if test_imports():
        steps_passed += 1
    else:
        print("\n❌ Setup failed at step 5")
        return
    
    # Final status
    print(f"\n{'='*50}")
    print("SETUP COMPLETE")
    print('='*50)
    
    print(f"✅ {steps_passed}/{total_steps} steps completed successfully")
    
    if env_ready:
        print("\n🚀 Ready to run!")
        print("Execute: streamlit run app.py")
    else:
        print("\n⚠️  Almost ready!")
        print("1. Edit the .env file and add your GOOGLE_API_KEY")
        print("2. Then run: streamlit run app.py")
    
    print("\n📚 Need help?")
    print("- Get API key: https://makersuite.google.com/app/apikey")
    print("- Documentation: README.md")

if __name__ == "__main__":
    main()