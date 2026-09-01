import asyncio
import os

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from hydrogram import Client
from hydrogram.handlers.message_handler import MessageHandler
from hydrogram.handlers.callback_query_handler import CallbackQueryHandler
import logging

from Kymang.config import API_HASH, API_ID, BOT_TOKEN

# config.py sudah raise EnvironmentError jika ada var yang kosong

class Bot(Client):
    __module__ = "hydrogram.client"
    _bot = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Task 2.3: Per-bot Semaphore & Rate Limit (30 msg/sec Telegram Limit)
        self._semaphore = asyncio.Semaphore(10)      # Max 10 concurrent tasks per sub-bot
        self._rate_limiter = asyncio.Semaphore(30)    # Max 30 requests/sec limit

    async def safe_send(self, func, *args, **kwargs):
        """
        Task 2.4: Isolated FloodWait Circuit Breaker.
        Hanya instance sub-bot ini yang sleep jika terkena FloodWait, bot lain tidak terpengaruh.
        """
        from hydrogram.errors import FloodWait
        async with self._semaphore:
            try:
                return await func(*args, **kwargs)
            except FloodWait as e:
                logging.getLogger("Bot").warning(f"[{self.me.username}] FloodWait {e.value}s — Sleeping isolated.")
                await asyncio.sleep(e.value)
                return await func(*args, **kwargs)

    def on_message(self, filters=None):
        def decorator(func):
            for ub in self._bot:
                ub.add_handler(MessageHandler(func, filters))
            return func

        return decorator

    def on_callback_query(self, filters=None):
        def decorator(func):
            for ub in self._bot:
                ub.add_handler(CallbackQueryHandler(func, filters))
            return func

        return decorator

    async def start(self):
        await super().start()
        if self not in self._bot:
            self._bot.append(self)


_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

bot = Bot(
    name="Botsub",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir=_base_dir,
)
