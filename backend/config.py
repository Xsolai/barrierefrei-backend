#!/usr/bin/env python3
"""
BarrierefreiCheck - Konfiguration
Zentrale Konfigurationsdatei für Pfade und Einstellungen
"""

from pathlib import Path
import os

# Basis-Verzeichnisse
BASE_DIR = Path(__file__).parent
RESOURCES_DIR = BASE_DIR / "resources"

# Expert Prompts
EXPERT_PROMPTS_DIR = RESOURCES_DIR / "expert_prompts"
GENERATED_PROMPTS_DIR = EXPERT_PROMPTS_DIR / "generated_prompts"

# URL-Konfiguration
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://inclusa.de')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://18.184.65.167:8003')

# OpenAI Konfiguration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-2025-04-14")  # GPT-4.1 mit 1M Token Context!
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_RESPONSE_TOKENS", "5000"))  # Response tokens
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))  # 0.0 für Konsistenz

# NEU: Context Window für 1 Million Token Support!
OPENAI_MAX_CONTEXT_TOKENS = int(os.getenv("OPENAI_MAX_CONTEXT_TOKENS", "1000000"))  # 1 MILLION!

# Logging
LOG_FILE = BASE_DIR / "backend.log"
LOG_LEVEL = "INFO"

# Analyse-Einstellungen
MAX_PAGES_TO_ANALYZE = 10
ANALYSIS_TIMEOUT = 300  # Sekunden 