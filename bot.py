"""Discord bot providing VC decision memos."""
from __future__ import annotations

import json
import os
import sys
import ssl
import certifi

import discord
from discord import app_commands
from dotenv import load_dotenv
from openai import OpenAI

from prompts import SYSTEM_PROMPT, format_user_prompt
from weaviate_client import (
    build_context,
    calculate_confidence,
    chunk_text,
    embed_chunks,
    get_client,
    initialize_weaviate,
    query_company,
    upsert_chunks,
)

load_dotenv()

# Validate required environment variables
def validate_environment():
    """Validate that all required environment variables are set."""
    required_vars = ["DISCORD_TOKEN"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    
    print("✅ Environment variables validated")

# Configure SSL context for macOS
def create_ssl_context():
    """Create SSL context that works on macOS."""
    try:
        # Try to create a proper SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        return ssl_context
    except Exception:
        # Fallback: create context without verification (less secure but works)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        print("⚠️  Using unverified SSL context (less secure)")
        return ssl_context

# Configure Discord intents
intents = discord.Intents.default()
intents.message_content = True  # Required for slash commands

# Create client with SSL context
try:
    ssl_context = create_ssl_context()
    connector = discord.http.HTTPSConnector(ssl=ssl_context)
    client = discord.Client(intents=intents, connector=connector)
except Exception:
    # Fallback to default client
    print("⚠️  Using default Discord client (may have SSL issues)")
    client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    try:
        synced = await tree.sync()
        print(f"✅ Logged in as {client.user}")
        print(f"✅ Synced {len(synced)} command(s)")
        
        # Initialize Weaviate schema at startup
        if not initialize_weaviate():
            print("⚠️  Weaviate initialization failed - some commands may not work")
        
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@tree.command(name="test", description="Test if the bot is working")
async def test_command(interaction: discord.Interaction):
    """Simple test command to verify bot functionality."""
    await interaction.response.send_message("✅ Bot is working! Ready to process VC decisions.", ephemeral=True)


@tree.command(name="ingest_company", description="Ingest a company one-pager")
async def ingest_company(interaction: discord.Interaction, name: str, link: str, text: str):
    await interaction.response.defer(thinking=True, ephemeral=True)
    
    try:
        wclient = get_client()
        chunks = chunk_text(text)
        print(f"Created {len(chunks)} chunks for {name}")
        
        vectors = embed_chunks(chunks)
        print(f"Generated embeddings for {len(vectors)} chunks")
        
        chunk_count = upsert_chunks(wclient, name, name, link, chunks, vectors)
        await interaction.followup.send(f"✅ Ingested {chunk_count} chunks for {name}", ephemeral=True)
        wclient.close()
    except Exception as e:
        print(f"❌ Ingestion error: {e}")
        await interaction.followup.send(f"❌ Failed to ingest company: {str(e)}", ephemeral=True)
        try:
            wclient.close()
        except:
            pass


@tree.command(name="vc_decide", description="Generate a VC decision memo")
async def vc_decide(
    interaction: discord.Interaction,
    name: str,
    stage: str,
    check_size: str,
    horizon: str,
):
    await interaction.response.defer(thinking=True)
    
    try:
        wclient = get_client()
        docs = query_company(wclient, name, k=5)
        if not docs:
            await interaction.followup.send("❌ Not enough evidence.")
            return
        
        # Calculate confidence using proper similarity scoring
        avg_similarity, is_confident = calculate_confidence(docs, threshold=0.25)
        if not is_confident:
            await interaction.followup.send(f"❌ Not enough evidence. Confidence: {avg_similarity:.3f} (threshold: 0.25)")
            wclient.close()
            return
        
        context = build_context(docs)
        
        # Generate memo using LLM with fallback
        from llm_client import generate_memo
        memo_content = generate_memo(name, stage, check_size, horizon, context)
        
        try:
            data = json.loads(memo_content)
        except Exception as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Raw LLM response: {memo_content}")
            await interaction.followup.send(f"❌ LLM response parsing error: {str(e)}", ephemeral=True)
            wclient.close()
            return

        embed = discord.Embed(title=f"{name} Memo", color=0x00ff00)
        embed.add_field(name="Verdict", value=data.get("verdict", "-"), inline=False)
        scores = data.get("scores", {})
        score_lines = "\n".join(f"{k}: {v}" for k, v in scores.items())
        embed.add_field(name="Scorecard", value=score_lines or "-", inline=False)
        embed.add_field(name="Pros", value="\n".join(data.get("pros", [])) or "-", inline=False)
        embed.add_field(name="Cons", value="\n".join(data.get("cons", [])) or "-", inline=False)
        embed.add_field(name="Key Metrics", value="\n".join(data.get("key_metrics", [])) or "-", inline=False)
        embed.add_field(name="Biggest Risks", value="\n".join(data.get("biggest_risks", [])) or "-", inline=False)
        embed.add_field(name="Fit for Profile", value=data.get("fit_for_profile", "-"), inline=False)
        sources = [f"[{i+1}] {doc[2]}" for i, doc in enumerate(docs)]
        embed.add_field(name="Sources", value="\n".join(sources) or "-", inline=False)
        embed.set_footer(text=data.get("disclaimer", "This is not investment advice"))
        await interaction.followup.send(embed=embed)
        wclient.close()
        
    except Exception as e:
        print(f"❌ VC decision error: {e}")
        await interaction.followup.send(f"❌ Failed to generate memo: {str(e)}", ephemeral=True)
        try:
            wclient.close()
        except:
            pass


def main() -> None:
    print("🚀 Starting Discord VC Decision Bot...")

    # Validate environment before starting
    validate_environment()
    
    token = os.getenv("DISCORD_TOKEN")
    try:
        client.run(token)
    except discord.LoginFailure:
        print("❌ Invalid Discord token. Please check your DISCORD_TOKEN in .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
