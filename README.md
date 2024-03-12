# Discord Websocket Server

This project is a Discord bot designed to interface with a websocket server. The bot listens to messages on Discord channels and relays them to connected websocket clients. It supports the custom emoji (animated and static) as well as username mentions.

This project was created for bridging Discord data into [Cables.gl](https://cables.gl).

## Setup

### Requirements

Install the required Pyton packages. This library uses Discord.py to interface with the Discord API.

```bash
pip install -r requirements.txt
```

### Discord Token

Create a .env file in the project root with the following content:

```makefile
DISCORD_TOKEN=your_discord_bot_token
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=6879
```

Replace `your_discord_bot_token` with your actual Discord bot token.

See the Discord.py documentation for setting up a bot account and connecting to a server:

https://discordpy.readthedocs.io/en/stable/discord.html

## Running

Run the bot with `python main.py`.