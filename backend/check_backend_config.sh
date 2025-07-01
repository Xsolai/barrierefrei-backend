#!/bin/bash

# Backend Diagnose Script
# Dieses Script prüft die Konfiguration und zeigt Probleme

echo "🔍 Backend Diagnose Script"
echo "=========================="
echo ""

# Farben
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Backend-Verbindung testen
echo "1️⃣ Backend-Verbindung testen..."
if curl -s http://localhost:8003/ > /dev/null; then
    echo -e "${GREEN}✅ Backend läuft auf Port 8003${NC}"
else
    echo -e "${RED}❌ Backend nicht erreichbar auf Port 8003${NC}"
fi
echo ""

# 2. Environment Variables prüfen
echo "2️⃣ Environment Variables prüfen..."
echo ""

# Supabase
if [ -z "$SUPABASE_URL" ]; then
    echo -e "${RED}❌ SUPABASE_URL nicht gesetzt!${NC}"
    echo "   Setzen Sie: export SUPABASE_URL=https://xxx.supabase.co"
else
    echo -e "${GREEN}✅ SUPABASE_URL gesetzt${NC}"
fi

if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo -e "${RED}❌ SUPABASE_SERVICE_ROLE_KEY nicht gesetzt!${NC}"
    echo "   Setzen Sie: export SUPABASE_SERVICE_ROLE_KEY=your-key"
else
    echo -e "${GREEN}✅ SUPABASE_SERVICE_ROLE_KEY gesetzt${NC}"
fi

# Stripe
if [ -z "$STRIPE_SECRET_KEY" ]; then
    echo -e "${YELLOW}⚠️  STRIPE_SECRET_KEY nicht gesetzt${NC}"
    echo "   Setzen Sie: export STRIPE_SECRET_KEY=sk_live_xxx"
fi

if [ -z "$STRIPE_WEBHOOK_SECRET" ]; then
    echo -e "${YELLOW}⚠️  STRIPE_WEBHOOK_SECRET nicht gesetzt${NC}"
    echo "   Setzen Sie: export STRIPE_WEBHOOK_SECRET=whsec_xxx"
fi

# OpenAI
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY nicht gesetzt!${NC}"
    echo "   Setzen Sie: export OPENAI_API_KEY=sk-xxx"
else
    echo -e "${GREEN}✅ OPENAI_API_KEY gesetzt${NC}"
fi

echo ""

# 3. Test-API-Calls
echo "3️⃣ Test-API-Calls..."
echo ""

# Payment Session Test (sollte 503 zurückgeben wenn Stripe nicht konfiguriert ist)
echo "Testing /create-payment-session..."
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8003/create-payment-session \
  -H "Content-Type: application/json" \
  -d '{"plan_id":"test","website_url":"test.com","customer_email":"test@test.com","user_id":"test","price_amount":100}')

if [ "$response" = "503" ]; then
    echo -e "${YELLOW}⚠️  Payment Service nicht verfügbar (Stripe fehlt?)${NC}"
elif [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ Payment Service verfügbar${NC}"
else
    echo -e "${RED}❌ Unerwarteter Status: $response${NC}"
fi

# Analyze Test
echo "Testing /analyze-complete-async..."
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8003/analyze-complete-async \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","max_pages":1,"plan":"basic"}')

if [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ Analyze Endpoint funktioniert${NC}"
else
    echo -e "${RED}❌ Analyze Endpoint Problem: Status $response${NC}"
fi

echo ""
echo "4️⃣ Empfehlungen:"
echo "==============="

# .env Datei erstellen
echo ""
echo "Erstellen Sie eine .env Datei mit allen benötigten Variablen:"
echo ""
echo "cat > .env << EOF"
echo "# Supabase (KRITISCH!)"
echo "SUPABASE_URL=https://xxx.supabase.co"
echo "SUPABASE_SERVICE_ROLE_KEY=eyJxxx..."
echo ""
echo "# Stripe"
echo "STRIPE_SECRET_KEY=sk_live_xxx"
echo "STRIPE_WEBHOOK_SECRET=whsec_xxx"
echo ""
echo "# OpenAI"
echo "OPENAI_API_KEY=sk-xxx"
echo ""
echo "# URLs"
echo "FRONTEND_URL=https://inclusa.de"
echo "BACKEND_URL=http://18.184.65.167:8003"
echo "EOF"
echo ""
echo "Dann laden Sie die Environment Variables:"
echo "export \$(cat .env | grep -v '^#' | xargs)"
echo ""
echo "Und starten Sie das Backend neu!" 