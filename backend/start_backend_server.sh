#!/bin/bash

# Backend Start Script für Production Server
# Dieses Script auf den Server (18.184.65.167) kopieren und ausführen

echo "🚀 Starting Barrierefrei Backend Server..."

# Farben für Output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Prüfe ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 ist nicht installiert!${NC}"
    echo "Installieren Sie es mit: sudo apt install python3 python3-pip"
    exit 1
fi

# Zum Backend-Verzeichnis wechseln
BACKEND_DIR="/opt/barrierefrei-backend"  # Passen Sie diesen Pfad an!

if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend-Verzeichnis nicht gefunden: $BACKEND_DIR${NC}"
    echo "Bitte passen Sie den BACKEND_DIR Pfad im Script an."
    exit 1
fi

cd "$BACKEND_DIR"

# Prüfe ob main.py existiert
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ main.py nicht gefunden im Verzeichnis: $BACKEND_DIR${NC}"
    exit 1
fi

# Virtual Environment aktivieren (falls vorhanden)
if [ -d "venv" ]; then
    echo "📦 Aktiviere Virtual Environment..."
    source venv/bin/activate
fi

# Prüfe ob Backend bereits läuft
if lsof -Pi :8003 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Backend läuft bereits auf Port 8003${NC}"
    echo "Stoppen Sie es mit: kill \$(lsof -t -i:8003)"
    exit 0
fi

# Environment Variables setzen (falls .env existiert)
if [ -f ".env" ]; then
    echo "📋 Lade Environment Variables aus .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Backend starten
echo -e "${GREEN}✅ Starte Backend auf Port 8003...${NC}"
echo "📝 Logs werden nach backend.log geschrieben"

# Mit nohup im Hintergrund starten
nohup python3 main.py > backend.log 2>&1 &
BACKEND_PID=$!

# Kurz warten
sleep 3

# Prüfen ob Backend läuft
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✅ Backend erfolgreich gestartet! PID: $BACKEND_PID${NC}"
    echo ""
    echo "📊 Status prüfen mit:"
    echo "   curl http://localhost:8003/"
    echo ""
    echo "📋 Logs anzeigen mit:"
    echo "   tail -f $BACKEND_DIR/backend.log"
    echo ""
    echo "🛑 Backend stoppen mit:"
    echo "   kill $BACKEND_PID"
    echo ""
    echo -e "${GREEN}✅ Frontend kann jetzt auf das Backend zugreifen!${NC}"
else
    echo -e "${RED}❌ Backend konnte nicht gestartet werden!${NC}"
    echo "Prüfen Sie die Logs:"
    tail -20 backend.log
    exit 1
fi 