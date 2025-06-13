# Deployment Guide für Vercel

## 🚨 WICHTIG: Backend muss laufen!

Das Backend auf `18.184.65.167:8003` muss aktiv sein, damit das Frontend funktioniert!

### Backend auf dem Server starten:

```bash
# SSH auf den Server
ssh user@18.184.65.167

# Zum Backend-Verzeichnis
cd /path/to/barrierefrei-backend

# Backend starten (im Hintergrund)
nohup python main.py > backend.log 2>&1 &

# Oder mit systemd Service (empfohlen)
sudo systemctl start barrierefrei-backend
```

## 📋 Vercel Deployment Checkliste

### 1. Environment Variables in Vercel setzen

Gehen Sie zu: https://vercel.com/kapty78s-projects/barrierefreicheck/settings/environment-variables

Fügen Sie folgende Variablen hinzu:

```
NEXT_PUBLIC_SUPABASE_URL=<Ihre-Supabase-URL>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<Ihr-Supabase-Key>
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=<Ihr-Stripe-Public-Key>
```

**Hinweis**: Die Backend-URL ist bereits im Proxy hardcoded (`http://18.184.65.167:8003`)

### 2. Deployment durchführen

```bash
# Im Frontend-Verzeichnis
cd frontend

# Mit Vercel CLI
vercel --prod

# Oder via Git Push (wenn mit GitHub verbunden)
git push origin main
```

### 3. Nach dem Deployment testen

1. **Backend-Verbindung testen**:
   ```bash
   curl https://barrierefreicheck.vercel.app/api/proxy?path=/
   ```

2. **In der Browser-Konsole** (F12):
   ```javascript
   // Sollte true zurückgeben wenn Backend läuft
   fetch('/api/proxy?path=/').then(r => r.ok)
   ```

## 🔧 Troubleshooting

### Problem: "Status wird geladen..." bleibt hängen

**Ursache**: Backend antwortet nicht

**Lösung**:
1. Backend-Status prüfen: `curl http://18.184.65.167:8003/`
2. Backend-Logs prüfen: `tail -f backend.log`
3. Backend neu starten

### Problem: CORS-Fehler

**Lösung**: Der Proxy umgeht CORS-Probleme automatisch. Wenn trotzdem Fehler auftreten:
- Prüfen Sie, ob der Proxy-Endpoint funktioniert
- Stellen Sie sicher, dass alle API-Calls über `/api/proxy` laufen

### Problem: Supabase-Verbindung fehlgeschlagen

**Lösung**: 
- Prüfen Sie die Environment Variables in Vercel
- Stellen Sie sicher, dass die Supabase-Keys korrekt sind

## 🚀 Backend mit SSL (Empfohlen)

Für Produktion sollten Sie SSL einrichten:

```bash
# Nginx installieren
sudo apt install nginx certbot python3-certbot-nginx

# Nginx-Konfiguration
sudo nano /etc/nginx/sites-available/api-barrierefrei

# Inhalt:
server {
    server_name api.inclusa.de;
    
    location / {
        proxy_pass http://localhost:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Aktivieren und SSL einrichten
sudo ln -s /etc/nginx/sites-available/api-barrierefrei /etc/nginx/sites-enabled/
sudo certbot --nginx -d api.inclusa.de
```

Dann den Proxy anpassen in `frontend/src/app/api/proxy/route.ts`:
```typescript
const BACKEND_URL = 'https://api.inclusa.de';
``` 