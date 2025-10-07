FROM python:3.11

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

EXPOSE 8000
# Copy entrypoint and make executable
COPY entrypoint.sh /entrypoint.sh
COPY wait_for_db.py /wait_for_db.py
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
