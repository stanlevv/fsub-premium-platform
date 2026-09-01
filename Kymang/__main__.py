# Kymang Engine Main Entry Point

import asyncio
import importlib
import logging
from sys import version as pyver

from hydrogram import __version__ as hydrover
from hydrogram import idle
from hydrogram.errors import RPCError

from Kymang import Bot, bot
from Kymang.config import LOG_GRP
from Kymang.modules import loadModule
from Kymang.modules.cek_expired import init_expiration_notifier
from Kymang.modules.data import ensure_indexes, get_bot, remove_bot
from Kymang.modules.monitor import init_health_monitor

msg = """
**Berhasil Di Aktifkan**
**Python Version** `{}`
**Hydrogram Version** `{}`
"""


async def main():
    await ensure_indexes()
    init_health_monitor()
    init_expiration_notifier()
    await bot.start()
    
    for bt in await get_bot():
        b = Bot(**bt)
        try:
            await b.start()
            print(f"{b.me.first_name} [Berhasil Diaktifkan]")
        except RPCError:
            await remove_bot(bt["name"])
            logging.getLogger("Info").info(f"✅ {bt['name']} Berhasil Dihapus Dari Database")
    
    for mod in loadModule():
        importlib.reload(importlib.import_module(f"Kymang.modules.{mod}"))
    
    try:
        await bot.send_message(chat_id=LOG_GRP, text=msg.format(pyver.split()[0], hydrover))
    except Exception as e:
        logging.getLogger("Info").warning(f"⚠️ Gagal mengirim pesan log startup ke LOG_GRP ({LOG_GRP}): {e}")
    await idle()


if __name__ == "__main__":
    logging.getLogger("Info").info("JIKA BUTUH BANTUAN SILAHKAN HUBUNGI @OneWatchBokep")
    asyncio.run(main())

