# Aprendizaje Dinámico de APIs

El agente puede aprender cualquier API automáticamente analizando su documentación.

## ¿Cómo Funciona?

1. **Proporcionas documentación** (OpenAPI/Swagger, README, docs)
2. **El agente la analiza** y extrae endpoints, parámetros, autenticación
3. **Genera tools dinámicamente** para cada endpoint
4. **Los registra** y puede usarlos inmediatamente

## Formatos Soportados

- **OpenAPI/Swagger** (2.0, 3.0, 3.1) - Recomendado
- **Postman Collections**
- **Markdown/README** con ejemplos de API
- **PDF** con documentación
- **URLs** a documentación online

## Ejemplo: Aprender API de Jira

### 1. Proporcionar Documentación

```
Usuario: "Aquí está el swagger.json de Jira"
        [adjunta archivo o URL]
```

### 2. El Agente Analiza

```
Agente: "Analizando especificación OpenAPI de Jira..."
        
        "Encontré 47 endpoints:
         - POST /rest/api/3/issue - Crear issue
         - GET /rest/api/3/project - Listar proyectos
         - PUT /rest/api/3/issue/{issueIdOrKey} - Actualizar issue
         ..."
        
        "Generando tools..."
        
        "Listo. Ahora puedo interactuar con Jira."
```

### 3. Usar la API

```
Usuario: "Crea un issue en el proyecto DEVOPS con título 'Bug en login'"

Agente: *ejecuta create_jira_issue()*
        
        "Issue creado:
         - Key: DEVOPS-123
         - URL: https://jira.example.com/browse/DEVOPS-123"
```

## Comandos Disponibles

### Analizar OpenAPI/Swagger

```
"Analiza esta especificación OpenAPI: [URL o archivo]"
"Aprende la API desde este swagger.json"
```

### Analizar Documentación de Texto

```
"Lee esta documentación de API: [URL]"
"Aquí está el README de la API [adjunta archivo]"
```

### Probar Endpoint

```
"Prueba el endpoint GET /api/users"
"Llama a POST /api/products con estos datos: {...}"
```

### Listar APIs Aprendidas

```
"¿Qué APIs conoces?"
"Muéstrame los endpoints de la API de Jira"
```

## Ejemplo Completo: API Personalizada

### Swagger Spec

```yaml
openapi: 3.0.0
info:
  title: Mi API Interna
  version: 1.0.0
servers:
  - url: https://api.miempresa.com/v1
paths:
  /users:
    get:
      summary: Listar usuarios
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: Lista de usuarios
  /users/{id}:
    get:
      summary: Obtener usuario
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
security:
  - bearerAuth: []
```

### Conversación

```
Usuario: "Analiza este swagger.yaml"
        [adjunta archivo]

Agente: "API aprendida: Mi API Interna v1.0.0
         
         Tools generados:
         - get_users(limit=None)
         - get_user_by_id(id)
         
         Autenticación: Bearer token
         ¿Cuál es tu token de autenticación?"

Usuario: "El token es: abc123xyz"

Agente: "Token configurado. Listo para usar la API."

Usuario: "Lista los primeros 10 usuarios"

Agente: *ejecuta get_users(limit=10)*
        
        "Encontré 10 usuarios:
         1. John Doe (ID: user_001)
         2. Jane Smith (ID: user_002)
         ..."

Usuario: "Obtén los detalles del usuario user_001"

Agente: *ejecuta get_user_by_id(id="user_001")*
        
        "Usuario user_001:
         - Nombre: John Doe
         - Email: john@example.com
         - Rol: Admin"
```

## Autenticación

El agente soporta múltiples métodos de autenticación:

### API Key

```yaml
securitySchemes:
  apiKey:
    type: apiKey
    in: header
    name: X-API-Key
```

```
Usuario: "La API key es: sk-abc123"
Agente: "API key configurada"
```

### Bearer Token (JWT)

```yaml
securitySchemes:
  bearerAuth:
    type: http
    scheme: bearer
```

```
Usuario: "El token es: eyJhbGc..."
Agente: "Bearer token configurado"
```

### OAuth 2.0

```yaml
securitySchemes:
  oauth2:
    type: oauth2
    flows:
      authorizationCode:
        authorizationUrl: https://api.example.com/oauth/authorize
        tokenUrl: https://api.example.com/oauth/token
```

```
Usuario: "Usa OAuth con client_id=xxx y client_secret=yyy"
Agente: "Iniciando flujo OAuth... [genera URL de autorización]"
```

### Basic Auth

```yaml
securitySchemes:
  basicAuth:
    type: http
    scheme: basic
```

```
Usuario: "Usuario: admin, Password: pass123"
Agente: "Credenciales configuradas"
```

## Sistema RAG para Documentación Larga

Para documentación extensa (PDFs, sitios web completos), el agente usa RAG:

### 1. Indexación

```
Usuario: "Indexa toda la documentación de esta URL: https://docs.example.com"

Agente: "Descargando y procesando documentación..."
        "Creando embeddings..."
        "Indexado en vector database"
        "Listo. Puedo responder preguntas sobre la documentación."
```

### 2. Búsqueda Semántica

```
Usuario: "¿Cómo autentico requests en esta API?"

Agente: *busca en vector DB*
        
        "Según la documentación, hay 3 métodos:
         1. API Key en header X-API-Key
         2. Bearer token en Authorization
         3. OAuth 2.0 con client credentials
         
         [Muestra fragmentos relevantes de la documentación]"
```

## Persistencia

Las APIs aprendidas se guardan y están disponibles en futuras sesiones:

```
Usuario: [Nueva conversación]
        "¿Qué APIs conoces?"

Agente: "Tengo configuradas:
         1. Jira API (47 endpoints)
         2. Mi API Interna (2 endpoints)
         3. GitHub API (120 endpoints)
         
         ¿Cuál quieres usar?"
```

## Limitaciones

- **Calidad de documentación**: Mejores resultados con OpenAPI bien documentado
- **APIs complejas**: Puede requerir configuración manual para casos edge
- **Rate limiting**: Respeta límites de la API
- **Autenticación compleja**: OAuth con múltiples pasos puede requerir intervención

## Mejores Prácticas

1. **Usa OpenAPI cuando sea posible** - Más preciso
2. **Proporciona ejemplos** - Ayuda al agente a entender
3. **Especifica autenticación** - Evita errores
4. **Prueba endpoints primero** - Valida antes de usar en producción
5. **Documenta casos especiales** - El agente aprenderá

## Próximos Pasos

- [Referencia de Tools](../api/tools-reference.md)
- [Arquitectura del Sistema RAG](../architecture/dynamic-learning.md)
