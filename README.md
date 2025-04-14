
# CUPS API Status

## Overview
This project provides an API to interact with **CUPS** (Common UNIX Printing System) and retrieve the status of printers. The service exposes an endpoint that returns information about the default printer and the number of completed and pending jobs for that printer in **JSON format**.

## Features
- Returns the default printer for the system.
- Provides a count of completed and pending print jobs.
- Simple Flask-based microservice.

## Prerequisites
- **CUPS** should be installed and configured on the host machine.
- Docker and Docker Compose installed on your system.

## Endpoints
### GET `/cups/status`
Returns the status of the default printer, including the count of completed and pending jobs.

### Example Response:
```json
{
  "default_printer": "ML-1640-Series",
  "completed_jobs_count": 5,
  "pending_jobs_count": 2
}
```

## Installation

### 1. Clone the repository (or download the files):
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Build and start the container using Docker Compose:
```bash
docker-compose up --build
```

### 3. Verify the API is running:
Once the container is up and running, you can access the API at:
```
http://localhost:5001/cups/status
```

### 4. Stopping the container:
To stop the service, use:
```bash
docker-compose down
```

## Docker Compose Configuration
The project includes a `docker-compose.yml` file that simplifies the process of building and running the service.

### Example `docker-compose.yml`:
```yaml
version: '3.8'

services:
  cups-api:
    build: .
    container_name: cups-api
    ports:
      - "5001:5001"   # Exposes the API on port 5001
    volumes:
      - /var/run/cups/cups.sock:/var/run/cups/cups.sock  # Mounts the CUPS socket
    privileged: true  # Required to interact with the CUPS service
    environment:
      - FLASK_ENV=production
    restart: always
    network_mode: "host"  # Uses host network to avoid connectivity issues with CUPS
```

## Dockerfile
The project includes a `Dockerfile` to build the image for the Flask API:
```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY app.py .
RUN pip install flask && apt-get update && apt-get install -y cups-client && apt-get clean

EXPOSE 5001

CMD ["python", "app.py"]
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

