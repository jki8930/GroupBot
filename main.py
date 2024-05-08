import re
import asyncio
from typing import Any
import logging
import os
from dotenv import load_dotenv
from contextlib import suppress
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramBadRequest
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


def parse_time(time_string: str | None) -> datetime | None:
    if not time_string:
        print("Can't parse")
        return None

    match_ = re.match(r"(\d+)([a-z])", time_string.lower().strip())
    current_datetime = datetime.now()

    if match_:
        value, unit = int(match_.group(1)), match_.group(2)

        match unit:
            case "m": time_delta = timedelta(minutes=value)
            case "h": time_delta = timedelta(hours=value)
            case "w": time_delta = timedelta(weeks=value)
            case _: return None
    else:
        return None
        
    new_datetime = current_datetime + time_delta
    print(new_datetime)
    return new_datetime


router = Router()
router.message.filter(F.chat.type == "supergroup", F.from_user.id == 1339062105)


@router.message(Command("ban"))
async def ban(message: Message, bot: Bot, command: CommandObject | None=None) -> Any:
    reply = message.reply_to_message
    if not reply:
        return message.answer(text="🙈 пользователь не найден!")
    
    until_date = parse_time(command.args)
    mention = reply.from_user.first_name

    with suppress(TelegramBadRequest):
        await bot.ban_chat_member(
            chat_id=message.chat.id, 
            user_id=reply.from_user.id, 
            until_date=until_date
        )
        await message.answer(text=f"😂 пользователь <b>{mention}</b> забанен.")


@router.message(Command("mute"))
async def mute(message: Message, bot: Bot, command: CommandObject | None=None) -> Any:
    reply = message.reply_to_message
    if not reply:
        return message.answer(text="🙈 пользователь не найден!")
    
    until_date = parse_time(command.args)
    mention = reply.from_user.first_name

    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id, 
            user_id=reply.from_user.id,
            until_date=until_date,
            permissions=ChatPermissions(cand_send_messages=False)
        )
        await message.answer(text=f"🤐 пользователя <b>{mention}</b> заткнули.")


async def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv(".env")

    bot = Bot(os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(router)

    await bot.delete_webhook(True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")