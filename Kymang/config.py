#Kymang

import os

from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(env_path, override=True)
load_dotenv(".env", override=True)


BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID_ENV = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
MONGO_URL = os.environ.get("MONGO_URL")
ADMINS_ENV = os.environ.get("ADMINS")
LOG_GRP_ENV = os.environ.get("LOG_GRP")

if not BOT_TOKEN:
    raise EnvironmentError("BOT_TOKEN wajib diisi di file .env")
if not API_ID_ENV:
    raise EnvironmentError("API_ID wajib diisi di file .env")
if not API_HASH:
    raise EnvironmentError("API_HASH wajib diisi di file .env")
if not MONGO_URL:
    raise EnvironmentError("MONGO_URL wajib diisi di file .env")
if not ADMINS_ENV:
    raise EnvironmentError("ADMINS wajib diisi di file .env")
if not LOG_GRP_ENV:
    raise EnvironmentError("LOG_GRP wajib diisi di file .env")

API_ID = int(API_ID_ENV)
ADMINS = [int(x) for x in ADMINS_ENV.replace(",", " ").split()]
LOG_GRP = int(LOG_GRP_ENV)
BOT_ID = int(os.environ.get("BOT_ID", BOT_TOKEN.split(":")[0]))

MEMBER = [int(x) for x in os.environ.get("MEMBER", "").replace(",", " ").split()] if os.environ.get("MEMBER") else []
KITA = [int(x) for x in os.environ.get("KITA", "").replace(",", " ").split()] if os.environ.get("KITA") else []
MASTER_CRYPTO_KEY = os.environ.get("MASTER_CRYPTO_KEY", BOT_TOKEN)

