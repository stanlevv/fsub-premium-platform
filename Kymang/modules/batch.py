#Kymang

from hydrogram import filters
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Kymang import bot
from Kymang.config import BOT_ID
from Kymang.modules.data import admin_info, cek_owner
from Kymang.modules.func import encode, get_message_id


@bot.on_message(filters.private & filters.command("batch"))
async def batch(c, m):
    if c.me.id == BOT_ID:
        return
    cek = await cek_owner(c.me.id)
    adm = await admin_info(c.me.id, m.from_user.id)
    for i in cek:
        owner = i["owner"]
        chg = i["channel"]
    if not adm and m.from_user.id != owner:
        return
    while True:
        try:
            first_message = await c.ask(
                m.from_user.id,
                "<b>Silahkan Teruskan Pesan/File Pertama dari Channel Database. (Forward with Qoute)</b>\n\n<b>atau Kirim Link Postingan dari Channel Database</b>",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except BaseException:
            return
        f_msg_id = await get_message_id(c, first_message)
        if f_msg_id:
            break
        await first_message.reply(
            "❌ <b>ERROR</b>\n\n<b>Postingan yang Diforward ini bukan dari Channel Database saya</b>",
            quote=True,
        )
        continue

    while True:
        try:
            second_message = await c.ask(
                m.from_user.id,
                "<b>Silahkan Teruskan Pesan/File Terakhir dari Channel DataBase. (Forward with Qoute)</b>\n\n<b>atau Kirim Link Postingan dari Channel Database</b>",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except BaseException:
            return
        s_msg_id = await get_message_id(c, second_message)
        if s_msg_id:
            break
        await second_message.reply(
            "❌ <b>ERROR</b>\n\n<b>Postingan yang Diforward ini bukan dari Channel Database saya</b>",
            quote=True,
        )
        continue

    string = f"get-{f_msg_id * abs(chg)}-{s_msg_id * abs(chg)}"
    base64_string = encode(string)
    link = f"https://t.me/{c.me.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Bagikan Tautan", url=f"https://telegram.me/share/url?url={link}"
                )
            ]
        ]
    )
    await second_message.reply_text(
        f"<b>Link Sharing File Berhasil Di Buat:</b>\n\n{link}",
        quote=True,
        reply_markup=reply_markup,
    )


@bot.on_message(filters.private & filters.command("genlink"))
async def link_generator(c, m):
    if c.me.id == BOT_ID:
        return
    cek = await cek_owner(c.me.id)
    adm = await admin_info(c.me.id, m.from_user.id)
    for i in cek:
        owner = i["owner"]
        chg = i["channel"]
    if not adm and m.from_user.id != owner:
        return
    while True:
        try:
            channel_message = await c.ask(
                m.from_user.id,
                "<b>Silahkan Teruskan Pesan dari Channel DataBase. (Forward with Qoute)</b>\n\n<b>atau Kirim Link Postingan dari Channel Database</b>",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except BaseException:
            return
        msg_id = await get_message_id(c, channel_message)
        if msg_id:
            break
        await channel_message.reply(
            "❌ <b>ERROR</b>\n\n<b>Postingan yang Diforward ini bukan dari Channel Database saya</b>",
            quote=True,
        )
        continue

    base64_string = encode(f"get-{msg_id * abs(chg)}")
    link = f"https://t.me/{c.me.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Bagikan Tautan", url=f"https://telegram.me/share/url?url={link}"
                )
            ]
        ]
    )
    await channel_message.reply_text(
        f"<b>Link File Sharing Berhasil Di Buat:</b>\n\n{link}",
        quote=True,
        reply_markup=reply_markup,
    )
