# 👁️ Guía de Uso de la Función de Visión

La función de **Visión Móvil** permite al Agente "ver" a través de la cámara de tu teléfono móvil, facilitando tareas como inspección de hardware, lectura de pantallas externas o identificación de objetos físicos.

> [!NOTE]
> **Privacidad y Costo Zero**: Todo el procesamiento se realiza de forma **local** utilizando **Ollama**. Esto significa que es **100% gratuito** (sin costos de API de terceros) y tus datos visuales nunca salen de tu red local.

## 🚀 Cómo Activar la Visión

Sigue estos pasos para habilitar la visión en tu sesión:

1.  **En el Chat Web**: Haz clic en el botón **"👁️ Activar Visión"** ubicado en la parte superior de la barra lateral izquierda.
2.  **Escaneo de QR**: Se abrirá una ventana emergente con un código QR único.
3.  **Conexión Móvil**: 
    *   Escanea el código QR con la cámara de tu teléfono.
    *   Acepta los permisos de cámara en el navegador de tu móvil.
    *   Verás una interfaz simple en tu teléfono confirmando que estás transmitiendo.
4.  **Confirmación**: Asegúrate de que en la interfaz web aparezca el widget flotante con la leyenda **"📡 Conectado"**.

---

## 🛠️ Cómo Utilizarla con el Agente

Una vez conectado, puedes interactuar con el agente usando comandos naturales. Aquí tienes algunos ejemplos:

*   **Identificación**: *"¿Qué modelo de placa madre es la que estoy apuntando?"*
*   **Lectura**: *"¿Qué dice el error que aparece en ese monitor?"*
*   **Localización**: *"Ayúdame a encontrar el puerto serial en esta Raspberry Pi."*

### Interacción Visual Proactiva
El agente puede enviarte marcas visuales a tu teléfono. Por ejemplo, si le pides ayuda para encontrar un componente, él dibujará un **punto rojo** en la pantalla de tu móvil para indicarte exactamente dónde mirar.

---

## ⚙️ Detalles Técnicos

### Estados de Conexión
*   **📡 Conectado**: La transmisión es fluida y el agente está recibiendo fotogramas.
*   **⌛ Buscando...**: El agente está procesando la imagen actual.
*   **❌ Desconectado**: La sesión móvil se ha cerrado o hay un problema de red.

### Controles del Widget
*   **🗖 Maximizar**: Agranda la vista previa en la web para que puedas ver mejor lo que el agente está analizando.
*   **× Cerrar**: Finaliza la sesión de visión actual.

---

> [!TIP]
> **Mejor Resolución**: Asegúrate de tener buena iluminación. El agente utiliza modelos de visión avanzados que funcionan mejor con imágenes claras y estables.

> [!IMPORTANT]
> **Privacidad**: La transmisión de video es efímera y solo se activa cuando tú escaneas el código QR. No se almacena video de forma permanente en el servidor, solo se procesan capturas puntuales para responder a tus preguntas.
