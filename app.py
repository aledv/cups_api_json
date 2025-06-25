#!/usr/bin/env python3
import cups
from flask import Flask, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_cups_connection():
    """Stabilisce connessione con CUPS"""
    try:
        # Connessione al server CUPS (localhost:631 di default)
        conn = cups.Connection()
        return conn
    except Exception as e:
        logging.error(f"Errore connessione CUPS: {e}")
        return None

def get_default_printer(conn):
    """Ottiene la stampante predefinita"""
    try:
        return conn.getDefault()
    except Exception as e:
        logging.error(f"Errore ottenimento stampante predefinita: {e}")
        return None

def get_printer_status(conn, printer_name):
    """Ottiene lo stato della stampante"""
    try:
        if not printer_name:
            return "unknown"
        
        printers = conn.getPrinters()
        if printer_name in printers:
            printer_info = printers[printer_name]
            state = printer_info.get('printer-state', 3)
            
            # Stati CUPS: 3=idle, 4=processing, 5=stopped
            if state == 3:
                return "idle"
            elif state == 4:
                return "processing"
            elif state == 5:
                return "stopped"
            else:
                return "unknown"
        return "not_found"
    except Exception as e:
        logging.error(f"Errore ottenimento stato stampante: {e}")
        return "error"

def get_jobs_count(conn):
    """Ottiene il conteggio dei job completati e pendenti"""
    try:
        # Job attivi/pendenti
        active_jobs = conn.getJobs(which_jobs='not-completed')
        pending_count = len(active_jobs)
        
        # Job completati (limitiamo agli ultimi per performance)
        completed_jobs = conn.getJobs(which_jobs='completed', limit=100)
        completed_count = len(completed_jobs)
        
        return completed_count, pending_count
    except Exception as e:
        logging.error(f"Errore ottenimento job: {e}")
        return 0, 0

@app.route('/cups/status', methods=['GET'])
def cups_status():
    """Endpoint principale che restituisce lo status di CUPS"""
    try:
        # Connessione a CUPS
        conn = get_cups_connection()
        if not conn:
            return jsonify({
                "error": "Impossibile connettersi a CUPS",
                "default_printer": None,
                "completed_jobs_count": 0,
                "pending_jobs_count": 0,
                "printer_status": "error"
            }), 500
        
        # Ottieni stampante predefinita
        default_printer = get_default_printer(conn)
        
        # Ottieni stato stampante
        printer_status = get_printer_status(conn, default_printer)
        
        # Ottieni conteggio job
        completed_count, pending_count = get_jobs_count(conn)
        
        response = {
            "default_printer": default_printer,
            "completed_jobs_count": completed_count,
            "pending_jobs_count": pending_count,
            "printer_status": printer_status
        }
        
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Errore generale: {e}")
        return jsonify({
            "error": str(e),
            "default_printer": None,
            "completed_jobs_count": 0,
            "pending_jobs_count": 0,
            "printer_status": "error"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)