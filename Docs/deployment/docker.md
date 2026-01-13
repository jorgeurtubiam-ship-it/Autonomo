# Deployment con Docker

Guía completa para desplegar el Agente Autónomo usando Docker.

## Prerrequisitos

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM mínimo
- 10GB espacio en disco

## Estructura de Archivos

```
agente-autonomo/
├── docker-compose.yml
├── .env
├── backend/
│   ├── Dockerfile
│   └── ...
├── frontend/
│   ├── Dockerfile
│   └── ...
└── config.yaml
```

## docker-compose.yml

```yaml
version: '3.8'

services:
  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - DB_HOST=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - VECTOR_DB_HOST=chromadb
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - postgres
      - chromadb
    restart: unless-stopped
    networks:
      - agent-network

  # Frontend Web UI
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "8080:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - agent-network

  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=agent_db
      - POSTGRES_USER=agent
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    networks:
      - agent-network

  # ChromaDB (Vector Database)
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    restart: unless-stopped
    networks:
      - agent-network

  # Redis (Cache)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - agent-network

volumes:
  postgres_data:
  chroma_data:
  redis_data:

networks:
  agent-network:
    driver: bridge
```

## Dockerfile - Backend

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorios
RUN mkdir -p /app/data /app/logs

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s \
  CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicio
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Dockerfile - Frontend

```dockerfile
# Build stage
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## Comandos de Deployment

### Iniciar Servicios

```bash
# Primera vez
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
```

### Detener Servicios

```bash
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

### Actualizar

```bash
# Pull latest changes
git pull origin main

# Rebuild y restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Escalar Servicios

```bash
# Múltiples instancias del backend
docker-compose up -d --scale backend=3
```

## Configuración de Producción

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
    environment:
      - ENV=production
      - LOG_LEVEL=INFO

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    deploy:
      replicas: 2

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
```

### Usar en Producción

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Monitoreo

### Logs Centralizados

```bash
# Ver todos los logs
docker-compose logs -f

# Logs de las últimas 100 líneas
docker-compose logs --tail=100

# Logs desde hace 1 hora
docker-compose logs --since 1h
```

### Métricas

```bash
# Ver uso de recursos
docker stats

# Inspeccionar contenedor
docker inspect agent-backend
```

## Backup

### Base de Datos

```bash
# Backup
docker exec agent-postgres pg_dump -U agent agent_db > backup.sql

# Restore
docker exec -i agent-postgres psql -U agent agent_db < backup.sql
```

### Volúmenes

```bash
# Backup de volumen
docker run --rm -v agent_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz /data

# Restore
docker run --rm -v agent_postgres_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/postgres-backup.tar.gz -C /
```

## Troubleshooting

### Backend no inicia

```bash
# Ver logs
docker-compose logs backend

# Verificar variables de entorno
docker-compose config

# Reiniciar servicio
docker-compose restart backend
```

### Frontend no carga

```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/health

# Verificar logs de nginx
docker-compose logs frontend
```

### Base de datos no conecta

```bash
# Verificar que postgres esté corriendo
docker-compose ps postgres

# Conectar manualmente
docker exec -it agent-postgres psql -U agent -d agent_db
```

## Seguridad

### Secrets

Nunca incluyas secrets en el código. Usa `.env`:

```bash
# .env
OPENAI_API_KEY=sk-...
DB_PASSWORD=secure-password-here
JWT_SECRET=random-secret-key
```

### SSL/TLS

Para producción, usa HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name tudominio.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://frontend:80;
    }
    
    location /api {
        proxy_pass http://backend:8000;
    }
}
```

## Próximos Pasos

- [Producción](production.md) - Configuración para producción
- [Seguridad](security.md) - Mejores prácticas de seguridad
