# Giovanna Rupture Monitor — Dockerfile
# Runs pipeline (ShadowTraffic local data) and serves dashboard via http.server

FROM python:3.12-slim

WORKDIR /app

# Install deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY main.py .
COPY generate_shadowtraffic_data.py .
COPY dashboard.html .
COPY data/ data/
COPY spec/ spec/
COPY contract.md .
COPY README.md .

# Entrypoint: run pipeline then serve
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
