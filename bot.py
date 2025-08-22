"""Discord bot providing VC decision memos."""
from __future__ import annotations

import json
import os

import discord
from discord import app_commands
from dotenv import load_dotenv
from openai import OpenAI

from prompts import SYSTEM_PROMPT, format_user_prompt
from weaviate_client import (
    build_context,
    chunk_text,
    embed_chunks,
    get_client,
    query_company,
    upsert_chunks,
)

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")


@tree.command(name="ingest_company", description="Ingest a company one-pager")
async def ingest_company(interaction: discord.Interaction, name: str, link: str, text: str):
    await interaction.response.defer(thinking=True, ephemeral=True)
    wclient = get_client()
    chunks = chunk_text(text)
    vectors = embed_chunks(chunks)
    upsert_chunks(wclient, name, name, link, chunks, vectors)
    await interaction.followup.send(f"Ingested {len(chunks)} chunks for {name}", ephemeral=True)


@tree.command(name="vc_decide", description="Generate a VC decision memo")
async def vc_decide(
    interaction: discord.Interaction,
    name: str,
    stage: str,
    check_size: str,
    horizon: str,
):
    await interaction.response.defer(thinking=True)
    wclient = get_client()
    docs = query_company(wclient, name, k=5)
    if not docs:
        await interaction.followup.send("Not enough evidence.")
        return
    avg_top3 = sum(d[1] for d in docs[:3]) / min(3, len(docs))
    if avg_top3 > 0.8:
        await interaction.followup.send("Not enough evidence.")
        return
    context = build_context(docs)
    user_prompt = format_user_prompt(name, stage, check_size, horizon, context)
    api_key = os.getenv("FRIENDLI_API_KEY") or os.getenv("OPENAI_API_KEY")
    llm = OpenAI(api_key=api_key)
    response = llm.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    try:
        data = json.loads(response.choices[0].message.content)
    except Exception:
        await interaction.followup.send("LLM response parsing error", ephemeral=True)
        return

    embed = discord.Embed(title=f"{name} Memo")
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
    embed.set_footer(text=data.get("disclaimer", ""))
    await interaction.followup.send(embed=embed)


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN not set")
    client.run(token)


if __name__ == "__main__":
    main()
