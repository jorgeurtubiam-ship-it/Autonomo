# Guía de Navegación Web - BrowserTool

## 🌐 Capacidad de Navegación Web

El agente ahora puede **navegar por internet** usando Playwright, similar a Cline.

### ✨ Características

- 🌐 **Visitar páginas web** - Navega a cualquier URL
- 📸 **Capturar screenshots** - Toma imágenes de páginas completas
- 📜 **Extraer contenido** - Obtiene texto e información
- 🖱️ **Hacer click** - Interactúa con elementos
- ⌨️ **Escribir texto** - Llena formularios
- 🔍 **Esperar elementos** - Espera a que carguen
- 📊 **Scroll** - Navega por páginas largas
- ⬅️➡️ **Navegación** - Ir atrás/adelante

---

## 🎯 Acciones Disponibles

### 1. Navigate - Visitar URL

**Descripción:** Navega a una página web

**Ejemplo:**
```
"Visita https://github.com/cline/cline"
"Ve a google.com"
"Abre la página de Wikipedia"
```

**Respuesta:**
```json
{
  "success": true,
  "url": "https://github.com/cline/cline",
  "title": "GitHub - cline/cline",
  "status": 200
}
```

---

### 2. Screenshot - Capturar Pantalla

**Descripción:** Toma un screenshot de la página actual

**Ejemplo:**
```
"Toma un screenshot de esta página"
"Captura la pantalla"
"Guarda una imagen de lo que ves"
```

**Respuesta:**
```json
{
  "success": true,
  "screenshot_path": "/Users/user/.agent_data/screenshots/screenshot_20251225_213000.png",
  "filename": "screenshot_20251225_213000.png",
  "url": "https://github.com/cline/cline"
}
```

**Ubicación:** `~/.agent_data/screenshots/`

---

### 3. Extract - Extraer Contenido

**Descripción:** Extrae texto de la página o de un elemento específico

**Ejemplo sin selector (página completa):**
```
"Extrae el contenido de la página"
"¿Qué dice esta página?"
"Dame el texto de la página"
```

**Ejemplo con selector:**
```
"Extrae el texto del h1"
"Dame el contenido del elemento .description"
"Lee el texto de #main-content"
```

**Respuesta:**
```json
{
  "success": true,
  "title": "Example Domain",
  "url": "https://example.com",
  "text": "Example Domain\nThis domain is for use in illustrative examples...",
  "html_length": 1256
}
```

---

### 4. Click - Hacer Click

**Descripción:** Hace click en un elemento

**Ejemplo:**
```
"Haz click en el botón de login"
"Click en .search-button"
"Presiona el botón #submit"
```

**Respuesta:**
```json
{
  "success": true,
  "selector": ".search-button",
  "message": "Click realizado en .search-button"
}
```

---

### 5. Type - Escribir Texto

**Descripción:** Escribe texto en un campo de entrada

**Ejemplo:**
```
"Escribe 'Python tutorial' en el campo de búsqueda"
"Escribe 'admin' en #username"
"Llena el formulario con 'test@example.com'"
```

**Respuesta:**
```json
{
  "success": true,
  "selector": "#search",
  "text": "Python tutorial",
  "message": "Texto escrito en #search"
}
```

---

### 6. Scroll - Hacer Scroll

**Descripción:** Hace scroll hacia abajo en la página

**Ejemplo:**
```
"Haz scroll hacia abajo"
"Baja en la página"
"Scroll"
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Scroll realizado"
}
```

---

### 7. Wait - Esperar Elemento

**Descripción:** Espera a que un elemento aparezca en la página

**Ejemplo:**
```
"Espera a que aparezca el botón #load-more"
"Espera el elemento .results"
```

**Respuesta:**
```json
{
  "success": true,
  "selector": "#load-more",
  "message": "Elemento #load-more encontrado"
}
```

---

### 8. Back/Forward - Navegación

**Descripción:** Navega hacia atrás o adelante en el historial

**Ejemplo:**
```
"Ve hacia atrás"
"Regresa a la página anterior"
"Avanza"
```

---

### 9. Close - Cerrar Navegador

**Descripción:** Cierra el navegador y libera recursos

**Ejemplo:**
```
"Cierra el navegador"
```

---

## 💡 Ejemplos de Uso Completos

### Ejemplo 1: Buscar en Google

```
Usuario: "Ve a Google, busca 'Playwright tutorial', y toma un screenshot"

Agente:
1. navigate(url="https://google.com")
2. type(selector="input[name='q']", text="Playwright tutorial")
3. click(selector="input[type='submit']")
4. wait(selector="#search")
5. screenshot()
```

