FROM python:3.11-slim

WORKDIR /app

COPY app.py .
RUN pip install flask && apt-get update && apt-get install -y cups-client && apt-get clean

EXPOSE 5001

CMD ["python", "app.py"]
