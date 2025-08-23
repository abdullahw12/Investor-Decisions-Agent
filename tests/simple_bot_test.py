#!/usr/bin/env python3
"""Simple bot test to validate token and basic connection."""

import os
import requests
from dotenv import load_dotenv

def test_discord_token():
    """Test if the Discord token is valid by making a simple API call."""
    load_dotenv()
    
    token = os.getenv("DISCORD_TOKEN")
    if not token or token == "your_discord_bot_token_here":
        print("❌ No valid Discord token found in .env file")
        return False
    
    print("🧪 Testing Discord token validity...")
    
    # Test the token by getting bot user info
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
        
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Token is valid!")
            print(f"✅ Bot name: {bot_info.get('username', 'Unknown')}")
            print(f"✅ Bot ID: {bot_info.get('id', 'Unknown')}")
            return True
        elif response.status_code == 401:
            print("❌ Invalid token - check your DISCORD_TOKEN in .env")
            return False
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

if __name__ == "__main__":
    success = test_discord_token()
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Make sure the bot is invited to your Discord server")
        print("2. Check the bot has proper permissions (Send Messages, Use Slash Commands)")
        print("3. Run: python bot.py")
        print("4. Try /test command in Discord")
    else:
        print("\n❌ Fix the token issue first, then try again")
        print("See discord_setup_guide.md for detailed setup instructions")