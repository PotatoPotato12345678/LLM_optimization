FROM python:3.11

WORKDIR /app

# Install OS dependencies. coinor-ipopt provides the `ipopt` executable used by
# the optimizer engine (the scheduling objective is nonlinear, so an NLP-capable
# solver is required).
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev gcc coinor-ipopt \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV OPTIMIZER_SOLVER=ipopt

# Copy app code
COPY . .

EXPOSE 8000
# Copy entrypoint and make executable
COPY entrypoint.sh /entrypoint.sh
COPY wait_for_db.py /wait_for_db.py
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
