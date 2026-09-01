#Kymang idiot

import asyncio

from hydrogram import filters, Client
from hydrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, UserDeactivatedBan

from Kymang import bot
from Kymang.config import ADMINS, BOT_ID
from Kymang.modules.data import (
    add_admin, add_protect, add_seller, add_sub, admin_info, cek_admin,
    cek_owner, del_admin, del_seller, del_sub, del_user, get_subs,
    get_user, max_info, seller_info, sub_info
)


async def is_authorized(c, m) -> bool:
    if c.me.id == BOT_ID:
        return False
    cek = await cek_owner(c.me.id)
    if not cek:
        return False
    owner = cek[0]["owner"]
    if m.from_user.id == owner:
        return True
    adm = await admin_info(c.me.id, m.from_user.id)
    return bool(adm)


@bot.on_message(filters.command("users"))
async def get_users(c, m):
    if not await is_authorized(c, m):
        return
    msg = await c.send_message(m.chat.id, "**Tunggu Sebentar...**")
    users = await get_user(c.me.id)
    await msg.edit(f"**{len(users)} Pengguna Bot Ini.**")


@bot.on_message(filters.command("buser") & filters.user(ADMINS))
async def get_buser(c, m):
    if c.me.id != BOT_ID:
        return
    msg = await c.send_message(m.chat.id, "Tunggu Sebentar...")
    users = await get_user(c.me.id)
    await msg.edit(f"{len(users)} user")


async def _do_broadcast(c, m, query, pls_wait_text, reply_text):
    if not (reply := m.reply_to_message):
        return await m.reply(reply_text)
    
    total = 0
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0

    pls_wait = await m.reply(pls_wait_text)
    for x in query:
        chat_id = x["user"]
        try:
            await reply.copy(chat_id)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await reply.copy(chat_id)
            successful += 1
        except UserIsBlocked:
            await del_user(c.me.id, chat_id)
            blocked += 1
        except (UserDeactivatedBan, InputUserDeactivated):
            await del_user(c.me.id, chat_id)
            deleted += 1
        except:
            unsuccessful += 1
        total += 1

    status = f"""**Berhasil Mengirim pesan ke:

Berhasil: {successful}
Gagal: {unsuccessful}
Pengguna Diblokir: {blocked}
Akun Dihapus: {deleted}
Total Pengguna: {total}**"""

    return await pls_wait.edit(status)


@bot.on_message(filters.command("broadcast"))
async def send_text(c: Client, m):
    if not await is_authorized(c, m):
        return
    query = await get_user(c.me.id)
    await _do_broadcast(c, m, query, "Tunggu Sebentar...", "`/broadcast [Reply ke pesan]`")


@bot.on_message(filters.private & filters.command("bacot") & filters.user(ADMINS))
async def send_text_master(c, m):
    if c.me.id != BOT_ID:
        return
    query = await get_user(c.me.id)
    await _do_broadcast(c, m, query, "SABAR NGENTOT", "Reply Goblok")


@bot.on_message(filters.command("addadmin"))
async def add_admin_bot(c, m):
    if not await is_authorized(c, m):
        return
    if len(m.command) < 2:
        return await m.reply(
            "Balas pesan pengguna atau berikan user_id/username."
        )
    ids = int(m.command[1])
    adm = await admin_info(c.me.id, ids)
    if not adm:
        await add_admin(int(c.me.id), ids)
        await m.reply(f"User {ids} Berhasil ditambahkan menjadi admin.")
    else:
        await m.reply(f"User {ids} Sudah ada di daftar Admin.")


@bot.on_message(filters.command("deladmin"))
async def del_admin_bot(c, m):
    if c.me.id == BOT_ID:
        return
    cek = await cek_owner(c.me.id)
    for i in cek:
        owner = i["owner"]
    if m.from_user.id != owner:
        return
    if len(m.command) < 2:
        return await m.reply(
            "Balas pesan pengguna atau berikan user_id/username."
        )
    ids = int(m.command[1])
    adm = await admin_info(c.me.id, ids)
    if adm:
        await del_admin(int(c.me.id), ids)
        await m.reply(f"User {ids} Berhasil Dihapus dari daftar Admin.")
    else:
        await m.reply(f"User {ids} Tidak terdaftar di daftar Admin.")


