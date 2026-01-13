# Guía de Uso del Chat - Ejemplos Completos

## 🎯 Capacidades del Agente

El agente tiene **14 herramientas** disponibles en 4 categorías:

### 📁 Gestión de Archivos (6 tools)
- `read_file` - Leer archivos
- `write_file` - Crear/modificar archivos
- `list_directory` - Listar directorios
- `search_files` - Buscar archivos
- `delete_file` - Eliminar archivos
- `get_file_info` - Info de archivos

### ⚙️ Ejecución de Comandos (3 tools)
- `execute_command` - Ejecutar comandos shell
- `run_script` - Ejecutar scripts
- `install_package` - Instalar paquetes

### 🔧 Operaciones Git (4 tools)
- `git_status` - Estado de git
- `git_diff` - Ver diferencias
- `git_commit` - Hacer commits
- `git_log` - Ver historial

### 🌐 HTTP/APIs (1 tool)
- `http_request` - Llamadas HTTP a APIs externas

---

## 📝 Ejemplos de Uso

### 1. Gestión de Archivos

**Listar archivos:**
```
"Lista todos los archivos .py en el directorio actual"
"Muéstrame los archivos en la carpeta backend"
"Busca todos los archivos .md en el proyecto"
```

**Leer archivos:**
```
"Lee el contenido de README.md"
"Muéstrame el archivo backend/api/main.py"
"¿Qué dice el archivo package.json?"
```

**Crear archivos:**
```
"Crea un archivo llamado test.txt con el texto 'Hola Mundo'"
"Escribe un script Python que imprima 'Hello' en hello.py"
```

**Info de archivos:**
```
"Dame información sobre el archivo README.md"
"¿Cuánto pesa el archivo database.db?"
```

---

### 2. Ejecución de Comandos

**Comandos del sistema:**
```
"Ejecuta el comando ls -la"
"Muéstrame el uso de memoria con free -h"
"¿Qué procesos están corriendo? usa ps aux"
```

**Comandos de desarrollo:**
```
"Ejecuta npm install"
"Corre pytest para los tests"
"Inicia el servidor con python manage.py runserver"
```

---

### 3. Operaciones Git

**Estado del repositorio:**
```
"Muéstrame el estado de git"
"¿Qué archivos han cambiado?"
"Muéstrame las diferencias en git"
```

**Historial:**
```
"Muéstrame los últimos 5 commits"
"¿Quién hizo el último commit?"
"Muéstrame el log de git"
```

**Commits:**
```
"Haz un commit con el mensaje 'Fix: corregido bug en API'"
"Agrega todos los archivos y haz commit"
```

---

### 4. Llamadas HTTP (Nagios, APIs)

**Nagios:**
```
"Tráeme las alertas de Nagios en http://localhost:8080/nagios/cgi-bin/statusjson.cgi?query=servicecount con usuario nagiosadmin y contraseña nagios@2025"

"Consulta el estado de los servicios de Nagios"

"¿Cuántas alertas críticas hay en Nagios?"
```

**APIs públicas:**
```
"Haz un GET a https://api.github.com/users/octocat"

"Consulta la API de GitHub para ver mi perfil"

"Tráeme datos del clima de https://api.weather.com"
```

**APIs con autenticación:**
```
"Llama a http://localhost:8080/api/data con usuario admin y contraseña secret123"
```

---

## 🎨 Ejemplos Combinados

**Análisis de proyecto:**
```
"Lista todos los archivos Python, luego muéstrame el contenido de main.py y dime cuántas líneas tiene"
```

**Desarrollo:**
```
"Crea un archivo test.py con un script de prueba, luego ejecútalo con python test.py"
```

**Monitoreo:**
```
"Consulta las alertas de Nagios y guárdalas en un archivo alertas.txt"
```

**Git workflow:**
```
"Muéstrame qué archivos cambiaron, luego haz un commit con mensaje 'Update: mejoras en API'"
```

---

## 💡 Tips

### ✅ Buenas Prácticas

1. **Sé específico:** "Lista archivos .py" en vez de "muéstrame archivos"
2. **Da contexto:** "En la carpeta backend, lista archivos"
3. **Usa rutas completas:** "Lee /home/user/proyecto/README.md"

### ⚠️ Limitaciones

1. **Comandos largos:** El agente tiene timeout de 30 segundos
2. **Archivos grandes:** Las respuestas se truncan a 1000 caracteres
3. **Permisos:** Necesita permisos para ejecutar comandos

### 🔒 Seguridad

- ✅ El agente NO ejecuta comandos destructivos sin confirmación
- ✅ Los comandos `delete_file` requieren confirmación
- ✅ Las contraseñas en HTTP se envían de forma segura

---

## 🚀 Inicio Rápido

1. **Abre el chat:**
   ```
   http://localhost:3000
   ```

2. **Prueba un comando simple:**
   ```
   "Lista los archivos en el directorio actual"
   ```

3. **Prueba con Nagios:**
   ```
   "Consulta las alertas de Nagios"
   ```

4. **Explora las capacidades:**
   ```
   "¿Qué puedes hacer?"
   ```

---

## 📊 Estado del Sistema

**Backend:** http://localhost:8000
**Frontend:** http://localhost:3000
**Tools disponibles:** 14
**Persistencia:** SQLite + File System
**WebSocket:** Habilitado

¡Listo para usar! 🎉
