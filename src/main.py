# -*- coding: utf-8 -*-

import asyncio
import os
import uuid
from pathlib import Path

from environs import Env
from pyrogram import Client, filters
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import InputPeerChannel, InputReportReasonSpam

from __version__ import __version__

env = Env()
env.read_env()  # read .env file, if it exists

api_id = env.int('API_ID')
api_hash = env.str('API_HASH')
session_path = Path('session')

print(f"ВЕРСІЯ: {__version__}")


def on_start():
    if session_path.exists():
        with open(session_path) as file:
            session_string = file.read()

            if not session_string:
                os.remove(session_path)
                print("Стара конфігурація видалена")
                print("Перезапустіть програму щоб почати користування")
                exit()

            return Client(session_string, api_id, api_hash)

    else:
        with Client(uuid.uuid4().hex, api_id, api_hash) as tmp_app:
            with open(session_path, 'w') as file:
                session_string = tmp_app.export_session_string()
                file.write(session_string)

        print("Програма сконфігурована")
        print("Перезапустіть програму щоб почати користування")
        exit()


app = on_start()


@app.on_message(filters.command(commands='report') & filters.private)
async def cmd_report(client, message):
    print("Експорт файла з каналами...")
    await client.send_message("me", "Експорт файла з каналами...")

    print("💁‍♂️ Рекомендується відправляти не більше 30-40 скарг в годину")
    await client.send_message("me", "💁‍♂️ Рекомендується відправляти не більше 30-40 скарг в годину")

    with open(Path('ban_channels.txt')) as file:
        ids = list(map(str.strip, file.readlines()))

    length = len(ids)

    for _, i in enumerate(ids, start=1):
        try:
            peer: InputPeerChannel = await client.resolve_peer(i)
            response = await client.send(data=ReportPeer(peer=peer, reason=InputReportReasonSpam(), message="Тероризм"))
            print(f"[{_}/{length}] Канал {i} отримав скаргу, {response}")
            await client.send_message("me", f"[{_}/{length}] Канал {i} отримав скаргу, {response}")

        except Exception as exc:
            print(exc)

        finally:
            await asyncio.sleep(5)  # Спимо щоб не перегружати


app.connect()
app.send_message("me", "Введіть тут команду /report")
print("Введіть на телефоні в особистому чаті команду /report\n"
      "Вам надійшло спеціальне повідомлення в цей чат. Перевірте список чатів.")
app.disconnect()
app.run()
