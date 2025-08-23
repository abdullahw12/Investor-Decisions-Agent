#!/usr/bin/env python3
"""Start the Discord bot with SSL fixes."""

import os
import sys
import certifi

def setup_ssl():
    """Set up SSL environment variables."""
    cert_path = certifi.where()
    os.environ['SSL_CERT_FILE'] = cert_path
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path

if __name__ == "__main__":
    print("🚀 Starting Discord VC Decision Bot with SSL fixes...")
    
    # Set up SSL
    setup_ssl()
    
    # Import and run the main bot
    from bot import main
    main()