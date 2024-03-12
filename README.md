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
SSL_CERT_FILE=./fullchain.pem
SSL_KEY_FILE=./privkey.pem
```

Replace `your_discord_bot_token` with your actual Discord bot token.

See the Discord.py documentation for setting up a bot account and connecting to a server:

https://discordpy.readthedocs.io/en/stable/discord.html

## Running

Run the bot with `python main.py`.

You will need to get an SSL certificate and configure the location of the fullchain and private key in the `.env` file.

You can get a free SSL certificate from LetsEncrypt using the certbot.

## Configuring as a service

To use run the bot as a systemd service, create `etc/systemd/system/discord_server.service` with the following content:

```bash
[Unit]
Description=Discord Bot Service
After=network.target

[Service]
Type=simple
User=<your_username>
WorkingDirectory=/path/to/the/project
ExecStart=/usr/bin/python3 /path/to/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload # Reload systemd
sudo systemctl enable discord_server.service # Enable the service
sudo systemctl start discord_server.service # Start the service
sudo systemctl status discord_server.service # Check the status
sudo journalctl -u discord_server.service # View the logs
sudo systemctl stop discord_server.service # Stop the service
```

## Example output:

The `message_parts` array will contain the message split on any emoji, so that URLs can be easily parsed.

With emoji:

```json
{
    "channel_name": "bot-testing",
    "content": "Forgot to connect facepalm",
    "username": "zetaphor",
    "avatar_url": "https://cdn.discordapp.com/avatars/134317574342180864/dd1c8320d2dc84c52f36e6d913bedcec.png?size=1024",
    "message_parts": [
        "Forgot to connect ",
        "https://cdn.discordapp.com/emojis/1217142444290740325.png"
    ],
    "has_emoji": true
}
```

Without emoji:

```json
{
    "channel_name": "bot-testing",
    "content": "Awesome",
    "username": "zetaphor",
    "avatar_url": "https://cdn.discordapp.com/avatars/134317574342180864/dd1c8320d2dc84c52f36e6d913bedcec.png?size=1024",
    "message_parts": [
        "Awesome"
    ],
    "has_emoji": false
}
```