# -*- coding: utf-8 -*-
"""
List the Gemini models this specific account/API key can actually call,
instead of guessing model name strings one at a time and hitting 404s.

Run: python3 list_available_models.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print(f"{'Model name':40s} {'Supports generateContent'}")
print("-" * 70)

for m in client.models.list():
    name = getattr(m, "name", str(m))
    actions = (
        getattr(m, "supported_actions", None)
        or getattr(m, "supported_generation_methods", None)
        or []
    )
    supports_generate = any("generateContent" in str(a) or "generate_content" in str(a) for a in actions)
    if supports_generate:
        print(f"{name:40s} {'yes' if supports_generate else 'no'}")

print(
    "\nLook for a plain/flagship name (e.g. containing 'flash' with no extra "
    "decimal-point suffix like '3.5' or '3.6') rather than the newest preview "
    "point-release -- those get throttled hardest. Once you pick one, check "
    "its quota at https://ai.dev/rate-limit BEFORE plugging it into "
    "crewai_researcher_agent.py, so we don't repeat this cycle a third time."
)