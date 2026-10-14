"""
content_generator.py
====================
This file handles all AI content generation using Ollama (runs 100% locally).

How it works (for beginners):
- Ollama runs a local AI model on YOUR computer (no internet or API key needed!)
- We send the user's topic and chosen language to the local model
- We ask it to return a headline, message, tips, and slogan as JSON
- We parse the JSON and return it as a Python dictionary
- If anything goes wrong, we return an error message
"""

import requests   # For sending HTTP requests to local Ollama server
import json       # For parsing JSON responses
import re         # For text cleanup


# ── Ollama settings ────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"  # Ollama runs on this address
OLLAMA_MODEL = "llama3.2"                              # Lightweight, fast model (~2GB)


def generate_awareness_content(topic: str, language: str, api_key: str = None):
    """
    Generate environmental awareness content using a local Ollama model.

    Parameters:
    -----------
    topic    : The environmental topic, e.g., "Save Trees"
    language : The output language, e.g., "English", "Hindi", "Kannada"
    api_key  : Not used (kept for compatibility with app.py — Ollama is free & local!)

    Returns:
    --------
    (content_dict, error_string)
      - content_dict : Dictionary with keys: headline, message, tips, slogan
      - error_string : None if success, or error message string if failed
    """

    # ── Step 1: Check if Ollama is running ──
    try:
        health = requests.get("http://localhost:11434", timeout=5)
    except requests.exceptions.ConnectionError:
        return None, (
            "Ollama is not running! Please start it by opening a Terminal and running: "
            "ollama serve"
        )
    except Exception as e:
        return None, f"Could not connect to Ollama: {str(e)}"

    # ── Step 2: Build the prompt ──
    prompt = f"""You are an expert environmental awareness educator. Generate content for a poster.

Topic: "{topic}"
Language: {language}

Write ALL content in {language} only. Use simple words everyone can understand.
Be positive, inspiring, and motivating. Keep it concise.

Return ONLY a valid JSON object like this (no explanation, no extra text):

{{
  "headline": "A strong headline about {topic} (max 12 words)",
  "message": "A meaningful message explaining why {topic} matters (2-3 sentences)",
  "tips": [
    "First practical tip anyone can do",
    "Second practical tip about {topic}",
    "Third practical tip about {topic}"
  ],
  "slogan": "A short catchy slogan about {topic} (max 10 words)"
}}

IMPORTANT: Return ONLY the JSON. No markdown, no explanation, no extra text."""

    # ── Step 3: Call local Ollama model ──
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,        # Get full response at once (not streamed)
                "options": {
                    "temperature": 0.7,  # Controls creativity (0=robotic, 1=creative)
                    "num_predict": 500,  # Max tokens to generate
                }
            },
            timeout=120  # Wait up to 2 minutes for the model to respond
        )
        response.raise_for_status()
        raw_text = response.json().get("response", "").strip()

    except requests.exceptions.Timeout:
        return None, (
            "The AI took too long to respond (>2 min). "
            "Try a shorter topic or restart Ollama: ollama serve"
        )
    except requests.exceptions.RequestException as e:
        return None, f"Failed to call Ollama: {str(e)}"

    # ── Step 4: Parse JSON from response ──
    try:
        # Remove markdown code fences if the model added them
        cleaned = re.sub(r"```(?:json)?", "", raw_text).replace("```", "").strip()

        # Find the JSON object in the response (in case there's extra text)
        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not json_match:
            return None, "AI did not return valid JSON. Please try again."

        content = json.loads(json_match.group())

        # Validate required keys
        required_keys = ["headline", "message", "tips", "slogan"]
        for key in required_keys:
            if key not in content:
                return None, f"AI response was missing the '{key}' field. Please try again."

        # Ensure exactly 3 tips
        if not isinstance(content["tips"], list) or len(content["tips"]) < 3:
            return None, "AI did not return 3 tips. Please try again."
        content["tips"] = content["tips"][:3]

        return content, None  # ✅ Success!

    except json.JSONDecodeError as e:
        return None, (
            f"Could not parse the AI response as JSON. Please try again. "
            f"(Technical detail: {str(e)})"
        )
    except Exception as e:
        return None, f"Unexpected error while processing response: {str(e)}"
