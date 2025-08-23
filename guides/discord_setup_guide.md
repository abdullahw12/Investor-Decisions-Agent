# Discord Bot Setup Guide

## Step 1: Create Discord Application

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Give it a name like "VC Decision Agent"
4. Click "Create"

## Step 2: Create Bot User

1. In your application, go to the "Bot" section (left sidebar)
2. Click "Add Bot" or "Create Bot"
3. Under "Token" section, click "Copy" to get your bot token
4. Paste this token in your `.env` file as `DISCORD_TOKEN`

## Step 3: Configure Bot Permissions

### Required Bot Permissions:
- ✅ **Send Messages** - To send responses
- ✅ **Use Slash Commands** - To register and use slash commands
- ✅ **Embed Links** - To send rich embeds with memo data
- ✅ **Read Message History** - For proper interaction handling

### In the Bot section:
1. Under "Privileged Gateway Intents":
   - ✅ Enable "Message Content Intent" (if you want the bot to read message content)
2. Under "Bot Permissions":
   - ✅ Send Messages
   - ✅ Use Slash Commands
   - ✅ Embed Links
   - ✅ Read Message History

## Step 4: Generate Invite Link

1. Go to "OAuth2" → "URL Generator" (left sidebar)
2. Under "Scopes":
   - ✅ Check "bot"
   - ✅ Check "applications.commands"
3. Under "Bot Permissions":
   - ✅ Send Messages
   - ✅ Use Slash Commands
   - ✅ Embed Links
   - ✅ Read Message History
4. Copy the generated URL at the bottom
5. Open this URL in your browser to invite the bot to your server

## Step 5: Add Bot to Your Server

1. Use the invite link from Step 4
2. Select your Discord server
3. Click "Authorize"
4. Complete any CAPTCHA if prompted

## Step 6: Test the Bot

1. Make sure your `.env` file has the correct `DISCORD_TOKEN`
2. Run: `python test_bot_startup.py`
3. If successful, run: `python bot.py`
4. In Discord, try typing `/test` - you should see the command appear
5. Run the command and you should get a "Bot is working!" message

## Troubleshooting

### Bot doesn't appear online:
- Check that the token in `.env` matches the one from the developer portal
- Make sure the bot has been invited to your server
- Verify the bot has proper permissions

### Slash commands don't appear:
- Wait a few minutes after starting the bot (commands can take time to sync)
- Make sure "applications.commands" scope was selected when inviting
- Try restarting the bot

### Permission errors:
- Check that the bot role has the required permissions in your server
- Make sure the bot's role is above any roles it needs to interact with

## Current Token Status
Your current token in `.env` is: `MTQwODU2NDczMDA3NDg5MDM5MA.GDkETI.N6R7vnkELUD8pm36s9Iz_fGCjx-CfFEhfzjxyY`

If this token doesn't work, you may need to:
1. Regenerate the token in the developer portal
2. Update your `.env` file with the new token
3. Re-invite the bot to your server