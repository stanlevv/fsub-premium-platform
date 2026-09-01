# Kymang/modules/crypto.py
# PRD v5.0 Modul 3: Enkripsi Token Klien AES-256-GCM

import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from Kymang.config import MASTER_CRYPTO_KEY

# ─── Key normalisasi ke 32 bytes via SHA-256 ───────────────────────────────────
# ponytail: sha256 cukup untuk key derivation sederhana ini.
_KEY = hashlib.sha256(MASTER_CRYPTO_KEY.encode()).digest()


def encrypt_token(token: str) -> str:
    """
    Enkripsi plaintext token menggunakan AES-256-GCM.
    Return: base64url string format = nonce(12) + ciphertext + tag
    """
    nonce = os.urandom(12)          # Nonce unik per enkripsi — WAJIB tidak di-reuse
    aesgcm = AESGCM(_KEY)
    ciphertext = aesgcm.encrypt(nonce, token.encode(), None)
    return base64.urlsafe_b64encode(nonce + ciphertext).decode()


def decrypt_token(b64_encrypted: str) -> str:
    """
    Dekripsi token. Raise exception jika ciphertext dimodifikasi (authenticated).
    """
    raw = base64.urlsafe_b64decode(b64_encrypted.encode())
    nonce, ciphertext = raw[:12], raw[12:]
    aesgcm = AESGCM(_KEY)
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
