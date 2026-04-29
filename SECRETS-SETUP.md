# 🔐 Guía de Configuración de Secrets

Este archivo te guía sobre cómo obtener y configurar tus credenciales locales de forma segura.

## ⚠️ IMPORTANTE

- **Nunca** commitees tu `.env` a git (está en `.gitignore`)
- **Solo** usa `.env.example` como referencia
- **Siempre** guarda tus credenciales en `/.env` (local, no compartible)

---

## 📋 Credenciales Necesarias

### 1. SUPABASE_URL
**Dónde obtenerla:**
1. Ve a https://supabase.com/dashboard
2. Selecciona tu proyecto: `support-agent-ai`
3. Click en **Settings** (rueda engranaje)
4. Copia en la sección **API**: **Project URL**

**Formato esperado:**
```
SUPABASE_URL=https://xxxxx.supabase.co
```

**Ejemplo:**
```
SUPABASE_URL=https://abcdef123456.supabase.co
```

---

### 2. SUPABASE_ANON_KEY
**Dónde obtenerla:**
1. Mismo lugar: Settings → API
2. Copia el campo **API Key (anon)**
3. Es una cadena larga (aprox 120+ caracteres)

**Formato esperado:**
```
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 3. SUPABASE_SERVICE_ROLE_KEY
**Dónde obtenerla:**
1. Settings → API
2. Copia el campo **API Key (service_role)** (con más permisos)
3. También es una cadena larga

**Formato esperado:**
```
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 4. OPENAI_API_KEY
**Dónde obtenerla:**
1. Ve a https://platform.openai.com/account/api-keys
2. Click en **Create new secret key**
3. Copia la clave (aparece solo una vez)
4. Formato: `sk-...`

**Formato esperado:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxx...
```

---

### 5. OPENAI_MODEL
**Dónde obtenerla:**
- Modelo a usar: `gpt-4-mini` (recomendado para este proyecto)
- Opciones: `gpt-4-mini`, `gpt-4-turbo`, etc.

**Formato esperado:**
```
OPENAI_MODEL=gpt-4-mini
```

---

### 6. N8N_WEBHOOK_URL (Opcional)
**Dónde obtenerla:**
1. Ve a tu n8n en Railway
2. En Webhooks, copia la URL completa
3. Formato: `https://[tu-railway-n8n].com/webhook/support-tickets`

**Formato esperado:**
```
N8N_WEBHOOK_URL=https://your-railway-n8n.com/webhook/support-tickets
```

---

### 7. N8N_WEBHOOK_AUTH_TOKEN (Opcional)
**Dónde obtenerla:**
1. En n8n, genera un Bearer Token
2. Cópialo de forma segura

**Formato esperado:**
```
N8N_WEBHOOK_AUTH_TOKEN=your-token-here
```

---

### 8. ENVIRONMENT
**Valores:**
- `development` (recomendado para local)
- `production`

**Formato esperado:**
```
ENVIRONMENT=development
```

---

## 🛠️ Configuración Local (Opción A: Automática - Recomendado)

### Step 1: Ejecutar el script
```bash
chmod +x setup-secrets.sh
./setup-secrets.sh
```

El script te pedirá cada valor interactivamente. **Solo proporciona los que tengas disponibles.**

### Step 2: Responder las preguntas
- Deja vacío para saltear un valor
- Puedes ejecutar el script múltiples veces para agregar más valores después

### Step 3: Verificar
```bash
# Ver cantidad de variables configuradas
grep "=" .env
```

---

## 🛠️ Configuración Local (Opción B: Manual)

### Step 1: Copiar template
```bash
cp .env.example .env
```

### Step 2: Editar archivo
```bash
# Con nano
nano .env

# Con VS Code
code .env

# Con vim
vim .env
```

### Step 3: Reemplazar valores
```
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-anon-key-aqui
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key-aqui
OPENAI_API_KEY=sk-proj-tu-openai-key-aqui
OPENAI_MODEL=gpt-4-mini
ENVIRONMENT=development
```

### Step 4: Guardar y cerrar
- Nano: `Ctrl+S`, `Ctrl+X`
- VS Code: `Ctrl+S`
- Vim: `:wq`

---

## ✅ Verificación

Para confirmar que está configurado correctamente:

```bash
# Verifica que el archivo existe
ls -la .env

# Verifica que contiene valores
grep "=" .env

# Verifica contador de variables
echo "Total de variables: $(grep -c "=" .env)"
```

---

## 🔒 Seguridad - Buenas Prácticas

✅ **Está bien:**
- Guardar credenciales en `.env` local
- Compartir `.env.example` sin valores reales
- Usar credenciales en desarrollo local
- Ejecutar script setup-secrets.sh múltiples veces
- Actualizar valores cuando cambien

❌ **NUNCA hagas:**
- Commitear `.env` a git
- Compartir tu `.env` por email/Slack/Discord
- Pegar credenciales en código o comments
- Subir `.env` a repositorios públicos
- Guardar `.env` en control de versiones

---

## 🔄 Iteración - Agregar Nuevos Secrets

Conforme el proyecto avanza, se pueden agregar nuevas variables:

1. Ejecuta nuevamente: `./setup-secrets.sh`
2. El script detectará valores existentes
3. Agrega los nuevos valores solo cuando se pida
4. Las variables antiguas se mantienen intactas

---

## 📝 Notas

- Este archivo (`SECRETS-SETUP.md`) **SÍ está en git** (es documentación)
- El archivo `.env` **NO está en git** (está en `.gitignore`)
- El archivo `.env.example` **SÍ está en git** (es template sin valores)
- Los scripts **SÍ están en git** (son herramientas públicas)

---

**Última actualización:** 2026-04-28  
**Versión:** 1.0  
**Estado:** Activo - Se itera conforme avanza el proyecto
