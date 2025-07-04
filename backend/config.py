#!/usr/bin/env python3
"""
BarrierefreiCheck - Konfiguration
Zentrale Konfigurationsdatei für Pfade und Einstellungen
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Lade .env Datei
load_dotenv()

# Basis-Verzeichnisse
BASE_DIR = Path(__file__).parent
RESOURCES_DIR = BASE_DIR / "resources"

# Expert Prompts
EXPERT_PROMPTS_DIR = RESOURCES_DIR / "expert_prompts"
GENERATED_PROMPTS_DIR = EXPERT_PROMPTS_DIR / "generated_prompts"

# URL-Konfiguration - Verwende immer lokale Entwicklungseinstellungen als Fallback
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8003')

# Backend Server Konfiguration
BACKEND_HOST = os.getenv('BACKEND_HOST', '0.0.0.0')
BACKEND_PORT = int(os.getenv('BACKEND_PORT', '8003'))

# Payment URLs für Stripe Redirects
FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', 'http://localhost:3000')
PAYMENT_SUCCESS_URL = os.getenv('PAYMENT_SUCCESS_URL', f'{FRONTEND_BASE_URL}/payment/success')
PAYMENT_CANCEL_URL = os.getenv('PAYMENT_CANCEL_URL', f'{FRONTEND_BASE_URL}/payment/canceled')

# Development Fallbacks (falls Frontend nicht läuft)
DEV_PAYMENT_SUCCESS_URL = os.getenv('DEV_PAYMENT_SUCCESS_URL', 'http://localhost:8003/payment-test/success')
DEV_PAYMENT_CANCEL_URL = os.getenv('DEV_PAYMENT_CANCEL_URL', 'http://localhost:8003/payment-test/canceled')

# OpenAI Konfiguration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-2025-04-14")  # GPT-4.1 mit 1M Token Context!
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_RESPONSE_TOKENS", "5000"))  # Response tokens
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))  # 0.0 für Konsistenz

# NEU: Context Window für 1 Million Token Support!
OPENAI_MAX_CONTEXT_TOKENS = int(os.getenv("OPENAI_MAX_CONTEXT_TOKENS", "1000000"))  # 1 MILLION!

# Company/Contact Information
COMPANY_NAME = os.getenv('COMPANY_NAME', 'EcomTask UG')
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'support@inclusa.de')
COMPANY_WEBSITE = os.getenv('COMPANY_WEBSITE', 'https://inclusa.de')

# Logging
LOG_FILE = BASE_DIR / "backend.log"
LOG_LEVEL = "INFO"

# Analyse-Einstellungen
MAX_PAGES_TO_ANALYZE = 10
ANALYSIS_TIMEOUT = 300  # Sekunden 