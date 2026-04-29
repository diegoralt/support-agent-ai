#!/bin/bash

# setup-secrets.sh - Interactive script to configure .env file
# Flexible: only requires secrets you have available
# Can be run multiple times to add more secrets

set -e

ENV_FILE=".env"
ENV_EXAMPLE=".env.example"

echo "🔐 Setup de Secrets - Support Agent AI"
echo "=========================================="
echo ""
echo "Este script te ayuda a configurar tus credenciales locales."
echo "Solo proporciona los valores que tengas disponibles."
echo "Puedes ejecutar este script múltiples veces para agregar más valores."
echo ""

# Check if .env exists
if [ -f "$ENV_FILE" ]; then
    echo "⚠️  Archivo .env ya existe"
    echo "Variables actuales: $(grep -c "=" "$ENV_FILE" 2>/dev/null || echo "0")"
    read -p "¿Deseas actualizar/agregar valores? (y/n): " -n 1 -r UPDATE
    echo
    if [[ ! $UPDATE =~ ^[Yy]$ ]]; then
        echo "Abortando..."
        exit 0
    fi
else
    # Create .env from .env.example if it exists
    if [ -f "$ENV_EXAMPLE" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        echo "✅ Archivo .env creado desde .env.example"
    else
        touch "$ENV_FILE"
        echo "✅ Archivo .env creado (vacío)"
    fi
fi

echo ""
echo "Ingresa tus credenciales (deja vacío para saltear):"
echo "---"

# Function to update or add a variable
update_env_var() {
    local var_name=$1
    local var_description=$2
    local current_value=$(grep "^${var_name}=" "$ENV_FILE" 2>/dev/null | cut -d '=' -f2 || echo "")

    if [ -n "$current_value" ]; then
        echo ""
        echo "📍 $var_name (actual: ${current_value:0:20}...)"
    else
        echo ""
        echo "📝 $var_name"
    fi

    read -p "   $var_description: " -r input_value

    if [ -n "$input_value" ]; then
        if grep -q "^${var_name}=" "$ENV_FILE"; then
            # Update existing variable
            sed -i.bak "s|^${var_name}=.*|${var_name}=${input_value}|" "$ENV_FILE"
            rm -f "$ENV_FILE.bak"
        else
            # Add new variable
            echo "${var_name}=${input_value}" >> "$ENV_FILE"
        fi
        echo "   ✅ Actualizado"
    else
        echo "   ⏭️  Saltado"
    fi
}

# Ask for each secret
update_env_var "SUPABASE_URL" "URL del proyecto Supabase (https://xxxxx.supabase.co)"
update_env_var "SUPABASE_ANON_KEY" "API Key Anon de Supabase"
update_env_var "SUPABASE_SERVICE_ROLE_KEY" "Service Role Key de Supabase"
update_env_var "OPENAI_API_KEY" "API Key de OpenAI (sk-...)"
update_env_var "OPENAI_MODEL" "Modelo OpenAI a usar (ej: gpt-4-mini)"
update_env_var "N8N_WEBHOOK_URL" "URL del webhook de n8n (opcional)"
update_env_var "N8N_WEBHOOK_AUTH_TOKEN" "Token de autenticación n8n (opcional)"
update_env_var "ENVIRONMENT" "Ambiente (development/production)"

echo ""
echo "---"
echo "✅ Configuración completada"
echo ""
echo "📊 Variables configuradas en .env:"
TOTAL=$(grep -c "=" "$ENV_FILE" 2>/dev/null || echo "0")
echo "   Total de variables: $TOTAL"
echo ""
echo "🔒 Recuerda: NUNCA commitees .env a git"
echo "✔️  El archivo .env está en .gitignore y es seguro"
echo ""
echo "📖 Más información: lee SECRETS-SETUP.md"
