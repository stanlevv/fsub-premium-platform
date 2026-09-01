# Implementation Checklist (PRD v5.0)

> **Instruksi Eksekusi:** Kerjakan 1 modul per langkah. Berikan tanda `[x]` setelah setiap modul selesai dan lulus verifikasi sintaks/smoke test.

---

## 🔴 Fase 1: Fondasi, Migrasi Library & Keamanan Inti
- [x] **Task 1.0: Migrasi Library ke Hydrogram**
  - Ganti semua import `pyrogram` → `hydrogram` di seluruh modul (`Kymang/*.py`, `Kymang/modules/*.py`).
  - Hapus import `pyromod` (karena sudah native di Hydrogram).
  - Pastikan semua argumen opsional menggunakan *keyword arguments*.
- [x] **Task 1.1: Sanitasi Kredensial & Server Hardening**
  - Hapus semua hardcode fallback di `Kymang/config.py`.
  - Buat/update `.gitignore` untuk melindungi `.env`, `*.session`, dan file sensitif.
  - Buat template `.env.example` yang bersih.
- [x] **Task 1.2: MongoDB Connection Pooling Global**
  - Refactor `Kymang/modules/data.py` agar menggunakan single global connection pool (`maxPoolSize=20`, `minPoolSize=5`).
  - Tambahkan fungsi auto-create compound index saat startup.
- [x] **Task 1.3: In-Memory TTL Cache Engine**
  - Buat file baru `Kymang/modules/cache.py` menggunakan `cachetools` + `asyncache`.
  - Cache daftar channel FSub (60s), status bot (60s), dan status member user (30s).
- [x] **Task 1.4: Dual-Mode Link Cryptography (Zero Broken Links)**
  - Update `Kymang/modules/func.py`:
    - Link baru menggunakan HMAC-SHA256 signature (`sec_{ts}_{b64}_{hmac}`).
    - Link lama (Base64) tetap didecode normal tanpa error.
- [x] **Task 1.5: Enkripsi Token Klien AES-256-GCM di Database**
  - Buat file baru `Kymang/modules/crypto.py` untuk enkripsi & dekripsi token bot klien dengan master key.
  - Integrasikan ke `Kymang/modules/data.py`.

---

## 🔴 Fase 2: DRM Konten, Anti-DMCA & Isolasi Multi-Tenant
- [x] **Task 2.1: Native DRM & Delivery Protection**
  - Pastikan semua pengiriman media di `Kymang/modules/start.py` menyertakan `protect_content=True`.
- [x] **Task 2.2: Batched Auto-Delete Sweeper Engine**
  - Buat file baru `Kymang/modules/auto_del.py`.
  - Implementasikan background sweeper yang menghapus pesan batch (hingga 100 pesan/call) tiap 10 detik.
  - Tambahkan pesan notifikasi countdown 10 menit yang ramah user.
- [x] **Task 2.3: Per-Bot Semaphore & Rate Throttle**
  - Refactor `Kymang/__init__.py`:
    - Tambahkan `asyncio.Semaphore(10)` per instance sub-bot.
    - Tambahkan throttle 30 msg/detik per bot account.
- [x] **Task 2.4: Isolated FloodWait Circuit Breaker**
  - Wrapper handler aman di `Kymang/__init__.py` agar `FloodWait 429` di 1 sub-bot tidak memblokir bot lain.

---

## 🟠 Fase 3: Storage Redundancy, Monitoring & Bisnis
- [x] **Task 3.1: Multi-Storage Backup Mirroring & Auto-Failover**
  - Update `Kymang/modules/batch.py` & `data.py` untuk dual-channel storage (`PRIMARY_DB_CHANNEL` & `BACKUP_DB_CHANNEL`).
  - Implementasikan auto-failover jika channel primary error/strike.
- [x] **Task 3.2: Health Monitor & Heartbeat Auto-Recovery**
  - Buat file baru `Kymang/modules/monitor.py`.
  - Heartbeat checker tiap 2 menit + auto-restart instance yang macet.
  - Hourly Health Report ke `LOG_GRP` & Error alert < 30 detik.
  - Command `/stats` untuk pemilik sub-bot.
- [x] **Task 3.3: Notifikasi Jatuh Tempo & Graceful Deactivation**
  - Update `Kymang/modules/cek_expired.py` untuk notifikasi H-7, H-3, H-1.
  - Graceful deactivation saat masa aktif habis + session cleanup otomatis setelah 24 jam.
- [x] **Task 3.4: Telegram Stars (XTR) Billing Module**
  - Buat file baru `Kymang/modules/billing.py`.
  - Invoice Telegram Stars untuk sewa/perpanjang masa aktif sub-bot otomatis.

---

## 🟠 Fase 4: Deployment & Polish
- [x] **Task 4.1: Docker Blue-Green Deployment Setup**
  - Buat `Dockerfile`, `docker-compose.yml`, dan `.dockerignore`.
  - Konfigurasi volume permanen untuk `.session` dan `.env`.
- [x] **Task 4.2: Guided Onboarding `/setup`**
  - Wizard interaktif step-by-step untuk onboarding reseller baru di `Kymang/modules/start.py`.
- [x] **Task 4.3: Full Integration Smoke Test**
  - Uji end-to-end seluruh modul dan pastikan kompatibilitas zero-broken-links.