@bot.on_message(filters.command("listadmin"))
async def cek_admin_bot(c, m):
    if c.me.id == BOT_ID:
        return
    cek = await cek_owner(c.me.id)
    for i in cek:
        owner = i["owner"]
    if m.from_user.id != owner:
        return
    msg = "**Daftar Admin**\n\n"
    admins = await cek_admin(c.me.id)
    if admins is False:
        return await m.reply("Belum ada Admin yang terdaftar.")
    for i, ex in enumerate(admins, 1):
        msg += f"{i} › `{ex['admin']}`\n"
    return await m.reply(msg)


@bot.on_message(filters.command("addseller") & filters.user(ADMINS))
async def add_seller_sub(c, m):
    if c.me.id != BOT_ID:
        return
    if len(m.command) < 2:
        return await m.reply(
            "Balas pesan pengguna atau berikan user_id/username."
        )
    ids = m.command[1]
    iya = await seller_info(int(ids))
    if not iya:
        await add_seller(int(ids))
        await m.reply(f"User {ids} Berhasil di tambahkan ke seller")
    else:
        await m.reply(f"User {ids} Sudah menjadi seller")


@bot.on_message(filters.command("delseller") & filters.user(ADMINS))
async def del_seller_sub(c, m):
    if c.me.id != BOT_ID:
        return
    if len(m.command) < 2:
        return await m.reply(
            "Balas pesan pengguna atau berikan user_id/username."
        )
    ids = m.command[1]
    iya = await seller_info(int(ids))
    if iya:
        await del_seller(int(ids))
        await m.reply(f"{ids} Berhasil di hapus dari seller")
    else:
        await m.reply(f"{ids} Bukan bagian dari seller")


@bot.on_message(filters.private & filters.command("protect"))
async def set_protect(c, m):
    if not await is_authorized(c, m):
        return
    if len(m.command) < 2:
        return await m.reply(
            "`/protect [True/False]`"
        )
    jk = m.command[1]
    if jk in ["True", "False"]:
        await add_protect(c.me.id, jk)
        await m.reply(f"Berhasil mengatur protect menjadi {jk}")
    else:
        await m.reply(f"{jk} Format salah, Gunakan `/protect [True/False]`.")


@bot.on_message(filters.command("addbutton"))
async def add_sub_bot(c, m):
    if not await is_authorized(c, m):
        return
    if len(m.command) < 2:
        return await m.reply(
            "Gunakan Format `/addbutton -100xxxx`"
        )
    ids = int(m.command[1])
    adm = await sub_info(c.me.id, ids)
    s = await max_info(c.me.id)
    if len(m.command) == s:
        return await m.reply(f"Batas fsub {s} telah tercapai, Silahkan Hubungi Admin untuk bantuan.")
    if not adm:
        try:
            await c.export_chat_invite_link(ids)
            await add_sub(int(c.me.id), ids)
            await m.reply(f"{ids} Berhasil ditambahkan di Fsub")
        except Exception:
            return await m.reply(f"Maaf saya bukan admin di `{ids}`")
    else:
        await m.reply(f"{adm} Sudah menjadi admin di Fsub `{ids}`")


@bot.on_message(filters.command("delbutton"))
async def del_sub_bot(c, m):
    if not await is_authorized(c, m):
        return
    if len(m.command) < 2:
        return await m.reply(
            "Gunakan format `/delbutton -100xxxx`"
        )
    ids = int(m.command[1])
    adm = await sub_info(c.me.id, ids)
    if adm:
        await del_sub(int(c.me.id), ids)
        await m.reply(f"{ids} Telah di dihapus dari Fsub")
    else:
        await m.reply(f"{ids} Tidak ditemukan di daftar Fsub")


@bot.on_message(filters.command("listbutton"))
async def cek_sub_bot(c, m):
    if not await is_authorized(c, m):
        return
    msg = "**List Fsub / Button**\n\n"
    admins = await get_subs(c.me.id)
    if admins is None:
        return await m.reply("List Kosong")
    for i, ex in enumerate(admins, 1):
        try:
            get = await c.get_chat(ex["sub"])
            text = f"`{get.id}` | {get.title}"
        except Exception:
            continue
        msg += f"{i} › {text}\n"
    return await m.reply(msg)
