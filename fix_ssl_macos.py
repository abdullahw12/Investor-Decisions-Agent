#!/usr/bin/env python3
"""Fix SSL certificate issues on macOS."""

import os
import sys
import subprocess
import ssl
import certifi

def fix_ssl_certificates():
    """Fix SSL certificate issues on macOS."""
    print("🔧 Fixing SSL certificates on macOS...")
    
    # Method 1: Update certificates using the system
    try:
        print("📋 Method 1: Updating system certificates...")
        result = subprocess.run([
            "/Applications/Python 3.12/Install Certificates.command"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ System certificates updated successfully")
            return True
        else:
            print("⚠️  System certificate update not available")
    except Exception as e:
        print(f"⚠️  Method 1 failed: {e}")
    
    # Method 2: Set SSL environment variables
    try:
        print("📋 Method 2: Setting SSL environment variables...")
        cert_path = certifi.where()
        os.environ['SSL_CERT_FILE'] = cert_path
        os.environ['REQUESTS_CA_BUNDLE'] = cert_path
        print(f"✅ SSL_CERT_FILE set to: {cert_path}")
        return True
    except Exception as e:
        print(f"⚠️  Method 2 failed: {e}")
    
    # Method 3: Manual certificate installation
    print("📋 Method 3: Manual steps needed...")
    print("Run these commands in Terminal:")
    print("1. /Applications/Python\\ 3.12/Install\\ Certificates.command")
    print("2. Or: pip install --upgrade certifi")
    print("3. Or: brew install ca-certificates (if you have Homebrew)")
    
    return False

def test_ssl_connection():
    """Test SSL connection to Discord."""
    print("\n🧪 Testing SSL connection to Discord...")
    
    try:
        import requests
        response = requests.get("https://discord.com/api/v10/gateway", timeout=10)
        if response.status_code == 200:
            print("✅ SSL connection to Discord working!")
            return True
        else:
            print(f"⚠️  Discord API returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ SSL connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 macOS SSL Certificate Fix Tool")
    print("=" * 40)
    
    # Fix certificates
    fix_success = fix_ssl_certificates()
    
    # Test connection
    test_success = test_ssl_connection()
    
    if test_success:
        print("\n✅ SSL is working! You can now run:")
        print("   python bot.py")
    else:
        print("\n❌ SSL still not working. Try these manual steps:")
        print("1. Open Terminal")
        print("2. Run: /Applications/Python\\ 3.12/Install\\ Certificates.command")
        print("3. Or try: pip install --upgrade certifi")
        print("4. Then run: python bot.py")
    
    sys.exit(0 if test_success else 1)