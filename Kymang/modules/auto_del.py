# Kymang/modules/auto_del.py
# PRD v5.0 Modul 6: DRM Konten & Batched Auto-Delete Engine

import asyncio
from datetime import datetime, timezone, timedelta
import logging

from hydrogram.errors import FloodWait, RPCError
from Kymang.modules.data import mongodb

# Collection MongoDB untuk queue auto-delete (kebal restart server)
auto_del_db = mongodb.auto_delete_queue
logger = logging.getLogger("AutoDelete")

_sweeper_task = None

async def add_auto_delete(bot_id: int, chat_id: int, message_ids: list[int], delete_after_seconds: int = 600):
    """
    Registrasi list ID pesan ke antrean auto-delete MongoDB TTL.
    Default expiry: 600 detik (10 menit).
    """
    if not message_ids:
        return
    delete_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=delete_after_seconds)
    await auto_del_db.insert_one({
        "bot_id": bot_id,
        "chat_id": chat_id,
        "message_ids": message_ids,
        "delete_at": delete_at,
    })


async def _run_sweeper_loop(client):
    """
    Background worker: Hapus hingga 100 pesan per 1 API call delete_messages().
    Pemeriksaan antrean setiap 10 detik.
    """
    while True:
        try:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            while True:
                # Atomic lock claim (PRD Council Meeting #4) — cegah race condition multi-instance
                item = await auto_del_db.find_one_and_delete({"delete_at": {"$lte": now}})
                if not item:
                    break
                
                chat_id = item["chat_id"]
                msg_ids = item["message_ids"]
                
                # Batch delete 100 pesan per API call (batas API Telegram)
                for i in range(0, len(msg_ids), 100):
                    batch = msg_ids[i:i + 100]
                    try:
                        await client.delete_messages(chat_id=chat_id, message_ids=batch)
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        try:
                            await client.delete_messages(chat_id=chat_id, message_ids=batch)
                        except RPCError:
                            pass
                    except RPCError as err:
                        logger.debug(f"Auto-delete fail for chat {chat_id}: {err}")

        except Exception as e:
            logger.error(f"Error in auto-delete sweeper: {e}")

        await asyncio.sleep(10)


def init_auto_delete_sweeper(client):
    """Jalankan background task sweeper sekali saat bot start."""
    global _sweeper_task
    if _sweeper_task is None:
        _sweeper_task = asyncio.create_task(_run_sweeper_loop(client))
