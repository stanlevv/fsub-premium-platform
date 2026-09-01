# Project Guidelines & Agent Constraints (FSub Platform)

## 🚨 MANDATORY FIRST READ (Sebelum Apapun)
> **AI AGENT WAJIB membaca file berikut secara berurutan sebelum menulis satu baris kode:**
>
> 1. 📋 [`COUNCIL_MEETING.md`](file:///c:/Users/diego%20armando/Documents/MATKUL%202025/SEMESTER%203/Pemrograman%20Mobile%20%5BVTI51316%5D/bot%20tele/COUNCIL_MEETING.md) — **Hasil rapat ahli 1 Sep 2026. Berisi temuan kritis dari audit kode aktual, gap implementasi vs PRD, dan aturan tambahan yang MENGIKAT. Dokumen ini LEBIH BARU dari AGENTS.md ini.**
> 2. 📄 [`PRD.md`](file:///c:/Users/diego%20armando/Documents/MATKUL%202025/SEMESTER%203/Pemrograman%20Mobile%20%5BVTI51316%5D/bot%20tele/PRD.md) — Single Source of Truth arsitektur.
> 3. ✅ [`IMPLEMENTATION_CHECKLIST.md`](file:///c:/Users/diego%20armando/Documents/MATKUL%202025/SEMESTER%203/Pemrograman%20Mobile%20%5BVTI51316%5D/bot%20tele/IMPLEMENTATION_CHECKLIST.md) — Status task saat ini.

---

## 📌 Tech Stack & Architecture
- **Language:** Python 3.10+ (Asynchronous asyncio) — **Target: Python 3.12. Jangan gunakan fitur yang deprecated di 3.12+.**
- **Framework:** `hydrogram` >= 0.2.0 (Hydrogram community fork; `pyromod` built-in)
- **Database:** MongoDB via `motor` (Async Motor Driver) — ⚠️ *Deprecated per Mei 2025. Jangan tambah import motor baru. Lihat COUNCIL_MEETING.md #3.*
- **Caching:** `cachetools` (In-Memory TTL Cache)
- **Security:** `cryptography` (AES-256-GCM token encryption via `crypto.py`), HMAC-SHA256 link signing
- **Single Source of Truth:** [`PRD.md`](file:///c:/Users/diego%20armando/Documents/MATKUL%202025/SEMESTER%203/Pemrograman%20Mobile%20%5BVTI51316%5D/bot%20tele/PRD.md) v5.0 + [`COUNCIL_MEETING.md`](file:///c:/Users/diego%20armando/Documents/MATKUL%202025/SEMESTER%203/Pemrograman%20Mobile%20%5BVTI51316%5D/bot%20tele/COUNCIL_MEETING.md) (update terbaru)

---

## ⚡ Execution Rules (Micro-Tasking Protocol)
1. **One Task at a Time:** Edit ONLY the specific file(s) assigned in the current step. Never make unrequested multi-file edits.
2. **Verification Required:** Run syntax compilation check after EVERY edit before claiming complete:
   `python -m py_compile <modified_file.py>`
3. **Non-Deviation:** Never invent new modules, change core variable names, or deviate from PRD.md v5.0 specs.

---

## 📝 Code Conventions (Hydrogram & Async)

### ✅ Correct Patterns:
```python
# Use hydrogram imports exclusively
from hydrogram import Client, filters
from hydrogram.enums import ParseMode
from hydrogram.errors import FloodWait

# ALWAYS use keyword-only arguments for optional parameters
await bot.send_message(
    chat_id=user_id,
    text="Hello",
    parse_mode=ParseMode.HTML,
    disable_web_page_preview=True
)

# Read environment variables strictly without hardcoded fallback secrets
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise EnvironmentError("BOT_TOKEN mandatory in .env")
```

### ❌ Incorrect Patterns:
```python
# DO NOT import pyrogram or pyromod
import pyrogram  # FORBIDDEN
import pyromod   # FORBIDDEN (pyromod is built-in native in Hydrogram >= 0.2.0)

# DO NOT use positional arguments for optional parameters
await bot.send_message(user_id, "Hello", ParseMode.HTML, True)  # FORBIDDEN

# DO NOT hardcode secret fallbacks in source code
BOT_TOKEN = os.environ.get("BOT_TOKEN", "6938657094:AAEy6...")  # FORBIDDEN
```

---

## 🚫 Critical Prohibitions (Do NOT Do)
- **DO NOT** break or remove legacy Base64 decoding in `Kymang/modules/func.py` (Dual-Mode Cryptography is required).
- **DO NOT** create unisolated global loops. Every sub-bot MUST have `asyncio.Semaphore(10)` and per-bot error boundary.
- **DO NOT** hardcode MongoDB connection strings, API hashes, or Telegram Bot Tokens anywhere in `.py` files.
- **DO NOT** commit `.session`, `.env`, or `*.key` files.

---

## 📋 References
- **🚨 Council Meeting (TERBARU):** [`COUNCIL_MEETING.md`](file:///c:/Users/diego%20armando/Documents/MATKUL%202025/SEMESTER%203/Pemrograman%20Mobile%20%5BVTI51316%5D/bot%20tele/COUNCIL_MEETING.md) — Audit kritis 1 Sep 2026. Baca ini PERTAMA.
- **PRD Specification:** [`PRD.md`](file:///c:/Users/diego%20armando/Documents/MATKUL%202025/SEMESTER%203/Pemrograman%20Mobile%20%5BVTI51316%5D/bot%20tele/PRD.md)
- **Task Checklist:** [`IMPLEMENTATION_CHECKLIST.md`](file:///c:/Users/diego%20armando/Documents/MATKUL%202025/SEMESTER%203/Pemrograman%20Mobile%20%5BVTI51316%5D/bot%20tele/IMPLEMENTATION_CHECKLIST.md)
- **Critical Prohibitions juga berlaku dari COUNCIL_MEETING.md:** Jangan `asyncio.get_event_loop()`, jangan plaintext `bot_token`, jangan import `motor` baru.
