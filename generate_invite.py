#!/usr/bin/env python3
"""Generate Discord bot invite link."""

import os
from dotenv import load_dotenv

def generate_invite_link():
    """Generate an invite link for the Discord bot."""
    load_dotenv()
    
    # Bot ID from the token test
    bot_id = "1408564730074890390"
    
    # Required permissions for the VC agent bot
    permissions = [
        "2048",    # Use Slash Commands
        "2048",    # Send Messages  
        "16384",   # Embed Links
        "65536",   # Read Message History
    ]
    
    # Calculate permission integer (bitwise OR of all permissions)
    # Send Messages (2048) + Use Slash Commands (2048) + Embed Links (16384) + Read Message History (65536)
    permission_int = 2048 + 16384 + 65536  # = 83968
    
    # Generate invite URL
    invite_url = f"https://discord.com/api/oauth2/authorize?client_id={bot_id}&permissions={permission_int}&scope=bot%20applications.commands"
    
    print("🔗 Discord Bot Invite Link:")
    print("=" * 50)
    print(invite_url)
    print("=" * 50)
    print("\n📋 Instructions:")
    print("1. Click the link above (or copy and paste it into your browser)")
    print("2. Select the Discord server you want to add the bot to")
    print("3. Make sure all permissions are checked")
    print("4. Click 'Authorize'")
    print("5. Complete any CAPTCHA if prompted")
    print("\n✅ After inviting the bot:")
    print("- Run: python bot.py")
    print("- Go to your Discord server")
    print("- Type /test and you should see the command appear")
    print("- Run the command to verify the bot is working")

if __name__ == "__main__":
    generate_invite_link()