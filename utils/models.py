"""Centralized model discovery, resolution, and configuration for Gemini agents."""

import os
from typing import List, Optional

DEFAULT_FALLBACK_MODEL = "gemini-3.6-flash"

# Models that return 404 or are obsolete on this account tier
DISALLOWED_MODELS = {
    "gemini-2.0-flash",
    "gemini-2.0-pro",
    "gemini-2.5-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
}

# Model preference hierarchy (highest priority first)
PREFERRED_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash",
]

_ACTIVE_MODEL: Optional[str] = None


def fetch_available_models(api_key: Optional[str] = None) -> List[str]:
    """Fetch all available models that support content generation from the Gemini API."""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key or key == "your_gemini_api_key_here":
        return []

    try:
        from google import genai
        client = genai.Client(api_key=key)
        
        available = []
        for model in client.models.list():
            # Extract clean model name, removing 'models/' prefix if present
            raw_name = getattr(model, "name", "")
            clean_name = raw_name.replace("models/", "").strip()
            
            # Check supported actions if available
            supported_actions = getattr(model, "supported_actions", None) or []
            if not supported_actions or "generateContent" in supported_actions or "generate_content" in supported_actions:
                if clean_name and "gemini" in clean_name.lower() and clean_name.lower() not in DISALLOWED_MODELS:
                    available.append(clean_name)
                    
        return available
    except Exception:
        # API unreachable, invalid key, or offline
        return []


def detect_best_model(api_key: Optional[str] = None) -> str:
    """Query the Gemini API to detect and return the best available model for the given key."""
    # 1. If GEMINI_MODEL is explicitly set in environment and not 'auto', respect it
    env_model = os.getenv("GEMINI_MODEL", "").strip()
    if env_model and env_model.lower() != "auto":
        return env_model

    # 2. Query Gemini API for live available models
    available_models = fetch_available_models(api_key)
    
    if available_models:
        # Check against prioritized list
        for preferred in PREFERRED_MODELS:
            for available in available_models:
                if available.lower() == preferred.lower():
                    return available
        
        # If no preferred match, pick first available Gemini model
        return available_models[0]

    # 3. Fallback default if API query failed or returned no results
    return DEFAULT_FALLBACK_MODEL


def set_active_model(model_name: str) -> None:
    """Set the globally active model for all agents."""
    global _ACTIVE_MODEL
    _ACTIVE_MODEL = model_name
    os.environ["GEMINI_MODEL"] = model_name


def get_active_model() -> str:
    """Get the currently active model name. Resolves dynamically if not already cached."""
    global _ACTIVE_MODEL
    if _ACTIVE_MODEL:
        return _ACTIVE_MODEL

    env_model = os.getenv("GEMINI_MODEL", "").strip()
    if env_model and env_model.lower() != "auto":
        _ACTIVE_MODEL = env_model
        return _ACTIVE_MODEL

    # If API key is present in environment, attempt detection
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_gemini_api_key_here":
        _ACTIVE_MODEL = detect_best_model(api_key)
        return _ACTIVE_MODEL

    return DEFAULT_FALLBACK_MODEL


def resolve_and_set_model(api_key: Optional[str] = None) -> str:
    """Resolve the best model from the API or environment and cache it as active."""
    resolved = detect_best_model(api_key)
    set_active_model(resolved)
    return resolved


def update_env_file(model_name: str, env_path: str = ".env") -> bool:
    """Update or append GEMINI_MODEL in the specified .env file."""
    if not os.path.exists(env_path):
        return False

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()

        line = f"GEMINI_MODEL={model_name}"
        if "GEMINI_MODEL=" in content:
            import re
            content = re.sub(r"GEMINI_MODEL=.*", line, content)
        else:
            content = content.rstrip() + f"\n{line}\n"

        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False
