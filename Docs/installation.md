# Guía de Instalación

Esta guía te ayudará a instalar y configurar el Agente Autónomo en tu sistema.

## Requisitos Previos

### Software Requerido
- **Docker** y **Docker Compose** (recomendado)
- O alternativamente:
  - Python 3.10 o superior
  - Node.js 18 o superior
  - PostgreSQL 14 o superior (opcional, usa SQLite por defecto)

### API Keys Necesarias

Dependiendo de las funcionalidades que quieras usar, necesitarás:

- **LLM** (al menos una):
  - OpenAI API key
  - Anthropic API key
  - DeepSeek API key
  - O Ollama instalado localmente (gratis)

- **Cloud Providers** (opcional):
  - AWS Access Key y Secret Key
  - Azure Subscription ID y credenciales
  - GCP Service Account JSON

- **Notificaciones** (opcional):
  - Twilio API key (para WhatsApp)
  - Credenciales SMTP (para Email)
  - Slack Webhook URL

## Instalación con Docker (Recomendado)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/agente-autonomo.git
cd agente-autonomo
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```bash
# LLM Configuration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
# O usa Ollama (no requiere API key)

# AWS (opcional)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# Azure (opcional)
AZURE_SUBSCRIPTION_ID=...
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...

# GCP (opcional)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Nagios (opcional)
NAGIOS_URL=http://nagios.example.com
NAGIOS_USER=admin
NAGIOS_PASS=...

# WhatsApp (opcional)
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=+14155238886

# Database
DB_PASSWORD=tu_password_seguro
```

### 3. Iniciar los Servicios

```bash
docker-compose up -d
```

Esto iniciará:
- Backend (FastAPI) en puerto 8000
- Frontend (React) en puerto 8080
- PostgreSQL en puerto 5432
- ChromaDB (vector database) en puerto 8001

### 4. Verificar Instalación

```bash
# Ver logs
docker-compose logs -f

# Verificar que todos los servicios estén corriendo
docker-compose ps
```

### 5. Acceder a la Aplicación

Abre tu navegador en: **http://localhost:8080**

## Instalación Manual (Sin Docker)

### 1. Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar migraciones de base de datos
alembic upgrade head

# Iniciar servidor
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend

En otra terminal:

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local

# Iniciar servidor de desarrollo
npm run dev
```

### 3. Ollama (Opcional - Para LLM Local)

Si quieres usar modelos locales en lugar de APIs de pago:

```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Descargar modelo (ejemplo: DeepSeek)
ollama pull deepseek-coder:33b

# Ollama se ejecuta automáticamente en puerto 11434
```

## Configuración Inicial

### 1. Primer Acceso

Al abrir la aplicación por primera vez:

1. Verás la pantalla de configuración
2. Selecciona tu proveedor de LLM preferido
3. Ingresa tu API key
4. Configura el nivel de autonomía (recomendado: "Aprobación")
5. Haz clic en "Guardar"

### 2. Configurar Cloud Providers (Opcional)

Ve a **Configuración → Cloud Providers** y agrega tus credenciales para:
- AWS
- Azure
- GCP

### 3. Configurar Notificaciones (Opcional)

Ve a **Configuración → Notificaciones** y configura:
- WhatsApp (vía Twilio)
- Email (SMTP)
- Slack (Webhook)

## Verificación de Instalación

### Test Básico

En el chat, escribe:

```
Hola, ¿estás funcionando?
```

El agente debería responder.

### Test de Tools

```
Lista los archivos en el directorio actual
```

El agente debería ejecutar `list_directory()` y mostrar los archivos.

### Test de Cloud (si configuraste AWS)

```
Lista mis instancias EC2
```

## Solución de Problemas

### Error: "No API key configured"

- Verifica que hayas configurado al menos una API key de LLM en `.env`
- Reinicia los servicios: `docker-compose restart`

### Error: "Connection refused" al backend

- Verifica que el backend esté corriendo: `docker-compose ps`
- Revisa los logs: `docker-compose logs backend`

### Frontend no carga

- Verifica que el puerto 8080 no esté en uso
- Revisa los logs: `docker-compose logs frontend`

### Ollama no se conecta

- Verifica que Ollama esté corriendo: `ollama list`
- Asegúrate de que el puerto 11434 esté accesible

## Próximos Pasos

- Lee la [Guía de Inicio Rápido](quickstart.md)
- Explora la [Configuración Avanzada](configuration.md)
- Aprende sobre [Aprendizaje Dinámico de APIs](guides/api-learning.md)

## Actualización

Para actualizar a la última versión:

```bash
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```
