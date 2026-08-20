FROM python:3.14-slim

WORKDIR /app

# Install system dependencies for numpy and xgboost
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY model/ ./model/

EXPOSE 5000

CMD ["python", "app.py"]