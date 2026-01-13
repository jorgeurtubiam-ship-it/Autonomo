# 🖥️ Guía de Interfaz de Usuario (UI/UX)

Esta guía detalla las capacidades visuales y componentes interactivos del Agente Autónomo.

---

## 1. Terminal Interactivo (Live Terminal)

El sistema incluye un componente de terminal profesional que se activa automáticamente al ejecutar comandos del sistema.

### Características:
- **Estética macOS/Linux:** Encabezado con botones de control (rojo, amarillo, verde).
- **Consola Real:** Fondo negro con tipografía de ancho fijo (monospace).
- **Prompt Dinámico:** Muestra `user@autonomo:~$` seguido del comando ejecutado.
- **Resiliencia:** Activa el terminal incluso si la herramienta detectada es alucinada por el modelo, siempre que contenga un comando válido.

### Funcionamiento Técnico:
La función `showToolExecution` en `app.js` detecta el tipo de herramienta:
- El resultado se imprime directamente en el área de salida del terminal.
- **Visualización de Errores:** Los errores de ejecución se muestran claramente dentro del terminal, lo que permite al usuario verificar el fallo que disparó el proceso de "Self-Healing".

### 1.1 Feedback de Auto-Corrección:
Cuando el agente entra en modo de auto-corrección, el usuario verá:
1. Un mensaje de error en el terminal.
2. Un nuevo estado de "Pensando" indicando la investigación.
3. El uso del tool de navegación (`browser search`) para buscar la solución.
4. El reintento automático con el comando corregido.

---

## 2. Estado de Pensamiento (Thinking Indicator)

Para mejorar la retroalimentación al usuario, se ha implementado un indicador de carga moderno.

### Características:
- **Pulsación Animada:** El indicador realiza un efecto de pulso suave.
- **Texto Dinámico:** Muestra "Agente está pensando..." con puntos suspensivos animados.
- **Transiciones Fluidas:** Aparece inmediatamente después del mensaje del usuario y desaparece cuando el agente comienza a hablar o ejecutar herramientas.

---

## 3. Sistema de Temas (Theming)

El diseño está basado en **Glassmorphism** y **Dark Mode**.

### Paleta de Colores:
- **Fondo Principal:** `#0f172a` (Slate oscuro).
- **Burbujas Usuario:** `#4f46e5` (Indigo).
- **Burbujas Agente:** `#1e293b`.
- **Acentos:** `#38bdf8` (Cyan).

### Variables CSS Principales:
```css
:root {
  --primary-color: #4f46e5;
  --bg-dark: #0f172a;
  --glass-bg: rgba(30, 41, 59, 0.7);
  --terminal-bg: #000000;
}
```

---

## 4. Guía Visual de Mensajes

- **Markdown:** Soporte completo para negritas, cursivas, listas y bloques de código.
- **Tool Calls:** Los bloques de ejecución de herramientas tienen un borde distintivo y un icono de herramienta.
- **Scroll Automático:** La interfaz se desplaza automáticamente al fondo con cada nuevo mensaje o fragmento de texto.

---

**Última actualización:** 2025-12-29
