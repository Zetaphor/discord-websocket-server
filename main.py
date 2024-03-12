import discord
import os
import json
import asyncio
import re
import websockets
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('DISCORD_TOKEN')
websocket_host = os.getenv('WEBSOCKET_HOST', 'localhost')
websocket_port = os.getenv('WEBSOCKET_PORT', 6789)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

connected_clients = []

async def notify_clients(payload):
    if connected_clients:
        await asyncio.gather(
            *[client.send(json.dumps(payload)) for client in connected_clients]
        )

async def register(websocket):
    connected_clients.append(websocket)

async def unregister(websocket):
    connected_clients.remove(websocket)

async def websocket_server(websocket, path):
    await register(websocket)
    try:
        async for message in websocket:
            pass
    finally:
        await unregister(websocket)

async def replace_mentions_with_usernames(content, guild):
    mention_pattern = re.compile(r'<@!?(\d+)>')

    async def replace_mention(match):
        user_id = int(match.group(1))
        try:
            member = await guild.fetch_member(user_id)
            return '@' + member.display_name
        except:
            return match.group(0)

    async def process_matches():
        tasks = [replace_mention(m) for m in mention_pattern.finditer(content)]
        return [await t for t in asyncio.as_completed(tasks)]

    mentions_replaced = await process_matches()
    for m, r in zip(mention_pattern.finditer(content), mentions_replaced):
        content = content[:m.start()] + r + content[m.end():]

    return content

def get_sticker_url(message):
    if message.stickers:
        return message.stickers[0].url
    return None

def replace_custom_emojis(content):
    custom_emoji_pattern = re.compile(r'<a?:(\w+):(\d+)>')
    emoji_replacements = []
    message_parts = []
    last_pos = 0
    has_emoji = False

    for match in custom_emoji_pattern.finditer(content):
        has_emoji = True
        start, end = match.span()
        emoji_name = match.group(1)
        emoji_url = f'https://cdn.discordapp.com/emojis/{match.group(2)}.{ "gif" if match.group(0).startswith("<a") else "png"}'

        if start > last_pos:
            message_parts.append(content[last_pos:start])

        emoji_replacements.append((start, end, emoji_name, emoji_url))
        message_parts.append(emoji_url)

        last_pos = end

    if last_pos < len(content):
        message_parts.append(content[last_pos:])

    modified_content = ''
    last_end = 0
    for start, end, emoji_name, _ in emoji_replacements:
        modified_content += content[last_end:start] + emoji_name
        last_end = end
    modified_content += content[last_end:]

    return modified_content, message_parts, has_emoji

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    modified_content, message_parts, has_emoji = replace_custom_emojis(message.content)
    modified_content = await replace_mentions_with_usernames(modified_content, message.guild)

    if modified_content.strip() == "":
        return

    payload = {
        "channel_name": message.channel.name,
        "content": modified_content,
        "username": message.author.name,
        "avatar_url": message.author.display_avatar.url,
        "message_parts": message_parts,
        "has_emoji": has_emoji
    }
    await notify_clients(payload)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

async def main():
    websocket_server_ = websockets.serve(websocket_server, websocket_host, websocket_port)
    print(f"Websocket server running on {websocket_host}:{websocket_port}")
    await asyncio.gather(client.start(token), websocket_server_)

asyncio.run(main())
