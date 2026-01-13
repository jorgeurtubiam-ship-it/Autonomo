"""
Config Routes - Endpoints para configuración
"""

import logging
from fastapi import APIRouter, Depends, HTTPException

from ..models import ConfigUpdate, ConfigResponse
from ..dependencies import get_agent, reconfigure_agent, get_storage_dependency
from agent import AgentCore
from storage import ConversationStorage
import aiohttp

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/", response_model=ConfigResponse)
async def get_config(agent: AgentCore = Depends(get_agent)):
    """
    Obtiene la configuración actual del agente
    """
    # Leer provider del config si existe, sino del LLM actual
    provider = getattr(agent.config, 'llm_provider', None)
    if not provider:
        provider = agent.llm.__class__.__name__.replace("Provider", "").lower()
    
    # Leer modelo del config si existe, sino del LLM actual
    model = getattr(agent.config, 'model', None)
    if not model:
        model = agent.llm.model
    
    return ConfigResponse(
        llm_provider=provider,
        model=model,
        autonomy_level=agent.config.autonomy_level,
        temperature=0.7,  # TODO: Obtener de config real
        max_tokens=4000,  # TODO: Obtener de config real
        tools_count=len(agent.tool_registry.list_tools())
    )


@router.get("/ollama-models")
async def get_ollama_models():
    """
    Obtiene los modelos disponibles en la instancia local de Ollama
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status != 200:
                    return {"models": ["llama3.2:latest"]} # Fallback
                
                data = await response.json()
                models = [model["name"] for model in data.get("models", [])]
                return {"models": models}
    except Exception as e:
        logger.error(f"Error fetching Ollama models: {e}")
        return {"models": ["llama3.2:latest"], "error": str(e)}


@router.put("/")
async def update_config(
    config_update: dict,
    agent: AgentCore = Depends(get_agent),
    storage: ConversationStorage = Depends(get_storage_dependency)
):
    """
    Actualiza la configuración del agente
    
    - **llm_provider**: Proveedor de LLM (openai, anthropic, deepseek, ollama)
    - **model**: Modelo a usar
    - **autonomy_level**: Nivel de autonomía (full, semi, supervised)
    - **temperature**: Temperatura del modelo
    - **max_tokens**: Máximo de tokens
    - **api_keys**: Dict con API keys para los providers
    """
    try:
        # Guardar configuración sin reconfigurar inmediatamente
        # Esto evita errores si no hay API keys todavía
        
        updated_config = {}
        
        if "llm_provider" in config_update:
            provider = config_update["llm_provider"]
            model = config_update.get("model")
            
            # Obtener API key si se proporcionó o de la base de datos
            api_key = None
            if "api_keys" in config_update:
                api_keys = config_update["api_keys"]
                if provider == "openai" and api_keys.get("openai"):
                    api_key = api_keys["openai"]
                elif provider == "anthropic" and api_keys.get("anthropic"):
                    api_key = api_keys["anthropic"]
                elif provider == "deepseek" and api_keys.get("deepseek"):
                    api_key = api_keys["deepseek"]
            
            # Si no se proporcionó, intentar obtener de la base de datos
            if not api_key and provider != "ollama":
                api_key = storage.get_api_key(provider)
            
            # Intentar reconfigurar el LLM
            try:
                agent.reconfigure_llm(
                    provider=provider,
                    model=model,
                    api_key=api_key
                )
                updated_config["llm_provider"] = provider
                updated_config["model"] = agent.config.model
                
            except Exception as e:
                # Si falla la reconfiguración, solo guardar la preferencia
                logger.warning(f"No se pudo reconfigurar LLM: {e}")
                agent.config.llm_provider = provider
                
                if not model:
                    if provider == "ollama":
                        model = "llama3.2:latest"
                    elif provider == "openai":
                        model = "gpt-4"
                    elif provider == "anthropic":
                        model = "claude-3-sonnet-20240229"
                    elif provider == "deepseek":
                        model = "deepseek-chat"
                
                updated_config["llm_provider"] = provider
                updated_config["model"] = model
                agent.config.model = model
                updated_config["warning"] = str(e)
        
        if "api_keys" in config_update:
            # Guardar API keys en la base de datos
            api_keys = config_update["api_keys"]
            if api_keys.get("openai"):
                storage.save_api_key("openai", api_keys["openai"])
                agent.config.openai_api_key = api_keys["openai"]
                updated_config["openai_api_key"] = "***"
            if api_keys.get("anthropic"):
                storage.save_api_key("anthropic", api_keys["anthropic"])
                agent.config.anthropic_api_key = api_keys["anthropic"]
                updated_config["anthropic_api_key"] = "***"
            if api_keys.get("deepseek"):
                storage.save_api_key("deepseek", api_keys["deepseek"])
                agent.config.deepseek_api_key = api_keys["deepseek"]
                updated_config["deepseek_api_key"] = "***"
        
        if "model" in config_update and "llm_provider" not in config_update:
            updated_config["model"] = config_update["model"]
            agent.config.model = config_update["model"]
        
        if "temperature" in config_update:
            updated_config["temperature"] = config_update["temperature"]
        
        if "max_tokens" in config_update:
            updated_config["max_tokens"] = config_update["max_tokens"]

        if "autonomy_level" in config_update:
            level = config_update["autonomy_level"]
            if level in ["full", "semi", "supervised"]:
                agent.config.autonomy_level = level
                updated_config["autonomy_level"] = level
                logger.info(f"Nivel de autonomía actualizado a: {level}")
            else:
                logger.warning(f"Nivel de autonomía inválido: {level}")
        
        return {
            "status": "success",
            "message": "Configuración actualizada",
            "config": updated_config
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando configuración: {str(e)}"
        )
