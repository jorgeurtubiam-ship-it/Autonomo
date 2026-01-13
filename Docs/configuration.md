# Configuración

Guía completa de configuración del Agente Autónomo.

## Archivo de Configuración Principal

El archivo `config.yaml` es el centro de configuración del sistema.

### Ubicación

- **Docker**: `/app/config.yaml` (montado desde `./config.yaml`)
- **Manual**: `backend/config.yaml`

### Estructura Completa

```yaml
# ============================================
# LLM Configuration
# ============================================
llm:
  # Provider: openai, anthropic, deepseek, ollama
  provider: "openai"
  
  # Model name
  model: "gpt-4"
  
  # API Key (usa variables de entorno)
  api_key: "${OPENAI_API_KEY}"
  
  # Temperature (0.0 - 2.0)
  # Menor = más determinístico
  # Mayor = más creativo
  temperature: 0.7
  
  # Max tokens por respuesta
  max_tokens: 4000
  
  # Fallback provider si falla el principal
  fallback:
    provider: "ollama"
    model: "deepseek-coder:33b"

# ============================================
# Agent Behavior
# ============================================
agent:
  # Nivel de autonomía: full, semi, supervised
  autonomy_level: "semi"
  
  # Intervalo de chequeo para monitoreo (segundos)
  check_interval: 60
  
  # Máximo de acciones por hora (límite de seguridad)
  max_actions_per_hour: 50
  
  # Acciones que requieren aprobación explícita
  require_approval_for:
    - "terminate_instance"
    - "delete_resource"
    - "delete_file"
    - "execute_command"  # Comandos potencialmente peligrosos
  
  # Comandos bloqueados (nunca se ejecutan)
  blocked_commands:
    - "rm -rf /"
    - "mkfs"
    - "dd if=/dev/zero"
  
  # Timeout para ejecución de tools (segundos)
  tool_timeout: 300

# ============================================
# Cloud Providers
# ============================================

# AWS
aws:
  enabled: true
  region: "us-east-1"
  access_key_id: "${AWS_ACCESS_KEY_ID}"
  secret_access_key: "${AWS_SECRET_ACCESS_KEY}"
  
  # Regiones adicionales a monitorear
  additional_regions:
    - "us-west-2"
    - "eu-west-1"
  
  # Servicios habilitados
  services:
    ec2: true
    rds: true
    lambda: true
    cloudwatch: true
    s3: true

# Azure
azure:
  enabled: true
  subscription_id: "${AZURE_SUBSCRIPTION_ID}"
  tenant_id: "${AZURE_TENANT_ID}"
  client_id: "${AZURE_CLIENT_ID}"
  client_secret: "${AZURE_CLIENT_SECRET}"
  
  # Resource groups a monitorear
  resource_groups:
    - "production"
    - "staging"

# Google Cloud Platform
gcp:
  enabled: true
  project_id: "${GCP_PROJECT_ID}"
  credentials_file: "${GOOGLE_APPLICATION_CREDENTIALS}"
  
  # Zonas a monitorear
  zones:
    - "us-central1-a"
    - "europe-west1-b"

# ============================================
# Monitoring & Alerts
# ============================================

# Nagios
nagios:
  enabled: true
  url: "http://nagios.example.com"
  username: "${NAGIOS_USER}"
  password: "${NAGIOS_PASS}"
  
  # Verificar SSL
  verify_ssl: true
  
  # Intervalo de polling (segundos)
  poll_interval: 60
  
  # Filtros de alertas
  filters:
    severity: ["critical", "warning"]
    services: ["HTTP", "SSH", "MySQL"]

# ============================================
# Platform Integrations
# ============================================

# Rundeck
rundeck:
  enabled: false
  url: "http://rundeck.example.com"
  api_token: "${RUNDECK_API_TOKEN}"
  
  # Proyectos a monitorear
  projects:
    - "production"
    - "infrastructure"

# Dremio
dremio:
  enabled: false
  url: "http://dremio.example.com:9047"
  username: "${DREMIO_USER}"
  password: "${DREMIO_PASS}"

# MongoDB Atlas
mongodb_atlas:
  enabled: false
  public_key: "${ATLAS_PUBLIC_KEY}"
  private_key: "${ATLAS_PRIVATE_KEY}"
  project_id: "${ATLAS_PROJECT_ID}"

# ============================================
# Notifications
# ============================================

# WhatsApp (vía Twilio)
whatsapp:
  enabled: true
  provider: "twilio"  # twilio, business_api, whatsapp-web
  
  # Twilio credentials
  account_sid: "${TWILIO_ACCOUNT_SID}"
  auth_token: "${TWILIO_AUTH_TOKEN}"
  from_number: "${TWILIO_WHATSAPP_NUMBER}"
  
  # Números a notificar
  notify_numbers:
    - "+5491112345678"
  
  # Tipos de alertas a enviar
  alert_types:
    - "critical"
    - "error"

# Email
email:
  enabled: true
  smtp_host: "smtp.gmail.com"
  smtp_port: 587
  smtp_user: "${EMAIL_USER}"
  smtp_password: "${EMAIL_PASSWORD}"
  from_address: "agent@example.com"
  
  # Destinatarios
  recipients:
    - "admin@example.com"

# Slack
slack:
  enabled: false
  webhook_url: "${SLACK_WEBHOOK_URL}"
  channel: "#alerts"
  username: "Agente Autónomo"

# ============================================
# Database
# ============================================
database:
  # Tipo: postgresql, sqlite
  type: "postgresql"
  
  # PostgreSQL
  host: "postgres"
  port: 5432
  name: "agent_db"
  user: "agent"
  password: "${DB_PASSWORD}"
  
  # SQLite (alternativa)
  # sqlite_path: "./data/agent.db"
  
  # Connection pool
  pool_size: 10
  max_overflow: 20

# ============================================
# Vector Database (para RAG)
# ============================================
vector_db:
  # Tipo: chromadb, pinecone
  type: "chromadb"
  
  # ChromaDB
  host: "chromadb"
  port: 8001
  
  # Pinecone (alternativa)
  # api_key: "${PINECONE_API_KEY}"
  # environment: "us-west1-gcp"
  # index_name: "agent-docs"

# ============================================
# Web Interface
# ============================================
web:
  # Puerto del frontend
  port: 8080
  
  # Puerto del backend
  backend_port: 8000
  
  # CORS origins permitidos
  cors_origins:
    - "http://localhost:8080"
    - "http://localhost:3000"
  
  # Session timeout (minutos)
  session_timeout: 60
  
  # Max file upload size (MB)
  max_upload_size: 100

# ============================================
# Security
# ============================================
security:
  # JWT secret (genera uno único)
  jwt_secret: "${JWT_SECRET}"
  
  # JWT expiration (horas)
  jwt_expiration: 24
  
  # Rate limiting
  rate_limit:
    enabled: true
    requests_per_minute: 60
  
  # Allowed IPs (vacío = todos)
  allowed_ips: []
  
  # Enable audit log
  audit_log: true

# ============================================
# Logging
# ============================================
logging:
  # Level: DEBUG, INFO, WARNING, ERROR
  level: "INFO"
  
  # Log to file
  file: "./logs/agent.log"
  
  # Rotate logs
  rotation: "1 day"
  retention: "30 days"
  
  # Log format
  format: "json"  # json, text

# ============================================
# Performance
# ============================================
performance:
  # Cache TTL (segundos)
  cache_ttl: 300
  
  # Max concurrent tool executions
  max_concurrent_tools: 5
  
  # WebSocket ping interval (segundos)
  websocket_ping_interval: 30
```

