# Investor-Decisions-Agent

A Discord-native VC Decision Memo Agent that converts a startup one-pager into a short investment memo with citations.

## Getting Started

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure environment**
   Copy `.env.example` to `.env` and fill in your `DISCORD_TOKEN`, `FRIENDLI_API_KEY` (or `OPENAI_API_KEY`), and Weaviate credentials.
3. **Ingest sample data**
   ```bash
   python ingest.py data/friendliai.txt --name friendliai
   ```
4. **Run the bot**
   ```bash
   python bot.py
   ```

## Discord Commands

- `/ingest_company name:"<Company>" link:"<URL>" text:"<one-pager>"`
- `/vc_decide name:"<Company>" stage:"<Seed|Pre-Seed|A|B>" check_size:"250k" horizon:"5y"`

## Project Structure

- `bot.py` – Discord bot with slash commands.
- `ingest.py` – Offline ingestion script.
- `prompts.py` – Prompt templates.
- `weaviate_client.py` – Weaviate helpers for chunking, embedding, and retrieval.
- `data/` – Example one-pagers.

## Notes

This is boilerplate code intended for demonstration and requires valid API keys and a running Weaviate instance.
