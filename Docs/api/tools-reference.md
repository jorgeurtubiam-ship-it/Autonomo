# Referencia de Tools

Listado completo de todos los tools disponibles en el agente.

## File Operations

### read_file
Lee el contenido de un archivo.

**Parámetros:**
- `path` (string): Ruta absoluta o relativa al archivo

**Ejemplo:**
```
"Lee el archivo config.yaml"
```

### write_file
Crea o sobrescribe un archivo.

**Parámetros:**
- `path` (string): Ruta del archivo
- `content` (string): Contenido a escribir

**Ejemplo:**
```
"Crea un archivo test.txt con el contenido 'Hola Mundo'"
```

### edit_file
Edita un archivo existente (diff-based).

**Parámetros:**
- `path` (string): Ruta del archivo
- `changes` (array): Lista de cambios a aplicar

**Ejemplo:**
```
"En el archivo app.py, cambia el puerto de 8000 a 9000"
```

### list_directory
Lista el contenido de un directorio.

**Parámetros:**
- `path` (string): Ruta del directorio

**Ejemplo:**
```
"Lista los archivos en /home/user/project"
```

### search_files
Busca archivos por patrón.

**Parámetros:**
- `pattern` (string): Patrón de búsqueda (glob)
- `path` (string): Directorio donde buscar

**Ejemplo:**
```
"Busca todos los archivos .py en el proyecto"
```

## Command Execution

### execute_command
Ejecuta un comando shell.

**Parámetros:**
- `cmd` (string): Comando a ejecutar
- `cwd` (string, opcional): Directorio de trabajo

**Ejemplo:**
```
"Ejecuta npm install"
```

### execute_ssh
Ejecuta comando en servidor remoto vía SSH.

**Parámetros:**
- `host` (string): Host remoto
- `cmd` (string): Comando
- `user` (string, opcional): Usuario SSH

**Ejemplo:**
```
"Ejecuta 'systemctl status nginx' en server.example.com"
```

## Cloud - AWS

### list_ec2_instances
Lista instancias EC2.

**Parámetros:**
- `region` (string, opcional): Región AWS

**Ejemplo:**
```
"Lista las instancias EC2 en us-east-1"
```

### start_ec2
Inicia una instancia EC2.

**Parámetros:**
- `instance_id` (string): ID de la instancia

**Ejemplo:**
```
"Inicia la instancia i-1234567890abcdef0"
```

### stop_ec2
Detiene una instancia EC2.

**Parámetros:**
- `instance_id` (string): ID de la instancia

**Ejemplo:**
```
"Detén la instancia i-1234567890abcdef0"
```

### check_cloudwatch_alarms
Revisa alarmas de CloudWatch.

**Parámetros:**
- `state` (string, opcional): Estado (ALARM, OK, INSUFFICIENT_DATA)

**Ejemplo:**
```
"Muestra las alarmas activas de CloudWatch"
```

## Cloud - Azure

### list_vms
Lista VMs de Azure.

**Parámetros:**
- `resource_group` (string, opcional): Resource group

**Ejemplo:**
```
"Lista las VMs en Azure"
```

### start_vm
Inicia una VM de Azure.

**Parámetros:**
- `vm_id` (string): ID de la VM

**Ejemplo:**
```
"Inicia la VM prod-web-01"
```

## Cloud - GCP

### list_gce_instances
Lista instancias de Compute Engine.

**Parámetros:**
- `zone` (string, opcional): Zona GCP

**Ejemplo:**
```
"Lista las instancias GCE en us-central1-a"
```

## Monitoring

### check_nagios_alerts
Revisa alertas de Nagios.

**Parámetros:**
- `severity` (string, opcional): Severidad (critical, warning)

**Ejemplo:**
```
"Muestra las alertas críticas de Nagios"
```

### analyze_logs
Analiza archivos de log.

**Parámetros:**
- `path` (string): Ruta al archivo de log
- `pattern` (string, opcional): Patrón a buscar

**Ejemplo:**
```
"Analiza /var/log/nginx/error.log buscando errores 500"
```

## Platform Integrations

### execute_rundeck_job
Ejecuta un job de Rundeck.

