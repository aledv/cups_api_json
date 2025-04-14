from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

def run_command(command):
    try:
        output = subprocess.check_output(command, stderr=subprocess.DEVNULL, text=True)
        return output.strip().split('\n') if output.strip() else []
    except subprocess.CalledProcessError:
        return []

def get_default_printer():
    output = run_command(['lpstat', '-d'])
    if output and "system default destination:" in output[0]:
        return output[0].split(": ")[-1]
    return None

def get_completed_jobs_count(printer):
    completed_jobs = run_command(['lpstat', '-W', 'completed', printer])
    return len(completed_jobs)

def get_pending_jobs_count(printer):
    pending_jobs = run_command(['lpstat', '-W', 'not-completed', printer])
    return len(pending_jobs)

def get_printer_status(printer):
    output = run_command(['lpstat', '-p', printer])
    if output:
        # Di solito la prima riga ha qualcosa come:
        # "printer HP_LaserJet is idle.  enabled since ..."
        line = output[0].lower()
        if "disabled" in line:
            return "disabled"
        elif "idle" in line:
            return "idle"
        elif "printing" in line:
            return "printing"
        elif "paused" in line:
            return "paused"
        else:
            return "unknown"
    return "not found"

@app.route('/cups/status')
def cups_status():
    default_printer = get_default_printer()
    return jsonify({
        'default_printer': default_printer,
        'completed_jobs_count': get_completed_jobs_count(default_printer) if default_printer else 0,
        'pending_jobs_count': get_pending_jobs_count(default_printer) if default_printer else 0,
        'printer_status': get_printer_status(default_printer) if default_printer else "not found"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
