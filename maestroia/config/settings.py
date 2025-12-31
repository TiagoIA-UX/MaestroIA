import os
from dotenv import load_dotenv
from pathlib import Path

# =========================
# CARREGAMENTO DO .ENV
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

# =========================
# AMBIENTE
# =========================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

IS_PRODUCTION = ENVIRONMENT == "production"

# =========================
# OPENAI / LLM
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.3"))

if not OPENAI_API_KEY:
    raise RuntimeError(
        "❌ OPENAI_API_KEY não encontrada. "
        "Verifique o arquivo .env na raiz do projeto."
    )

# =========================
# LIMITES E GOVERNANÇA
# =========================

MAX_CAMPAIGNS_PER_USER = int(os.getenv("MAX_CAMPAIGNS_PER_USER", "3"))
REQUIRE_HUMAN_APPROVAL = os.getenv("REQUIRE_HUMAN_APPROVAL", "true").lower() == "true"

# =========================
# LOGS
# =========================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# =========================
# APIs DE REDES SOCIAIS
# =========================

# Meta (Facebook/Instagram)
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_APP_ID = os.getenv("META_APP_ID")

# Google Ads
GOOGLE_ADS_CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")

# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
GOOGLE_ADS_CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID")
GOOGLE_ADS_CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
GOOGLE_ADS_REFRESH_TOKEN = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")

# Twitter/X
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# LinkedIn
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")

# TikTok
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
TIKTOK_APP_ID = os.getenv("TIKTOK_APP_ID")

# YouTube
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Pinterest
PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")

# Snapchat
SNAPCHAT_ACCESS_TOKEN = os.getenv("SNAPCHAT_ACCESS_TOKEN")

# =========================
# DEBUG (SÓ PARA DEV)
# =========================

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
