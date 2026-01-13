# Frontend - Agente Autónomo

Interfaz web moderna para interactuar con el agente autónomo.

## 🚀 Inicio Rápido

1. **Asegúrate de que el backend esté corriendo:**
   ```bash
   cd ..
   ./start_server.sh
   ```

2. **Abre el frontend:**
   - Opción 1: Doble click en `index.html`
   - Opción 2: Servidor local:
     ```bash
     python3 -m http.server 8080
     # Abre http://localhost:8080
     ```

## ✨ Características

- 🎨 **Diseño Moderno**: Dark theme con animaciones suaves
- 💬 **Chat en Tiempo Real**: WebSocket para streaming
- 🔧 **Visualización de Tools**: Ve las herramientas ejecutándose
- 📝 **Historial**: Guarda y carga conversaciones
- 📱 **Responsive**: Funciona en móvil y desktop
- ⚡ **Rápido**: Sin frameworks pesados, vanilla JS

## 🎯 Uso

1. **Nueva Conversación**: Click en "+ Nueva Conversación"
2. **Escribe tu mensaje**: En el input inferior
3. **Envía**: Enter o click en el botón
4. **Ve en tiempo real**: 
   - Indicador de "pensando"
   - Tools ejecutándose
   - Respuesta del agente

## 🔧 Configuración

Edita las URLs en `app.js` si el backend está en otro puerto:

```javascript
const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000';
```

## 📁 Estructura

```
frontend/
├── index.html      # Estructura HTML
├── style.css       # Estilos (dark theme)
├── app.js          # Lógica (WebSocket + API)
└── README.md       # Esta guía
```

## 🎨 Personalización

### Colores

Edita las variables CSS en `style.css`:

```css
:root {
    --primary: #6366f1;
    --secondary: #8b5cf6;
    /* ... más colores */
}
```

### Fuente

Cambia la fuente en `index.html`:

```html
<link href="https://fonts.googleapis.com/css2?family=TuFuente&display=swap">
```

## 🐛 Troubleshooting

**No conecta al backend:**
- Verifica que el backend esté corriendo en puerto 8000
- Revisa la consola del navegador (F12)
- Verifica CORS en el backend

**WebSocket no funciona:**
- Asegúrate de que el backend soporte WebSocket
- Verifica la URL del WebSocket en `app.js`

**Estilos no cargan:**
- Verifica que `style.css` esté en el mismo directorio
- Limpia la caché del navegador (Ctrl+F5)

## 📝 Notas

- Requiere backend corriendo
- Funciona mejor en Chrome/Firefox
- No requiere build ni npm
