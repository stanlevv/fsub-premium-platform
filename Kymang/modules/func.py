#Kymang

import asyncio
import base64
import hashlib
import hmac
import re
import time

from hydrogram import enums, filters
from hydrogram.errors import FloodWait, UserNotParticipant

from Kymang.config import BOT_ID, BOT_TOKEN
from Kymang.modules.data import admin_info, cek_owner, get_subs


# ─── Legacy Encoder/Decoder (Base64) — DIPERTAHANKAN untuk Zero Broken Links ──
def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return (base64_bytes.decode("ascii")).strip("=")


def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")


# ─── Dual-Mode Cryptography (PRD v5.0 Modul 2) ────────────────────────────────
def _hmac_key(bot_token: str) -> bytes:
    """Derive HMAC key dari bot token."""
    return hashlib.sha256(bot_token.encode()).digest()


def encode_secure(string: str, bot_token: str = BOT_TOKEN) -> str:
    """
    Encode link baru dengan HMAC-SHA256 signature.
    Format: sec_{timestamp}_{b64_payload}_{hmac}
    """
    ts = str(int(time.time()))
    b64 = base64.urlsafe_b64encode(string.encode()).decode().strip("=")
    payload = f"{ts}_{b64}"
    sig = hmac.new(_hmac_key(bot_token), payload.encode(), hashlib.sha256).hexdigest()[:16]
    return f"sec_{payload}_{sig}"


def decode_payload(payload: str, bot_token: str = BOT_TOKEN) -> str:
    """
    Dual-Mode decoder:
    - Payload diawali 'sec_' → validasi HMAC, decode aman.
    - Payload lain → fallback ke legacy Base64 decoder.
    """
    if payload.startswith("sec_"):
        # Format: sec_{ts}_{b64}_{sig}
        parts = payload[4:].rsplit("_", 1)  # pisah sig di belakang
        if len(parts) != 2:
            raise ValueError("Format payload sec_ tidak valid")
        body, sig = parts
        expected = hmac.new(_hmac_key(bot_token), body.encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(sig, expected):
            raise ValueError("Signature HMAC tidak valid — link mungkin dimanipulasi")
        # body = {ts}_{b64} — ambil bagian b64
        _, b64 = body.split("_", 1)
        return decode(b64)
    else:
        # ponytail: link lama langsung lewat decoder lama — zero broken links
        return decode(payload)


async def is_subscribed(filter, c, m):
    if c.me.id == BOT_ID:
        return True
    for ix in await cek_owner(c.me.id):
        admin = ix["owner"]
    links = [x["sub"] for x in await get_subs(c.me.id)] if await get_subs(c.me.id) else []
    if not links:
        return False
    user_id = m.from_user.id
    adm = await admin_info(c.me.id, user_id)
    if user_id == int(admin):
        return True
    if adm:
        return True
    try:
        for link in links:
            member = await c.get_chat_member(link, user_id)
    except UserNotParticipant:
        return False

    return member.status in [
        enums.ChatMemberStatus.OWNER,
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.MEMBER,
    ]


async def get_messages(c, message_ids):
    messages = []
    total_messages = 0
    db = None
    backup_db = None
    owners = await cek_owner(c.me.id)
    if owners:
        for ix in owners:
            db = ix.get("channel")
            backup_db = ix.get("backup_channel")

    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages : total_messages + 200]
        try:
            msgs = await c.get_messages(db, temb_ids)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await c.get_messages(db, temb_ids)
        except BaseException:
            # Auto-Failover ke Backup Channel jika primary error/banned
            if backup_db:
                try:
                    msgs = await c.get_messages(backup_db, temb_ids)
                except BaseException:
                    msgs = []
            else:
                msgs = []
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages


async def get_message_id(c, m):
    for ix in await cek_owner(c.me.id):
        db = ix["channel"]
    if m.forward_from_chat and m.forward_from_chat.id == db:
        return m.forward_from_message_id
    elif m.forward_from_chat or m.forward_sender_name or not m.text:
        return 0
    else:
        pattern = "https://t.me/(?:c/)?(.*)/(\\d+)"
        matches = re.match(pattern, m.text)
        if not matches:
            return 0
        channel_id = matches[1]
        msg_id = int(matches[2])
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(db):
                return msg_id


subcribe = filters.create(is_subscribed)
