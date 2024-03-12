import discord
import os
import json
import asyncio
import re
import websockets
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

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

def replace_custom_emojis(content):
    custom_emoji_pattern = re.compile(r'<a?:(\w+):(\d+)>')
    return custom_emoji_pattern.sub(lambda m: f'https://cdn.discordapp.com/emojis/{m.group(2)}.{ "gif" if m.group(0).startswith("<a") else "png"}', content)

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

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    modified_content = replace_custom_emojis(message.content)
    modified_content = await replace_mentions_with_usernames(modified_content, message.guild)

    # sticker_url = get_sticker_url(message)

    if modified_content == "":
        return

    payload = {
        "channel_name": message.channel.name,
        "content": modified_content,
        "username": message.author.name,
        "avatar_url": message.author.display_avatar.url
    }
    await notify_clients(payload)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

async def main():
    websocket_server_ = websockets.serve(websocket_server, 'localhost', 6789)
    await asyncio.gather(client.start(token), websocket_server_)

asyncio.run(main())
