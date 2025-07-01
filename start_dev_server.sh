#!/bin/bash

# Hauptverzeichnis Start Script
# Wechselt ins Backend-Verzeichnis und startet Backend + ngrok

echo "🚀 Starte Development Server mit ngrok..."

# Farben für Output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funktion zum sanften Bereinigen aller Prozesse
cleanup_all_ports() {
    echo -e "${YELLOW}🧹 Bereinige alle Ports und Prozesse...${NC}"
    
    # Alle Python-Prozesse auf Port 8003 sanft beenden
    local backend_pids=$(lsof -t -i:8003 2>/dev/null)
    if [ ! -z "$backend_pids" ]; then
        echo -e "${CYAN}   🔄 Beende Backend-Prozesse auf Port 8003: $backend_pids${NC}"
        # Erst sanft versuchen
        kill $backend_pids 2>/dev/null
        sleep 3
        # Prüfen ob noch Prozesse laufen
        local remaining_pids=$(lsof -t -i:8003 2>/dev/null)
        if [ ! -z "$remaining_pids" ]; then
            echo -e "${YELLOW}   ⚠️ Verwende Force-Kill für hartnäckige Prozesse: $remaining_pids${NC}"
            kill -9 $remaining_pids 2>/dev/null
            sleep 1
        fi
    fi
    
    # Alle ngrok-Prozesse sanft beenden
    local ngrok_pids=$(pgrep ngrok 2>/dev/null)
    if [ ! -z "$ngrok_pids" ]; then
        echo -e "${CYAN}   🔄 Beende ngrok-Prozesse: $ngrok_pids${NC}"
        kill $ngrok_pids 2>/dev/null
        sleep 2
        # Force-Kill falls nötig
        local remaining_ngrok=$(pgrep ngrok 2>/dev/null)
        if [ ! -z "$remaining_ngrok" ]; then
            kill -9 $remaining_ngrok 2>/dev/null
        fi
    fi
    
    # Port 4040 (ngrok dashboard) bereinigen
    local ngrok_dash_pids=$(lsof -t -i:4040 2>/dev/null)
    if [ ! -z "$ngrok_dash_pids" ]; then
        echo -e "${CYAN}   🔄 Beende ngrok Dashboard-Prozesse auf Port 4040: $ngrok_dash_pids${NC}"
        kill $ngrok_dash_pids 2>/dev/null
        sleep 1
    fi
    
    echo -e "${GREEN}✅ Bereinigung abgeschlossen${NC}"
}

# Automatische Bereinigung am Start
cleanup_all_ports

# Zum Backend-Verzeichnis wechseln
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Backend-Verzeichnis nicht gefunden!${NC}"
    echo "Bitte führen Sie dieses Script aus dem Projektverzeichnis aus."
    exit 1
fi

cd backend

# Prüfen ob ngrok installiert ist
if ! command -v ngrok &> /dev/null; then
    echo -e "${RED}❌ ngrok ist nicht installiert!${NC}"
    echo "Installieren Sie es mit: brew install ngrok"
    exit 1
fi

# Prüfen ob main.py existiert
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ main.py nicht gefunden im Backend-Verzeichnis!${NC}"
    exit 1
fi

# Prüfen ob Python3 verfügbar ist
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ python3 ist nicht installiert!${NC}"
    exit 1
fi

# Finale Prüfung ob Port frei ist (falls Bereinigung nicht erfolgreich war)
if lsof -Pi :8003 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Port 8003 ist immer noch blockiert - erzwinge Bereinigung...${NC}"
    kill -9 $(lsof -t -i:8003) 2>/dev/null
    sleep 3
fi

# Backend im Hintergrund starten (ohne venv)
echo -e "${GREEN}✅ Starte Backend auf Port 8003 (ohne Virtual Environment)...${NC}"
nohup python3 main.py > backend.log 2>&1 &
BACKEND_PID=$!

# Verbesserte Backend-Start-Verification mit Health-Check
echo -e "${CYAN}⏳ Warte auf Backend-Start mit Health-Check...${NC}"
BACKEND_READY=false
for i in {1..20}; do
    sleep 2
    
    # Prüfen ob Prozess noch läuft
    if ! ps -p $BACKEND_PID > /dev/null; then
        echo -e "${RED}❌ Backend-Prozess beendet! (Versuch $i/20)${NC}"
        echo "Prüfen Sie die Logs:"
        tail -10 backend.log
        break
    fi
    
    # Prüfen ob Port verfügbar ist
    if lsof -Pi :8003 -sTCP:LISTEN -t >/dev/null 2>&1; then
        # Prüfen ob Health-Check funktioniert
        if curl -s http://localhost:8003/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend Health-Check erfolgreich! (Versuch $i/20)${NC}"
            BACKEND_READY=true
            break
        else
            echo -e "${YELLOW}⏳ Backend startet, Health-Check noch nicht bereit... (Versuch $i/20)${NC}"
        fi
    else
        echo -e "${YELLOW}⏳ Warte auf Backend-Port... (Versuch $i/20)${NC}"
    fi
done