## Variables de Entorno

Crea un archivo `.env` con tus credenciales:

```bash
# LLM
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# AWS
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# Azure
AZURE_SUBSCRIPTION_ID=...
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...

# GCP
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCP_PROJECT_ID=my-project

# Nagios
NAGIOS_USER=admin
NAGIOS_PASS=...

# Rundeck
RUNDECK_API_TOKEN=...

# Dremio
DREMIO_USER=admin
DREMIO_PASS=...

# MongoDB Atlas
ATLAS_PUBLIC_KEY=...
ATLAS_PRIVATE_KEY=...
ATLAS_PROJECT_ID=...

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=+14155238886

# Email
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Database
DB_PASSWORD=your-secure-password

# Security
JWT_SECRET=your-random-secret-key-here
```

## Configuración por Entorno

### Desarrollo

```yaml
# config.dev.yaml
agent:
  autonomy_level: "supervised"
  max_actions_per_hour: 10

logging:
  level: "DEBUG"

security:
  rate_limit:
    enabled: false
```

### Producción

```yaml
# config.prod.yaml
agent:
  autonomy_level: "semi"
  max_actions_per_hour: 100

logging:
  level: "INFO"

security:
  rate_limit:
    enabled: true
    requests_per_minute: 60
  
  audit_log: true
```

## Configuración desde la Interfaz Web

Muchas configuraciones se pueden cambiar desde la interfaz web:

1. Ve a **Configuración** (icono de engranaje)
2. Secciones disponibles:
   - **General**: LLM, autonomía
   - **Cloud Providers**: Credenciales AWS/Azure/GCP
   - **Notificaciones**: WhatsApp, Email, Slack
   - **Seguridad**: Permisos, rate limiting

## Validación de Configuración

Valida tu configuración antes de iniciar:

```bash
python -m backend.cli validate-config
```

## Troubleshooting

### Error: "Invalid API key"
- Verifica que las variables de entorno estén correctas
- Asegúrate de que el archivo `.env` esté en el directorio correcto

### Error: "Database connection failed"
- Verifica que PostgreSQL esté corriendo
- Revisa las credenciales en `config.yaml`

### Logs no aparecen
- Verifica que el directorio `logs/` exista
- Revisa permisos de escritura

## Próximos Pasos

- [Guía de Seguridad](../deployment/security.md)
- [Deployment en Producción](../deployment/production.md)
