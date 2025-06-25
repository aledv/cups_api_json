# CUPS Status Monitor

Un servizio Docker che monitora lo stato del server CUPS locale e fornisce un endpoint REST per ottenere informazioni su stampanti e job di stampa.

## Funzionalità

- **Endpoint `/cups/status`**: Restituisce informazioni complete sullo stato di CUPS
- **Endpoint `/health`**: Health check per il container
- **Monitoraggio in tempo reale**: Accesso diretto al server CUPS locale
- **Container sicuro**: Esecuzione con utente non-root

## Risposta API

```json
{
  "default_printer": "ML-1640-Series",
  "completed_jobs_count": 5,
  "pending_jobs_count": 2,
  "printer_status": "idle"
}
```

### Stati stampante possibili:
- `idle`: Stampante disponibile
- `processing`: Stampante in fase di stampa
- `stopped`: Stampante fermata
- `error`: Errore di comunicazione
- `not_found`: Stampante non trovata
- `unknown`: Stato sconosciuto

## Quick Start

### Opzione 1: Script automatico
```bash
chmod +x build-and-run.sh
./build-and-run.sh
```

### Opzione 2: Docker Compose
```bash
docker-compose up -d
```

### Opzione 3: Build manuale
```bash
# Build
docker build -t cups-status-monitor .

# Run
docker run -d \
  --name cups-status-monitor \
  --network host \
  -p 5001:5001 \
  -v /var/run/cups/cups.sock:/var/run/cups/cups.sock:ro \
  cups-status-monitor
```

## Test dell'endpoint

```bash
# Status CUPS
curl http://localhost:5001/cups/status

# Health check
curl http://localhost:5001/health
```

## Requisiti

- Docker
- Server CUPS attivo su localhost
- Porta 5001 disponibile

## Configurazione

Il container utilizza `network_mode: host` per accedere al server CUPS locale. Se CUPS utilizza un socket Unix, questo viene montato come volume read-only.

## Troubleshooting

### Controllo logs
```bash
docker logs cups-status-monitor
```

### Verificare CUPS
```bash
# Controlla se CUPS è attivo
systemctl status cups

# Testa connessione locale
lpstat -t
```

### Problemi comuni

1. **Errore di connessione CUPS**: Verifica che CUPS sia avviato e accessibile
2. **Porta 5001 occupata**: Cambia il mapping porta nel docker run o docker-compose
3. **Permessi socket**: Assicurati che il socket CUPS abbia i permessi corretti

## Struttura del progetto

```
.
├── app.py              # Applicazione Flask principale
├── Dockerfile          # Definizione immagine Docker
├── requirements.txt    # Dipendenze Python
├── docker-compose.yml  # Configurazione Docker Compose
├── build-and-run.sh   # Script di build e avvio
└── README.md          # Questa documentazione
```