**Parámetros:**
- `job_id` (string): ID del job
- `params` (object, opcional): Parámetros del job

**Ejemplo:**
```
"Ejecuta el job 'deploy-frontend' en Rundeck"
```

### execute_dremio_query
Ejecuta query SQL en Dremio.

**Parámetros:**
- `sql` (string): Query SQL

**Ejemplo:**
```
"Ejecuta en Dremio: SELECT * FROM sales WHERE date > '2024-01-01'"
```

### list_atlas_clusters
Lista clusters de MongoDB Atlas.

**Ejemplo:**
```
"Muestra los clusters de MongoDB Atlas"
```

## Notifications

### send_whatsapp
Envía mensaje por WhatsApp.

**Parámetros:**
- `phone` (string): Número de teléfono
- `message` (string): Mensaje

**Ejemplo:**
```
"Envía un WhatsApp a +5491112345678 con el mensaje 'Alerta crítica'"
```

### send_email
Envía email.

**Parámetros:**
- `to` (string): Destinatario
- `subject` (string): Asunto
- `body` (string): Cuerpo del mensaje

**Ejemplo:**
```
"Envía un email a admin@example.com con asunto 'Reporte diario'"
```

## Web & APIs

### web_search
Búsqueda en internet.

**Parámetros:**
- `query` (string): Consulta de búsqueda

**Ejemplo:**
```
"Busca en internet: mejores prácticas Docker"
```

### read_url
Lee contenido de una URL.

**Parámetros:**
- `url` (string): URL a leer

**Ejemplo:**
```
"Lee el contenido de https://example.com/api/docs"
```

### call_rest_api
Llamada REST genérica.

**Parámetros:**
- `url` (string): URL del endpoint
- `method` (string): Método HTTP (GET, POST, etc.)
- `headers` (object, opcional): Headers
- `body` (object, opcional): Cuerpo de la request

**Ejemplo:**
```
"Llama a POST https://api.example.com/users con body: {name: 'John'}"
```

## Dynamic API Learning

### analyze_openapi_spec
Analiza especificación OpenAPI.

**Parámetros:**
- `file_or_url` (string): Archivo o URL del spec

**Ejemplo:**
```
"Analiza el swagger.json de Jira"
```

### generate_tools_from_openapi
Genera tools desde OpenAPI.

**Parámetros:**
- `spec` (object): Especificación OpenAPI

**Ejemplo:**
```
"Genera tools desde esta especificación OpenAPI"
```

## Git Operations

### git_status
Muestra estado del repositorio Git.

**Ejemplo:**
```
"Muestra el estado de Git"
```

### git_commit
Hace commit de cambios.

**Parámetros:**
- `message` (string): Mensaje del commit

**Ejemplo:**
```
"Haz commit con mensaje 'Fix: corrige bug en login'"
```

### git_diff
Muestra diferencias.

**Ejemplo:**
```
"Muestra los cambios en Git"
```

## Code Analysis

### analyze_code
Analiza código fuente.

**Parámetros:**
- `path` (string): Ruta al archivo o directorio

**Ejemplo:**
```
"Analiza el código en src/utils.py"
```

### run_tests
Ejecuta tests.

**Parámetros:**
- `path` (string, opcional): Ruta a los tests
- `framework` (string, opcional): Framework (pytest, jest, etc.)

**Ejemplo:**
```
"Ejecuta los tests con pytest"
```

## Uso de Tools

### Llamada Directa

```
Usuario: "Lista los archivos en /home/user"
Agente: *ejecuta list_directory(path="/home/user")*
```

### Encadenamiento

```
Usuario: "Lee config.yaml y crea un backup"
Agente: *ejecuta read_file(path="config.yaml")*
        *ejecuta write_file(path="config.yaml.bak", content=...)*
```

### Condicional

```
Usuario: "Si hay alertas críticas en Nagios, envíame un WhatsApp"
Agente: *ejecuta check_nagios_alerts(severity="critical")*
        *si hay alertas: send_whatsapp(...)*
```

## Próximos Pasos

- [Crear Tools Personalizados](../development/custom-tools.md)
- [Arquitectura del Sistema de Tools](../architecture/tools-system.md)