if [ "$BACKEND_READY" != true ]; then
    echo -e "${RED}❌ Backend konnte nicht erfolgreich gestartet werden!${NC}"
    echo -e "${YELLOW}📋 Debugging-Informationen:${NC}"
    echo "Prozess läuft: $(ps -p $BACKEND_PID > /dev/null && echo 'Ja' || echo 'Nein')"
    echo "Port belegt: $(lsof -Pi :8003 -sTCP:LISTEN -t >/dev/null 2>&1 && echo 'Ja' || echo 'Nein')"
    echo ""
    echo "Letzte 20 Zeilen aus backend.log:"
    tail -20 backend.log
    exit 1
fi

echo -e "${GREEN}✅ Backend erfolgreich gestartet und bereit! PID: $BACKEND_PID${NC}"

# ngrok für Webhooks starten
echo -e "${BLUE}🌐 Starte ngrok Tunnel für Port 8003...${NC}"
echo -e "${YELLOW}⏳ ngrok startet... (kann ein paar Sekunden dauern)${NC}"

# ngrok im Hintergrund starten
nohup ngrok http 8003 > ngrok.log 2>&1 &
NGROK_PID=$!

# Warten bis ngrok bereit ist
sleep 8

# ngrok URL ermitteln (mit verbesserter Fehlerbehandlung)
NGROK_URL=""
for i in {1..15}; do
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    for tunnel in tunnels:
        if tunnel.get('proto') == 'https':
            print(tunnel['public_url'])
            break
except:
    pass
" 2>/dev/null)
    
    if [ ! -z "$NGROK_URL" ]; then
        break
    fi
    echo -e "${YELLOW}⏳ Warte auf ngrok... (Versuch $i/15)${NC}"
    sleep 2
done

if [ -z "$NGROK_URL" ]; then
    echo -e "${RED}❌ ngrok URL konnte nicht ermittelt werden!${NC}"
    echo "Prüfen Sie ngrok.log für Details:"
    cat ngrok.log 2>/dev/null || echo "ngrok.log nicht gefunden"
    # Trotzdem weitermachen - Backend läuft ja
    NGROK_URL="[ngrok URL nicht verfügbar]"
fi

# Erfolgsmeldung
echo ""
echo -e "${GREEN}🎉 Setup erfolgreich abgeschlossen!${NC}"
echo ""
echo -e "${BLUE}📊 Backend Status:${NC}"
echo "   • Backend läuft auf: http://localhost:8003"
echo "   • Backend PID: $BACKEND_PID"
echo "   • Health Check: http://localhost:8003/health"
echo ""
echo -e "${BLUE}🌐 ngrok Tunnel Status:${NC}"
echo "   • Public URL: $NGROK_URL"
echo "   • ngrok PID: $NGROK_PID"
echo "   • ngrok Dashboard: http://localhost:4040"
echo ""
if [ "$NGROK_URL" != "[ngrok URL nicht verfügbar]" ]; then
    echo -e "${YELLOW}🔗 Stripe Webhook URL:${NC}"
    echo -e "${GREEN}$NGROK_URL/stripe-webhook${NC}"
    echo ""
fi
echo -e "${BLUE}📋 Nützliche Befehle:${NC}"
echo "   • Backend Logs: tail -f backend/backend.log"
echo "   • ngrok Logs: tail -f backend/ngrok.log"
echo "   • Backend stoppen: kill $BACKEND_PID"
echo "   • ngrok stoppen: kill $NGROK_PID"
echo "   • Alles stoppen: kill $BACKEND_PID $NGROK_PID"
echo ""
if [ "$NGROK_URL" != "[ngrok URL nicht verfügbar]" ]; then
    echo -e "${GREEN}🎯 Nächste Schritte:${NC}"
    echo "1. Gehen Sie zu Stripe Dashboard"
    echo "2. Fügen Sie die Webhook-URL hinzu: $NGROK_URL/stripe-webhook"
    echo "3. Wählen Sie Events: checkout.session.completed"
    echo ""
fi
echo -e "${YELLOW}💡 Tipp: Lassen Sie dieses Terminal offen, um die Services am Laufen zu halten!${NC}"
echo -e "${CYAN}🔧 Backend läuft ohne Virtual Environment - alle Dependencies müssen global installiert sein${NC}"

# Verbesserte Trap-Funktion für sauberes Herunterfahren
cleanup_on_exit() {
    echo -e "\n${YELLOW}🛑 Beende Backend und ngrok...${NC}"
    kill $BACKEND_PID $NGROK_PID 2>/dev/null
    sleep 2
    
    # Sicherstellen, dass alle Prozesse beendet sind
    cleanup_all_ports
}

# Trap für sauberes Herunterfahren bei CTRL+C
trap cleanup_on_exit SIGINT SIGTERM

# Endlos-Schleife um das Script am Laufen zu halten
echo -e "${CYAN}🔄 Script läuft... Drücken Sie CTRL+C zum Beenden${NC}"
while true; do
    sleep 10
    # Prüfe ob Prozesse noch laufen
    if ! ps -p $BACKEND_PID > /dev/null; then
        echo -e "${RED}❌ Backend-Prozess beendet! PID: $BACKEND_PID${NC}"
        break
    fi
    if ! ps -p $NGROK_PID > /dev/null; then
        echo -e "${RED}❌ ngrok-Prozess beendet! PID: $NGROK_PID${NC}"
        break
    fi
done

cleanup_on_exit 