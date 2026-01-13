# 🤖 Agente Autónomo de Propósito General (Vision-Ready)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-orange.svg)](https://ollama.ai)

Un potente agente autónomo inspirado en la arquitectura de **Cline**, diseñado para automatizar operaciones de IT, desarrollo de software y gestión de infraestructura multi-cloud. Equipado con capacidades de **Visión en tiempo real**, este agente puede "ver" a través de tu móvil para ayudarte a debugear hardware, monitores o entornos físicos.

![Demo Visión - Agente Autónomo](assets/screenshots/demo_vision.png)

---

## 🌟 Características Principales

### ☁️ Administración Multi-Cloud & DevOps
Gestiona tu infraestructura de forma conversacional. El agente puede operar sobre:
- **Cloud Providers**: AWS, Azure, Google Cloud (GCP), Oracle Cloud (OCI).
- **Observabilidad**: Integración nativa para consulta y gestión de **Nagios**, **Zabbix** y **Prometheus**.
- **Automatización**: Ejecución de jobs en **Rundeck**, gestión de pipelines y scripts complejos.
- **APIs**: Capacidad de interactuar con cualquier API REST/JSON (Kubernetes, VMware, etc.).

### 👁️ Visión Activa (Cámara Móvil)
Unica funcionalidad que permite al agente ver lo que tú ves:
- **Debugeo Físico**: Apunta la cámara de tu móvil a un servidor, monitor o placa base y pregunta: "¿Qué error ves en el panel frontal?".
- **OCR Real-time**: Lee logs en pantallas físicas o etiquetas de activos.
- **Interacción**: El agente puede "señalar" (marcar) objetos en la pantalla de tu móvil para guiarte.

### 🧠 Inteligencia Flexible (Multi-LLM)
- **Modelos Locales**: Soporte completo para **Ollama** (Llama 3.2, Moondream para visión).
- **Cloud LLMs**: DeepSeek, OpenAI (GPT-4), Anthropic (Claude 3.5 Sonnet).

---

## 🚀 Inicio Rápido

### 1. Requisitos
- Python 3.10+
- Ollama (opcional, para ejecución 100% local)

### 2. Instalación
```bash
git clone https://github.com/jorgeurtubiam-ship-it/Autonomo.git
cd Autonomo
pip install -r requirements.txt
```

### 3. Configuración
Crea un archivo `.env` basado en `.env.example`:
```bash
cp .env.example .env
# Edita con tus llaves o usa Ollama por defecto
```

### 4. Lanzamiento
El sistema incluye un dashboard web con terminal integrada y streaming de video.
```bash
./start_all.sh
```
Accede a: `http://localhost:3000`

---

## 🛠️ Herramientas del Sistema (Tools)

El agente utiliza el ciclo **Plan & Act** para ejecutar tareas usando sus herramientas:

- **Operaciones de Archivo**: `read`, `write`, `search`, `list`, `patch`.
- **Ejecución**: Shell seguro, Python scripts, Node.js, despliegue de paquetes.
- **Git Pro**: Gestión completa de repositorios, ramas y commits.
- **Web & API**: Navegación con `browser` y peticiones `http_request`.
- **Visión**: `get_visual_context` y `point_to_object`.

---

## 🏗️ Arquitectura

```mermaid
graph TD
    User((Usuario)) --> UI[Frontend - Glassmorphism UI]
    UI --> WS[WebSocket / API FastAPI]
    WS --> Core[Agent Core - Plan & Act]
    Core --> LLM{LLM Provider}
    LLM --> OpenAI[OpenAI / Anthropic]
    LLM --> Ollama[Ollama Local]
    Core --> Tools[Tool Registry]
    Tools --> Cloud[AWS/Azure/OCI/GCP]
    Tools --> Obs[Nagios/Rundeck]
    Tools --> Vision[Vision Manager - WebRTC]
    Vision <--> Mobile((Móvil Usuario))
```

---

## 💡 Ejemplos de lo que puede hacer por ti

> "Revisa las instancias de **AWS** en 'us-east-1' que tengan la tag 'Producción' y dime si alguna tiene uso de CPU > 90%."

> "Mira a través de mi cámara (Visión) y dime qué cables están mal conectados en este rack."

> "Conéctate a **Nagios**, busca las alertas críticas de la última hora y genera un reporte en un archivo markdown."

> "Lanza el job 'Backup-DB' en **Rundeck** y avísame cuando termine consultando los logs."

---

## 📁 Estructura del Proyecto

- `backend/`: API FastAPI y lógica del agente (`core.py`, `llm_provider.py`).
- `frontend/`: Interfaz web moderna con soporte para WebRTC.
- `Docs/`: Documentación detallada por módulos.
- `scripts/`: Utilidades de control y mantenimiento.

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Siéntete libre de usarlo, modificarlo y contribuir.

---

## 🤝 Contribuciones

¿Quieres añadir soporte para más herramientas? ¡Los Pull Requests son bienvenidos!

1. Fork el proyecto.
2. Crea una rama (`git checkout -b feature/AmazingTool`).
3. Commit tus cambios (`git commit -m 'Add AmazingTool'`).
4. Push a la rama (`git push origin feature/AmazingTool`).
5. Abre un Pull Request.

---
*Hecho por [LordZero](https://github.com/jorgeurtubiam-ship-it) - 2026*

## 🏷️ Hashtags & Difusión

Si compartes este proyecto, ¡usa estos hashtags para llegar a más gente!

#AI #AutonomousAgents #DevOps #CloudComputing #MultiCloud #AWS #Azure #GCP #OCI #Nagios #Rundeck #ComputerVision #Ollama #OpenSource #FastAPI #Python #AIAgent #TechInnovation
