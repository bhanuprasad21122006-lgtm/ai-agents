"""Interactive / automated tool to fetch available Gemini models from the API and update project configuration."""

import os
import sys
from dotenv import load_dotenv

# Fix Windows console emoji printing issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from utils.models import (
    fetch_available_models,
    detect_best_model,
    update_env_file,
    PREFERRED_MODELS,
    DEFAULT_FALLBACK_MODEL,
)

def main():
    print("==================================================")
    print("  GEMINI API MODEL AUTO-UPDATER & DISCOVERY TOOL  ")
    print("==================================================\n")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        api_key = input("🔑 Enter your Gemini API Key to fetch models from API:\n> ").strip()
        if not api_key:
            print("❌ No API key provided. Exiting.")
            return

    print("\n🔍 Contacting Google Gemini API...")
    available = fetch_available_models(api_key)

    if not available:
        print("⚠️ Could not fetch models from API (invalid key, rate limit, or offline).")
        print(f"👉 Defaulting to recommended fallback model: {DEFAULT_FALLBACK_MODEL}")
        best_model = DEFAULT_FALLBACK_MODEL
    else:
        print(f"✅ Successfully found {len(available)} Gemini model(s) supporting content generation:\n")
        for i, m in enumerate(available, 1):
            marker = " (preferred)" if m in PREFERRED_MODELS[:3] else ""
            print(f"  [{i}] {m}{marker}")

        best_model = detect_best_model(api_key)
        print(f"\n🎯 Recommended Model: {best_model}")

    # Prompt or auto-update .env
    env_file = ".env"
    if not os.path.exists(env_file):
        env_file = ".env.example"

    print(f"\n💾 Updating {env_file} with GEMINI_MODEL={best_model}...")
    if update_env_file(best_model, env_file):
        print(f"✅ Successfully updated {env_file} to use {best_model}!")
    else:
        print(f"ℹ️ Set GEMINI_MODEL={best_model} in your .env file.")

    print("\nAll 14 agents will now automatically use this model. You're all set!")

if __name__ == "__main__":
    main()
