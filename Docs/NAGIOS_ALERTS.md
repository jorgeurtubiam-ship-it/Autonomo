# 🔍 Guía para Ver Alertas de Nagios

## 📋 Información de Acceso

- **URL:** http://localhost:8080/nagios/
- **Usuario:** `nagiosadmin`
- **Contraseña:** `nagios@2025`

---

## 🌐 Opción 1: Navegador Web (Recomendado)

### Paso a Paso:

1. **Abrir Nagios:**
   ```
   open http://localhost:8080/nagios/
   ```
   O abre tu navegador y ve a: `http://localhost:8080/nagios/`

2. **Login:**
   - Usuario: `nagiosadmin`
   - Contraseña: `nagios@2025`

3. **Ver Alertas:**
   - **Servicios:** Click en "Current Status" → "Services"
   - **Hosts:** Click en "Current Status" → "Hosts"
   - **Mapa:** Click en "Map" para vista gráfica

### Estados de Color:
- 🟢 **Verde (OK):** Todo funciona bien
- 🟡 **Amarillo (WARNING):** Advertencia, requiere atención
- 🔴 **Rojo (CRITICAL):** Crítico, requiere acción inmediata
- ⚪ **Gris (UNKNOWN):** Estado desconocido

---

## 💻 Opción 2: Línea de Comandos (curl)

### Ver Todos los Servicios:
```bash
curl -u nagiosadmin:nagios@2025 \
  http://localhost:8080/nagios/cgi-bin/status.cgi?host=all
```

### Solo Alertas Críticas:
```bash
curl -u nagiosadmin:nagios@2025 \
  "http://localhost:8080/nagios/cgi-bin/status.cgi?host=all&servicestatustypes=16"
```

### Solo Warnings:
```bash
curl -u nagiosadmin:nagios@2025 \
  "http://localhost:8080/nagios/cgi-bin/status.cgi?host=all&servicestatustypes=4"
```

### Ver Estado de Host Específico:
```bash
curl -u nagiosadmin:nagios@2025 \
  "http://localhost:8080/nagios/cgi-bin/status.cgi?host=localhost"
```

---

## 🐍 Opción 3: Script Python

### Ejecutar el Script:
```bash
# Instalar dependencias
pip install requests beautifulsoup4

# Ejecutar
python3 scripts/nagios_alerts.py
```

### Características del Script:
- ✅ Muestra resumen de estados (OK, WARNING, CRITICAL)
- ✅ Lista problemas detectados
- ✅ Formato bonito con emojis
- ✅ Fácil de personalizar

---

## 📊 Opción 4: API JSON (Si está habilitada)

Algunos endpoints de Nagios pueden devolver JSON:

```bash
# Intentar obtener JSON
curl -u nagiosadmin:nagios@2025 \
  -H "Accept: application/json" \
  http://localhost:8080/nagios/cgi-bin/statusjson.cgi
```

**Nota:** Esto depende de si Nagios tiene el módulo JSON habilitado.

---

## 🔔 Tipos de Alertas

### Por Código de Estado:
- `servicestatustypes=2` - OK
- `servicestatustypes=4` - WARNING
- `servicestatustypes=8` - UNKNOWN
- `servicestatustypes=16` - CRITICAL
- `servicestatustypes=28` - Todos los problemas (4+8+16)

### Ejemplos:

**Solo problemas:**
```bash
curl -u nagiosadmin:nagios@2025 \
  "http://localhost:8080/nagios/cgi-bin/status.cgi?host=all&servicestatustypes=28"
```

**Solo servicios OK:**
```bash
curl -u nagiosadmin:nagios@2025 \
  "http://localhost:8080/nagios/cgi-bin/status.cgi?host=all&servicestatustypes=2"
```

---

## 🎯 URLs Útiles de Nagios

| Función | URL |
|---------|-----|
| Dashboard | http://localhost:8080/nagios/ |
| Servicios | http://localhost:8080/nagios/cgi-bin/status.cgi?host=all |
| Hosts | http://localhost:8080/nagios/cgi-bin/status.cgi?hostgroup=all&style=hostdetail |
| Mapa | http://localhost:8080/nagios/cgi-bin/statusmap.cgi |
| Historial | http://localhost:8080/nagios/cgi-bin/history.cgi |
| Reportes | http://localhost:8080/nagios/cgi-bin/avail.cgi |

---

## 🔧 Troubleshooting

### No puedo conectar:
```bash
# Verificar que Nagios está corriendo
curl http://localhost:8080/nagios/

# Verificar puerto
lsof -i :8080
```

### Error de autenticación:
- Verifica usuario: `nagiosadmin`
- Verifica contraseña: `nagios@2025`
- Prueba en navegador primero

### Respuesta vacía:
- Nagios puede estar iniciando
- Espera 30 segundos y reintenta

---

## 💡 Recomendación

**Para uso diario:** Usa el **navegador web** (Opción 1)
- Más visual
- Más fácil de navegar
- Gráficos y mapas

**Para automatización:** Usa **curl** o **Python** (Opciones 2-3)
- Integrable en scripts
- Automatizable
- Parseable

---

## 📝 Ejemplo Completo

```bash
# 1. Abrir Nagios en navegador
open http://localhost:8080/nagios/

# 2. O ver en terminal
curl -u nagiosadmin:nagios@2025 \
  http://localhost:8080/nagios/cgi-bin/status.cgi?host=all \
  | grep -E "(OK|WARNING|CRITICAL)" | head -20

# 3. O usar el script Python
python3 scripts/nagios_alerts.py
```

¡Elige el método que prefieras! 🚀
