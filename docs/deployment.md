# Guía de Deployment - ASCII-Me

## Docker Containerization

### Dockerfile básico

```bash
FROM python:3.11-slim
Instalar dependencias del sistema

RUN apt-get update && apt-get install -y \
gcc \
libjpeg-dev \
zlib1g-dev \
&& rm -rf /var/lib/apt/lists/*

Crear usuario no-root

RUN useradd --create-home --shell /bin/bash ascii-me

Configurar directorio de trabajo

WORKDIR /app

Copiar requirements

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

Copiar código fuente

COPY src/ ./src/
COPY setup.py pyproject.toml ./

Instalar ASCII-Me

RUN pip install -e .

Cambiar a usuario no-root

USER ascii-me

Comando por defecto

CMD ["ascii-art", "--help"]
```

---

### Docker Compose para desarrollo

```bash

docker-compose.yml

version: '3.8'

services:
  ascii-me:
    build: .
    volumes:
      - ./images:/app/images:ro
      - ./output:/app/output
    environment:
      - LOG_LEVEL=INFO
    command: ascii-art scan /app/images

  ascii-me-api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./temp:/app/temp
    environment:
      - FLASK_ENV=production
    command: python -m examples.integrations
```

---

## Deployment en Cloud

### AWS Lambda

````bash

lambda_function.py

```python
import json
import base64
from io import BytesIO
from ascii_me import ASCIIConverter
from PIL import Image

def lambda_handler(event, context):
    """AWS Lambda handler para ASCII-Me."""
    try:
        # Obtener imagen de base64
        image_data = base64.b64decode(event['image'])
        image = Image.open(BytesIO(image_data))

        # Configurar convertidor
        converter = ASCIIConverter(
            width=event.get('width', 80),
            charset=event.get('charset', 'extended'),
            color_mode=False
        )

        # Convertir
        ascii_result = converter.image_to_ascii(image)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'ascii_art': ascii_result,
                'success': True
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'success': False
            })
        }
````

### Google Cloud Run

Dockerfile para Cloud Run

```bash

FROM python:3.11-slim

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
gcc libjpeg-dev zlib1g-dev \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY src/ ./src/
COPY setup.py pyproject.toml ./
RUN pip install -e .

COPY examples/cloud_run_app.py ./app.py

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app

text
```

### Heroku Deployment

```bash

app.yaml para Heroku

build:
os: ubuntu-22
python_version: 3.11

env_variables:
LOG_LEVEL: INFO
MAX_UPLOAD_SIZE: 10485760 # 10MB

runtime_config:
python_version: 3.11

text
undefined

Procfile

web: gunicorn examples.integrations:integracion_api_rest() --bind 0.0.0.0:$PORT

text
```

## Kubernetes Deployment

### Deployment manifest

```bash

k8s-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
name: ascii-me-api
labels:
app: ascii-me
spec:
replicas: 3
selector:
matchLabels:
app: ascii-me
template:
metadata:
labels:
app: ascii-me
spec:
containers:
- name: ascii-me
image: ascii-me:latest
ports:
- containerPort: 5000
env:
- name: LOG_LEVEL
value: "INFO"
resources:
requests:
memory: "256Mi"
cpu: "250m"
limits:
memory: "512Mi"
cpu: "500m"
livenessProbe:
httpGet:
path: /api/health
port: 5000
initialDelaySeconds: 30
periodSeconds: 10
readinessProbe:
httpGet:
path: /api/health
port: 5000
initialDelaySeconds: 5
periodSeconds: 5

apiVersion: v1
kind: Service
metadata:
name: ascii-me-service
spec:
selector:
app: ascii-me
ports:
- protocol: TCP
port: 80
targetPort: 5000
type: LoadBalancer

```

## Monitoreo y Logging

### Configuración de Prometheus

```bash
prometheus.yml

global:
scrape_interval: 15s

