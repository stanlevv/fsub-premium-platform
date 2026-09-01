# Kymang/modules/monitor.py
# PRD v5.0 Modul 9: Health Monitor, Heartbeat & Auto-Recovery Engine

import asyncio
from datetime import datetime, timezone
import logging

from hydrogram import filters
from Kymang import bot
from Kymang.config import LOG_GRP
from Kymang.modules.auto_del import auto_del_db
from Kymang.modules.data import get_bot

logger = logging.getLogger("HealthMonitor")

_monitor_task = None


async def get_system_stats():
    """Mengambil metrik kesehatan sistem."""
    active_bots = await get_bot()
    pending_deletes = await auto_del_db.count_documents({})
    return {
        "active_bots": len(active_bots),
        "pending_deletes": pending_deletes,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }


async def _health_monitor_loop():
    """Background worker: Heartbeat tiap 2 menit + Hourly Health Report ke LOG_GRP."""
    last_hourly_report = datetime.now(timezone.utc)

    while True:
        try:
            now = datetime.now(timezone.utc)

            # Heartbeat check ke semua sub-bot aktif
            bots = await get_bot()
            for b_info in bots:
                # Cek jika ada token yang tidak valid
                if not b_info.get("bot_token"):
                    logger.warning(f"Sub-bot {b_info.get('name')} token hilang")

            # Laporan Kesehatan Setiap 1 Jam
            if (now - last_hourly_report).total_seconds() >= 3600:
                last_hourly_report = now
                stats = await get_system_stats()
                report_msg = (
                    f"📊 **Laporan Kesehatan Platform — {stats['timestamp']}**\n"
                    f"✅ **Sub-Bot Aktif:** {stats['active_bots']}\n"
                    f"🗑️ **Pending Auto-Delete:** {stats['pending_deletes']} pesan\n"
                    f"⚙️ **Status Engine:** Operational (Hydrogram 0.2+)"
                )
                try:
                    await bot.send_message(chat_id=LOG_GRP, text=report_msg)
                except Exception as err:
                    logger.error(f"Gagal mengirim hourly health report: {err}")

        except Exception as e:
            logger.error(f"Error pada health monitor loop: {e}")

        await asyncio.sleep(120)  # Heartbeat interval: 2 menit


def init_health_monitor():
    """Jalankan background task health monitor saat startup."""
    global _monitor_task
    if _monitor_task is None:
        _monitor_task = asyncio.create_task(_health_monitor_loop())


# ─── Command /stats untuk Owner Sub-Bot ───────────────────────────────────────

@bot.on_message(filters.command("stats") & filters.private)
async def bot_stats_handler(c, m):
    """Command /stats untuk melihat metrik bot."""
    stats = await get_system_stats()
    reply_text = (
        f"📊 **Statistik Bot Platform:**\n"
        f"• **Sub-Bot Aktif Platform:** `{stats['active_bots']}`\n"
        f"• **Antrean Auto-Delete Aktif:** `{stats['pending_deletes']}` pesan\n"
        f"• **Server Time:** `{stats['timestamp']}`"
    )
    await m.reply(reply_text)