---

### Ejemplo 2: Web Scraping

```
Usuario: "Ve a Hacker News y extrae los títulos de las noticias"

Agente:
1. navigate(url="https://news.ycombinator.com")
2. extract(selector=".titleline")
```

---

### Ejemplo 3: Monitoreo de Nagios

```
Usuario: "Visita Nagios y toma un screenshot del dashboard"

Agente:
1. navigate(url="http://localhost:8080/nagios/")
2. wait(selector="#main")
3. screenshot()
```

---

### Ejemplo 4: Automatización de Formulario

```
Usuario: "Ve a example.com, llena el formulario de contacto"

Agente:
1. navigate(url="https://example.com/contact")
2. type(selector="#name", text="John Doe")
3. type(selector="#email", text="john@example.com")
4. type(selector="#message", text="Hello!")
5. click(selector="button[type='submit']")
```

---

## 🔧 Selectores CSS

El BrowserTool usa selectores CSS para identificar elementos:

| Tipo | Ejemplo | Descripción |
|------|---------|-------------|
| ID | `#username` | Elemento con id="username" |
| Clase | `.button` | Elementos con class="button" |
| Tag | `h1` | Todos los elementos \<h1\> |
| Atributo | `input[type='text']` | Inputs de tipo texto |
| Descendiente | `div .content` | .content dentro de div |

---

## ⚙️ Configuración

### Timeout

Por defecto: 30 segundos

```
"Espera el elemento #slow-load con timeout de 60000"
```

### Screenshots

- **Formato:** PNG
- **Ubicación:** `~/.agent_data/screenshots/`
- **Nombre:** `screenshot_YYYYMMDD_HHMMSS.png`
- **Tipo:** Full page (página completa)

---

## ⚠️ Limitaciones

### No Puede:
- ❌ Resolver CAPTCHAs
- ❌ Pasar autenticación de dos factores
- ❌ Ejecutar en sitios con anti-bot agresivo
- ❌ Manejar descargas de archivos

### Puede:
- ✅ Navegar sitios públicos
- ✅ Llenar formularios simples
- ✅ Extraer información
- ✅ Tomar screenshots
- ✅ Web scraping básico

---

## 🚀 Casos de Uso

### 1. Monitoreo
```
"Visita el dashboard de Grafana y toma un screenshot cada hora"
```

### 2. Testing
```
"Ve a la app de staging y verifica que el botón de login funcione"
```

### 3. Web Scraping
```
"Extrae los precios de productos de Amazon"
```

### 4. Documentación
```
"Visita la documentación de Playwright y extrae los ejemplos"
```

### 5. Investigación
```
"Busca información sobre Python async en Google y resume los resultados"
```

---

## 📊 Comparación con Cline

| Feature | Cline | Nuestro Agente |
|---------|-------|----------------|
| Navegación | ✅ Playwright/MCP | ✅ Playwright directo |
| Screenshots | ✅ | ✅ |
| Click/Type | ✅ | ✅ |
| Extract | ✅ | ✅ |
| Scroll | ✅ | ✅ |
| Wait | ✅ | ✅ |
| Headless | ✅ | ✅ |
| Multi-browser | ✅ | ✅ Chromium |

---

## 🔒 Seguridad

- ✅ Headless mode (sin UI visible)
- ✅ Timeout para evitar bloqueos
- ✅ Validación de URLs
- ✅ No ejecuta JavaScript arbitrario
- ✅ Screenshots limitados en tamaño

---

## 📝 Tips

1. **Usa selectores específicos:** `#login-button` mejor que `button`
2. **Espera elementos dinámicos:** Usa `wait` antes de `click`
3. **Cierra el navegador:** Usa `close` cuando termines
4. **Screenshots para debug:** Toma screenshots para ver qué ve el agente

---

## 🐛 Troubleshooting

### Error: "Elemento no encontrado"
- Verifica el selector CSS
- Usa `wait` para esperar que cargue
- Toma un screenshot para ver la página

### Error: "Timeout"
- Aumenta el timeout
- Verifica que la página cargue correctamente
- Revisa tu conexión a internet

### Screenshots no se guardan
- Verifica permisos en `~/.agent_data/screenshots/`
- Revisa espacio en disco

---

## ✅ Estado

- **Instalado:** ✅ Playwright + Chromium
- **Registrado:** ✅ Tool #15
- **Tests:** ✅ 10 tests pasando
- **Documentación:** ✅ Completa

¡Listo para navegar! 🌐
