# Kymang/modules/billing.py
# PRD v5.0 Modul 12: Telegram Stars (XTR) Billing & Subscription Engine

from datetime import datetime, timezone, timedelta
import logging

from hydrogram import filters
from hydrogram.types import LabeledPrice, Message, PreCheckoutQuery

from Kymang import bot
from Kymang.config import BOT_ID
from Kymang.modules.data import add_timer, mongodb

logger = logging.getLogger("BillingStars")
tx_db = mongodb.billing_transactions


# ─── Command /subscribe untuk Pembayaran Via Telegram Stars (XTR) ─────────────

@bot.on_message(filters.command(["subscribe", "sewa", "perpanjang"]) & filters.private)
async def send_stars_invoice(c, m: Message):
    """
    Kirim invoice pembayaran Telegram Stars (XTR) untuk perpanjang 30 hari.
    """
    if c.me.id != BOT_ID:
        return await m.reply("Fitur sewa/perpanjang hanya tersedia di Master Bot.")

    user_id = m.from_user.id
    payload = f"extend_30d_{user_id}_{int(datetime.now(timezone.utc).timestamp())}"

    try:
        await c.send_invoice(
            chat_id=m.chat.id,
            title="Perpanjang Sub-Bot FSub (30 Hari)",
            description="Masa aktif sub-bot akan diperpanjang 30 hari otomatis setelah pembayaran.",
            payload=payload,
            currency="XTR",  # Currency resmi Telegram Stars
            prices=[LabeledPrice("Akses Sub-Bot 30 Hari", 500)],  # 500 Telegram Stars
            start_parameter="subscribe_fsub",
        )
    except Exception as e:
        logger.error(f"Gagal mengirim invoice Stars: {e}")
        await m.reply(f"❌ **Gagal membuat invoice:** {e}")


# ─── Handler Pre-Checkout Query ────────────────────────────────────────────────

@bot.on_pre_checkout_query()
async def pre_checkout_handler(c, query: PreCheckoutQuery):
    """Validasi pre-checkout dari Telegram sebelum pembayaran dieksekusi."""
    await query.answer(ok=True)


# ─── Handler Successful Payment ──────────────────────────────────────────────

@bot.on_message(filters.successful_payment & filters.private)
async def successful_payment_handler(c, m: Message):
    """
    Di-trigger otomatis setelah user berhasil membayar dengan Telegram Stars.
    Masa aktif otomatis bertambah 30 hari & transaksi dicatat.
    """
    payment_info = m.successful_payment
    charge_id = payment_info.telegram_payment_charge_id
    total_stars = payment_info.total_amount
    payload = payment_info.invoice_payload
    user_id = m.from_user.id

    # Hitung masa aktif baru (30 hari dari sekarang)
    new_expiry_date = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%d-%m-%Y")
    await add_timer(user_id, new_expiry_date)

    # Catat histori transaksi ke database
    await tx_db.insert_one({
        "user_id": user_id,
        "charge_id": charge_id,
        "stars_amount": total_stars,
        "payload": payload,
        "status": "completed",
        "created_at": datetime.now(timezone.utc),
    })

    receipt_msg = (
        f"✅ **Pembayaran Berhasil!**\n\n"
        f"• **Jumlah Stars:** `{total_stars} XTR`\n"
        f"• **ID Transaksi:** `{charge_id}`\n"
        f"• **Masa Aktif Baru:** `{new_expiry_date}`\n\n"
        f"Terima kasih telah memperpanjang layanan sub-bot!"
    )
    await m.reply(receipt_msg)