scrape_configs:

    job_name: 'ascii-me'
    static_configs:

        targets: ['ascii-me-service:5000']
        metrics_path: /metrics
        scrape_interval: 5s
```

### Grafana Dashboard

```bash

{
"dashboard": {
"title": "ASCII-Me Metrics",
"panels": [
{
"title": "Requests per Second",
"type": "graph",
"targets": [
{
"expr": "rate(http_requests_total[5m])"
}
]
},
{
"title": "Response Time",
"type": "graph",
"targets": [
{
"expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)"
}
]
}
]
}
}

```

## CI/CD Pipeline Completo

### GitLab CI

```bash

.gitlab-ci.yml

stages:

    test

    build

    deploy

variables:
DOCKER_DRIVER: overlay2
DOCKER_TLS_CERTDIR: "/certs"

test:
stage: test
image: python:3.11
script:
- pip install -e .[dev]
- pytest --cov=src/ascii_me
- black --check src tests
- flake8 src tests

build:
stage: build
image: docker:20.10.16
services:
- docker:20.10.16-dind
script:
- docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
- docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
only:
- main

deploy:
stage: deploy
image: kubectl:latest
script:
- kubectl set image deployment/ascii-me-api ascii-me=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
- kubectl rollout status deployment/ascii-me-api
only:
- main
when: manual

```

## Configuración de Producción

### Configuración con variables de entorno

```bash

config.py

import os
from dataclasses import dataclass

@dataclass
class Config:
"""Configuración para ASCII-Me en producción."""

text
# Logging
log_level: str = os.getenv('LOG_LEVEL', 'INFO')
log_format: str = os.getenv('LOG_FORMAT', 'json')

# Performance
max_image_size: int = int(os.getenv('MAX_IMAGE_SIZE', '10485760'))  # 10MB
max_width: int = int(os.getenv('MAX_WIDTH', '200'))
max_height: int = int(os.getenv('MAX_HEIGHT', '200'))

# Cache
cache_enabled: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
cache_ttl: int = int(os.getenv('CACHE_TTL', '3600'))  # 1 hora

# Security
rate_limit: str = os.getenv('RATE_LIMIT', '100/hour')
allowed_origins: list = os.getenv('ALLOWED_ORIGINS', '*').split(',')

# Monitoring
metrics_enabled: bool = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
health_check_interval: int = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))

config = Config()

```

### Health Check endpoint

```bash

health.py

from datetime import datetime
import psutil
from ascii_me import version

def get_health_status():
"""Retorna el estado de salud del servicio."""
try:
return {
'status': 'healthy',
'timestamp': datetime.utcnow().isoformat(),
'version': version,
'uptime': get_uptime(),
'memory_usage': get_memory_usage(),
'disk_usage': get_disk_usage(),
'checks': {
'ascii_converter': test_ascii_converter(),
'image_processor': test_image_processor(),
}
}
except Exception as e:
return {
'status': 'unhealthy',
'error': str(e),
'timestamp': datetime.utcnow().isoformat()
}

def get_uptime():
"""Retorna el uptime del sistema."""
return psutil.boot_time()

def get_memory_usage():
"""Retorna el uso de memoria."""
memory = psutil.virtual_memory()
return {
'total': memory.total,
'available': memory.available,
'percent': memory.percent
}

def get_disk_usage():
"""Retorna el uso de disco."""
disk = psutil.disk_usage('/')
return {
'total': disk.total,
'free': disk.free,
'percent': (disk.used / disk.total) * 100
}

def test_ascii_converter():
"""Test básico del convertidor."""
try:
from ascii_me import ASCIIConverter
from PIL import Image

text
    converter = ASCIIConverter(width=10)
    img = Image.new('RGB', (50, 50), 'red')
    result = converter.image_to_ascii(img)

    return len(result) > 0
except:
    return False

def test_image_processor():
"""Test básico del procesador."""
try:
from ascii_me import ImageProcessor
processor = ImageProcessor()
return True
except:
return False

```
