FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y \
       libpq-dev \
       libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src/ .
COPY infra/startup.bash /app/startup.bash
RUN chmod +x /app/startup.bash
EXPOSE 8000

CMD ["/app/startup.bash"]