#!/usr/bin/env python3
"""Simple test script to validate Discord bot connection."""

import os
import sys
from dotenv import load_dotenv

def test_discord_connection():
    """Test Discord bot connection and basic functionality."""
    print("🧪 Testing Discord Bot Connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if Discord token is set
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN not found in environment")
        print("Please copy .env.example to .env and add your Discord bot token")
        return False
    
    if token == "your_discord_bot_token_here":
        print("❌ DISCORD_TOKEN is still the example value")
        print("Please update your .env file with a real Discord bot token")
        return False
    
    print("✅ Discord token found")
    
    # Try importing discord.py
    try:
        import discord
        print(f"✅ discord.py version: {discord.__version__}")
    except ImportError:
        print("❌ discord.py not installed")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All Discord connection prerequisites met")
    print("\n🚀 To test the bot:")
    print("1. Run: python bot.py")
    print("2. Check that it logs in successfully")
    print("3. Try the /test command in Discord")
    
    return True

if __name__ == "__main__":
    success = test_discord_connection()
    sys.exit(0 if success else 1)