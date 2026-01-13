# 🚀 Guía de Inicio Rápido

Esta guía te llevará de 0 a tener el Agente Autónomo funcionando en **menos de 5 minutos**.

---

## ⚡ Quick Start (5 minutos)

### Paso 1: Clonar y Preparar (1 min)

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/auto.git
cd auto

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
```

### Paso 2: Instalar Dependencias (2 min)

```bash
pip install -r requirements.txt
```

### Paso 3: Configurar API Key (1 min)

Elige **UNA** de estas opciones:

#### Opción A: DeepSeek (Recomendado - $0.14 por millón de tokens)

```bash
export DEEPSEEK_API_KEY=\"sk-...\"
```

#### Opción B: Ollama (Gratis, Local)

```bash
# Instalar Ollama
curl https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama3.2:latest

# Iniciar servidor
ollama serve
```

### Paso 4: Iniciar Aplicación (1 min)

```bash
# Iniciar todo (Backend + Frontend)
./start_all.sh
```

**¡Listo!** Abre http://localhost:3000 en tu navegador.

---

## 🎯 Primeros Pasos

### 1. Configurar API Key en la UI

1. Click en botón 🔑 \"API Keys\"
2. Pegar tu API key de DeepSeek
3. Click \"💾 Guardar\"

### 2. Iniciar Primera Conversación

1. Click "+ Nueva Conversación"
2. Escribe: `"Hola, preséntate"`
3. Presiona Enter

### 3. Probar Herramientas y Terminal
Verás aparecer una **terminal profesional** cuando ejecutes comandos:

```
"Crea un archivo test.txt con el texto 'Hola Mundo'"
"Lee el contenido de test.txt"
"Lista los archivos en el directorio actual" (Verás el terminal en vivo)
```

---

## 📖 Ejemplos Comunes

### Gestión de Archivos

```
\"Crea un archivo hello.py con un script que imprima 'Hola Mundo'\"
\"Busca todos los archivos .md en el proyecto\"
\"Elimina el archivo temp.txt\"
```

### Comandos Shell

```
\"Ejecuta 'ls -la' en el directorio actual\"
\"Instala el paquete requests con pip\"
\"Muestra los procesos de Python corriendo\"
```

### Git

```
\"Muestra el estado del repositorio\"
\"Haz un commit con mensaje 'feat: add feature'\"
\"Muestra los últimos 5 commits\"
```

### Desarrollo

```
\"Crea un servidor Express básico en Node.js\"
\"Escribe tests para la función fibonacci\"
\"Documenta la función process_message\"
```

---

## 🔧 Comandos Útiles

### Gestión del Sistema

```bash
# Iniciar todo
./start_all.sh

# Detener todo
./stop_all.sh

# Solo backend
./start_server.sh

# Solo frontend
./start_frontend.sh

# Reiniciar backend
./restart_server.sh
```

### Ver Logs

```bash
# Backend
tail -f logs/backend.log

# Frontend
tail -f logs/frontend.log

# Ambos
tail -f logs/*.log
```

### Verificar Estado

```bash
# Health check
curl http://localhost:8000/health

# Configuración actual
curl http://localhost:8000/api/config/

# Conversaciones
curl http://localhost:8000/api/conversations/
```

---

## 🎨 Cambiar Provider

### Desde la UI

1. Click en dropdown \"Provider\"
2. Seleccionar: DeepSeek / OpenAI / Anthropic / Ollama
3. Seleccionar modelo
4. ✅ Cambio automático

### Desde la API

```bash
curl -X PUT http://localhost:8000/api/config/ \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"llm_provider\": \"deepseek\",
    \"model\": \"deepseek-chat\"
  }'
```

---

## 🐛 Troubleshooting Rápido

### Backend no inicia

```bash
# Liberar puerto
lsof -ti:8000 | xargs kill -9

# Reintentar
./start_server.sh
```

### Frontend no carga

```bash
# Liberar puerto
lsof -ti:3000 | xargs kill -9

# Reintentar
./start_frontend.sh
```

### AI no responde

```bash
# Verificar provider
curl http://localhost:8000/api/config/

# Verificar API key
sqlite3 ~/.agent_data/conversations/agent.db \"SELECT * FROM api_keys;\"

# Ver logs
tail -50 logs/backend.log | grep -i error
```

---

## 📚 Próximos Pasos

1. **Explorar Interfaz:** [USER_INTERFACE.md](USER_INTERFACE.md) ⭐
2. **Arquitectura:** [ARCHITECTURE.md](ARCHITECTURE.md)
3. **API Reference:** [API_REFERENCE.md](API_REFERENCE.md)
4. **Desarrollo:** [Docs/development/custom-tools.md](development/custom-tools.md)

---

## 💡 Tips

- **Usa DeepSeek** para mejor relación calidad/precio
- **Ollama** es gratis pero más lento
- **Guarda conversaciones** importantes
- **Experimenta** con diferentes prompts
- **Revisa logs** si algo falla

---

## 🆘 Ayuda

- **Documentación:** [Docs/](.)
- **Issues:** GitHub Issues
- **Email:** soporte@tudominio.com

---

**¡Disfruta usando el Agente Autónomo!** 🚀
