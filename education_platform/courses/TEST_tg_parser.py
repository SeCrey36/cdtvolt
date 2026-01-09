import asyncio
from telethon import TelegramClient

# Токен и данные
api_id = '24517392'  # https://my.telegram.org/auth
api_hash = 'e11c67e5c25e67c572bede0f0a09537b'  # https://my.telegram.org/auth
bot_token = '8511246504:AAH_H953M100Pkf-Yl_7VFXoJz4wgeBOtTU'  # от ботфазера

# Канал, из которого будут получать сообщения
channel_username = '@secreyy36'

async def main():
    async with TelegramClient("session", api_id, api_hash) as client:
        await client.start(bot_token=bot_token)

        channel = await client.get_entity(channel_username)

        async for message in client.iter_messages(channel, limit=10):
            print(f"https://t.me/{channel_username}/{message.id}")

asyncio.run(main())
