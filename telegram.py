import configparser
from telethon import TelegramClient
from datetime import datetime

config = configparser.ConfigParser()
config.read(r'c:\Projects\config.ini')
api_id = config['TELEGRAM']['api_id']
api_hash = config['TELEGRAM']['api_hash']
#client = TelegramClient("scbot", api_id, api_hash)

async def send_message():
    async with TelegramClient("scalping bot", api_id, api_hash) as client:
        await client.send_message("me", "안녕하세요! Telethon을 이용한 자동 메시지입니다.")
        await client.send_message("me", "현재 날짜와 시각은 {} 입니다.".format(datetime.now()))

# 실행
if __name__ == "__main__":
    #import asyncio
    await send_message()