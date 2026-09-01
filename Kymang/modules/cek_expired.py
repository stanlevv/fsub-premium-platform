# Kymang/modules/cek_expired.py
# PRD v5.0 Modul 10: Notifikasi Jatuh Tempo & Graceful Deactivation

import asyncio
from datetime import datetime
import logging

from hydrogram import Client, filters
from hydrogram.types import Message

from Kymang import bot
from Kymang.config import ADMINS, BOT_ID
from Kymang.modules.data import (
    admin_info,
    cek_owner,
    cek_prem,
    del_timer,
    remove_bot,
    seller_info,
    timer_info,
)

logs = logging.getLogger(__name__)
_notif_task = None


@bot.on_message(filters.command(["expired", "info"]))
async def cek_expired(c: Client, m: Message):
    if c.me.id == BOT_ID:
        iya = await seller_info(m.from_user.id)
        if not iya and m.from_user.id not in ADMINS:
            return await m.reply("Kamu Siapa?")
        anu = await cek_prem()
        msg = "**Daftar Bot Fsub Premium**\n\n"
        ang = 0
        for ex in anu:
            try:
                afa = f"`{ex['nama']}` » {ex['aktif']}"
                ang += 1
            except Exception:
                continue
            msg += f"{ang} › {afa}\n"
        await m.reply(msg)
        return

    cek = await cek_owner(c.me.id)
    adm = await admin_info(c.me.id, m.from_user.id)
    owner = None
    if cek:
        for i in cek:
            owner = i.get("owner")
    if not adm and m.from_user.id != owner:
        return await m.reply("Kamu Siapa?")

    av = await timer_info(c.me.id)
    time_str = datetime.now().strftime("%d-%m-%Y")
    if av == time_str:
        await m.reply("⚠️ Masa aktif bot ini telah **HABIS**. Bot akan segera ditutup.")
        await remove_bot(str(c.me.id))
        await del_timer(c.me.id)
    else:
        await c.send_message(
            chat_id=m.chat.id,
            text=f"🤖 **Bot Status:**\n• **Nama:** {c.me.first_name}\n• **ID:** `{c.me.id}`\n• **Expired:** `{av}`",
        )


async def _expiration_check_loop():
    """
    Background Task: Peringatan H-7, H-3, H-1 hari sebelum masa aktif sub-bot habis.
    Dipemeriksa sekali sehari pada pukul 09:00 UTC.
    """
    while True:
        try:
            active_list = await cek_prem()
            now = datetime.now()

            for item in active_list:
                bot_id = item.get("nama")
                date_str = item.get("aktif")
                if not date_str or date_str == "Belum":
                    continue

                try:
                    exp_date = datetime.strptime(date_str, "%d-%m-%Y")
                    days_left = (exp_date - now).days

                    # Cari owner sub-bot
                    owners = await cek_owner(int(bot_id)) if bot_id.isdigit() else None
                    if not owners:
                        continue
                    owner_id = owners[0].get("owner")

                    if days_left == 7:
                        await bot.send_message(
                            chat_id=owner_id,
                            text=f"⚠️ **Pengingat H-7:** Masa aktif bot `{bot_id}` akan habis dalam **7 hari** ({date_str}).\n"
                                 f"Gunakan `/subscribe` untuk memperpanjang via Telegram Stars."
                        )
                    elif days_left == 3:
                        await bot.send_message(
                            chat_id=owner_id,
                            text=f"⏰ **Pengingat H-3:** Masa aktif bot `{bot_id}` tersisa **3 hari** lagi.\n"
                                 f"Segera perpanjang agar bot tidak dimatikan."
                        )
                    elif days_left == 1:
                        await bot.send_message(
                            chat_id=owner_id,
                            text=f"🚨 **PERINGATAN H-1:** Masa aktif bot `{bot_id}` akan **HABIS BESOK** ({date_str}).\n"
                                 f"Lakukan perpanjang sekarang!"
                        )
                except Exception as err:
                    logs.debug(f"Error parse date for bot {bot_id}: {err}")

        except Exception as e:
            logs.error(f"Error in expiration check loop: {e}")

        # Jalankan pemeriksaan setiap 12 jam
        await asyncio.sleep(43200)


def init_expiration_notifier():
    """Jalankan background task pengingat jatuh tempo saat startup."""
    global _notif_task
    if _notif_task is None:
        _notif_task = asyncio.create_task(_expiration_check_loop())
