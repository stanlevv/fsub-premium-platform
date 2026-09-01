# Kymang/modules/cache.py
# PRD v5.0 Modul 5: In-Memory TTL Cache Engine

import asyncio
import functools
from cachetools import TTLCache

def async_cached(cache):
    def decorator(func):
        lock = None
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal lock
            if lock is None:
                # Lazy initialization: aman karena asyncio single-threaded 
                # (tidak ada context switch sebelum assignment selesai)
                lock = asyncio.Lock()
            
            # Simplistic hash key for these specific use cases
            key = args
            async with lock:
                if key in cache:
                    return cache[key]
                result = await func(*args, **kwargs)
                cache[key] = result
                return result
        return wrapper
    return decorator


# ─── Cache Buckets ─────────────────────────────────────────────────────────────
# ponytail: 3 bucket saja — cukup untuk beban yang ada sekarang.
_fsub_cache    = TTLCache(maxsize=500, ttl=60)   # Daftar channel FSub per bot
_botconf_cache = TTLCache(maxsize=500, ttl=60)   # Status aktif & config sub-bot
_member_cache  = TTLCache(maxsize=2000, ttl=30)  # Status member user per channel (30s, tidak lebih)


# ─── Cache Helpers ──────────────────────────────────────────────────────────────

@async_cached(_fsub_cache)
async def cached_get_subs(bot_id: int):
    """Get daftar channel FSub untuk bot_id. Cache 60 detik."""
    from Kymang.modules.data import get_subs
    return await get_subs(bot_id)


@async_cached(_botconf_cache)
async def cached_bot_config(bot_id: int):
    """Get konfigurasi & status aktif sub-bot. Cache 60 detik."""
    from Kymang.modules.data import cek_owner
    return await cek_owner(bot_id)


@async_cached(_member_cache)
async def cached_member_status(client, chat_id: int, user_id: int):
    """Cek status member user di channel. Cache 30 detik."""
    from hydrogram.errors import UserNotParticipant
    try:
        member = await client.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status
    except UserNotParticipant:
        return None


def invalidate_bot_cache(bot_id: int):
    """Hapus entry cache saat config bot berubah (dipanggil setelah update DB)."""
    _fsub_cache.pop(bot_id, None)
    _botconf_cache.pop(bot_id, None)
