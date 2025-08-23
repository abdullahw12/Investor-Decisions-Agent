#!/usr/bin/env python3
"""Test bot startup without running indefinitely."""

import asyncio
import os
import sys
from dotenv import load_dotenv
import discord
from discord import app_commands

async def test_bot_startup():
    """Test that the bot can connect and sync commands."""
    load_dotenv()
    
    token = os.getenv("DISCORD_TOKEN")
    if not token or token == "your_discord_bot_token_here":
        print("❌ No valid Discord token found")
        return False
    
    print("🚀 Testing bot startup...")
    
    # Configure Discord intents
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    
    @tree.command(name="test", description="Test if the bot is working")
    async def test_command(interaction: discord.Interaction):
        await interaction.response.send_message("✅ Bot is working!", ephemeral=True)
    
    @client.event
    async def on_ready():
        try:
            synced = await tree.sync()
            print(f"✅ Logged in as {client.user}")
            print(f"✅ Synced {len(synced)} command(s)")
            print("✅ Bot is ready! You can now use /test command in Discord")
            await client.close()  # Close after successful connection
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")
            await client.close()
    
    try:
        await client.start(token)
        return True
    except discord.LoginFailure:
        print("❌ Invalid Discord token")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_bot_startup())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        sys.exit(0)