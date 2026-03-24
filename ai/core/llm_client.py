#!/usr/bin/env python3
"""
llm_client.py — LLM Interface (Groq with 4-key rotation + comprehensive AI logging)
=======================================================================================
Features:
  - 4 Groq API keys loaded from groq_key.txt, randomly rotated per call
  - Rate-limit aware: if one key fails with 429, auto-retries with next key
  - Full AI logging: every call → JSON file + Markdown file (separate folders)
    Naming: 0000_20260322_001500_key1_llama-3.3-70b-versatile.{json,md}
  - Default model: llama-3.3-70b-versatile (fastest & smartest on free Groq)
  - Supports multi-turn conversations (messages list)

Backends supported:
  - "groq"   : Groq cloud (FREE tier, fast, multi-key)  ← DEFAULT
  - "ollama" : Local Ollama (private, needs GPU)
  - "gemini" : Google Gemini (free tier)
"""

import json
import os
import re
import time
import random
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Optional

# ─── CONFIGURATION ────────────────────────────────────────────────────────────

BACKEND = os.environ.get("FRAUDSENSE_BACKEND", "groq")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral:7b")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = "gemini-1.5-flash"

# Model — user can override per-request or via env
GROQ_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3-32b") # 32B reasoning model — best quality on free tier

MAX_TOKENS = 8192       # qwen3-32b supports long context; needed for rich forensic reports
TEMPERATURE = 0.2       # Slightly higher for more natural NLP responses

# ─── AI LOGGING ───────────────────────────────────────────────────────────────

_BASE_DIR = Path(__file__).parent.parent       # ai/ folder
_LOG_DIR = _BASE_DIR / "logs"
_LOG_JSON_DIR = _LOG_DIR / "json"
_LOG_MD_DIR = _LOG_DIR / "md"

def _ensure_log_dirs():
    _LOG_JSON_DIR.mkdir(parents=True, exist_ok=True)
    _LOG_MD_DIR.mkdir(parents=True, exist_ok=True)

def _get_seq() -> int:
    """Return next log sequence number (reads existing files to find max)."""
    _ensure_log_dirs()
    max_seq = -1
    for f in list(_LOG_JSON_DIR.glob("*.json")) + list(_LOG_MD_DIR.glob("*.md")):
        try:
            n = int(f.stem.split("_")[0])
            if n > max_seq:
                max_seq = n
        except (ValueError, IndexError):
            pass
    return max_seq + 1

def _safe_model_name(model: str) -> str:
    """Make model name filesystem-safe."""
    return re.sub(r"[^a-zA-Z0-9\-]", "-", model)[:40]

def _strip_think_tags(text: str) -> str:
    """
    Remove <think>...</think> chain-of-thought blocks that reasoning models
    (like qwen3) emit internally. Keeps only the actual answer.
    """
    import re as _re
    # Remove <think> blocks (may be multi-line)
    cleaned = _re.sub(r'<think>[\s\S]*?</think>', '', text, flags=_re.IGNORECASE)
    # Also strip orphaned opening tags
    cleaned = _re.sub(r'</?think>', '', cleaned, flags=_re.IGNORECASE)
    return cleaned.strip()

def _write_ai_log(seq: int, key_num: int, model: str, messages_sent: list,
                  response_text: str, success: bool, error: str,
                  elapsed_ms: int, backend: str):
    """Write comprehensive AI log to both JSON and MD files."""
    try:
        _ensure_log_dirs()
        now = datetime.now()
        ts = now.strftime("%Y%m%d_%H%M%S")
        model_safe = _safe_model_name(model)
        base_name = f"{seq:04d}_{ts}_key{key_num}_{model_safe}"

        # ── Extract prompt parts ──────────────────────────────────────────────
        system_msg = next((m["content"] for m in messages_sent if m.get("role") == "system"), "")
        user_msgs = [m for m in messages_sent if m.get("role") == "user"]
        assistant_msgs = [m for m in messages_sent if m.get("role") == "assistant"]

        # ── JSON LOG ─────────────────────────────────────────────────────────
        log_entry = {
            "seq": seq,
            "timestamp": now.isoformat(),
            "backend": backend,
            "model": model,
            "key_number": key_num,
            "success": success,
            "elapsed_ms": elapsed_ms,
            "error": error or None,
            "messages_sent": messages_sent,
            "response": response_text,
            "meta": {
                "system_prompt_chars": len(system_msg),
                "user_messages": len(user_msgs),
                "history_turns": len(assistant_msgs),
                "response_chars": len(response_text),
                "total_messages": len(messages_sent)
            }
        }
        json_path = _LOG_JSON_DIR / f"{base_name}.json"
        json_path.write_text(json.dumps(log_entry, indent=2, ensure_ascii=False), encoding="utf-8")

        # ── MARKDOWN LOG ─────────────────────────────────────────────────────
        status_icon = "✅" if success else "❌"
        md = f"""# {status_icon} AI Call #{seq:04d}

**Date/Time:** {now.strftime('%Y-%m-%d %H:%M:%S')}
**Backend:** {backend} | **Model:** `{model}` | **Key:** #{key_num}
**Status:** {"SUCCESS" if success else f"FAILED — {error}"}
**Elapsed:** {elapsed_ms}ms | **Response length:** {len(response_text)} chars

---

## 🔧 System Prompt

```
{system_msg[:3000]}{"..." if len(system_msg) > 3000 else ""}
```

---

## 💬 Conversation History ({len(assistant_msgs)} prior turns)

"""
        for i, m in enumerate(messages_sent):
            role = m.get("role", "?")
            content = m.get("content", "")
            if role == "system":
                continue
            icon = "👤" if role == "user" else "🤖"
            label = "USER" if role == "user" else "ASSISTANT"
            md += f"### {icon} {label} (message {i})\n\n"
            md += f"```\n{content[:2000]}{'...' if len(content) > 2000 else ''}\n```\n\n"

        md += f"""---

## 🤖 AI Response

```
{response_text[:5000]}{"..." if len(response_text) > 5000 else ""}
```

---

## 📊 Metadata

| Field | Value |
|-------|-------|
| Sequence | #{seq:04d} |
| Timestamp | {now.isoformat()} |
| Model | {model} |
| Key # | {key_num} |
| Elapsed | {elapsed_ms}ms |
| System prompt chars | {len(system_msg)} |
| User messages | {len(user_msgs)} |
| History turns | {len(assistant_msgs)} |
| Response chars | {len(response_text)} |
| Success | {success} |
"""
        md_path = _LOG_MD_DIR / f"{base_name}.md"
        md_path.write_text(md, encoding="utf-8")

    except Exception as log_err:
        print(f"   ⚠️  AI log write failed: {log_err}")

# ─── MULTI-KEY MANAGER ────────────────────────────────────────────────────────

def _load_all_groq_keys() -> list:
    """
    Load ALL Groq API keys from groq_key.txt (one per line) + .env + env var.
    Returns list of (key_index, api_key) tuples.
    """
    keys = []
    base_dir = _BASE_DIR

    # 1. ai/.env — single key
    env_file = base_dir / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("GROQ_API_KEY="):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
                if k and not k.startswith("PASTE") and k not in [key for key in keys]:
                    keys.append(k)

    # 2. ai/groq_key.txt — one key per line (supports multiple!)
    key_file = base_dir / "groq_key.txt"
    if key_file.exists():
        for line in key_file.read_text(encoding="utf-8").splitlines():
            k = line.strip()
            if k and not k.startswith("PASTE") and k.startswith("gsk_") and k not in keys:
                keys.append(k)

    # 3. System env var
    env_key = os.environ.get("GROQ_API_KEY", "").strip()
    if env_key and env_key not in keys:
        keys.append(env_key)

    return keys

# Load all keys at startup
_ALL_GROQ_KEYS = _load_all_groq_keys()
GROQ_API_KEY = _ALL_GROQ_KEYS[0] if _ALL_GROQ_KEYS else ""  # First key for backward compat

def _pick_groq_key() -> tuple:
    """
    Pick a random Groq API key from the pool.
    Returns (key_index_1based, api_key).
    """
    if not _ALL_GROQ_KEYS:
        return (0, "")
    idx = random.randint(0, len(_ALL_GROQ_KEYS) - 1)
    return (idx + 1, _ALL_GROQ_KEYS[idx])

def _get_next_key(exclude_idx: int) -> tuple:
    """Get next key excluding the failed one."""
    available = [(i, k) for i, k in enumerate(_ALL_GROQ_KEYS) if i != (exclude_idx - 1)]
    if not available:
        return (exclude_idx, _ALL_GROQ_KEYS[exclude_idx - 1] if _ALL_GROQ_KEYS else "")
    i, k = random.choice(available)
    return (i + 1, k)

# ─── OLLAMA ───────────────────────────────────────────────────────────────────

def call_ollama(prompt: str, system: str = None, model_override: Optional[str] = None) -> dict:
    """Call local Ollama instance."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": model_override or OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": TEMPERATURE, "num_predict": MAX_TOKENS}
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data.get("message", {}).get("content", "")
            return {"success": True, "text": text, "model": (model_override or OLLAMA_MODEL), "backend": "ollama"}
    except urllib.error.URLError:
        return {"success": False, "error": f"Ollama not reachable at {OLLAMA_URL}. Run: ollama serve", "text": "", "backend": "ollama"}
    except Exception as e:
        return {"success": False, "error": str(e), "text": "", "backend": "ollama"}

# ─── GROQ (multi-key rotation + retry + full logging) ────────────────────────

def call_groq(prompt: str, system: str = None, model_override: Optional[str] = None,
              messages: list = None) -> dict:
    """
    Call Groq API with:
    - Random key selection from the pool (up to 4 keys)
    - Auto-retry with a different key on 429 rate limit
    - Full AI logging to logs/json/ and logs/md/
    - Always prepends system prompt (fixes hallucination bug)
    """
    if not _ALL_GROQ_KEYS:
        return {"success": False, "error": "No Groq API keys found. Add keys to ai/groq_key.txt (one per line).", "text": "", "backend": "groq"}

    try:
        from groq import Groq
    except ImportError:
        return {"success": False, "error": "groq SDK not installed. Run: pip install groq", "text": "", "backend": "groq"}

    model = model_override or GROQ_MODEL
    seq = _get_seq()

    def _build_msg_list(key_idx: int, key: str) -> list:
        """Build the final messages list always with system prompt at top."""
        msg_list = []
        if system:
            msg_list.append({"role": "system", "content": system})
        if messages:
            for m in messages:
                if m.get("role") != "system":
                    msg_list.append(m)
        elif prompt:
            msg_list.append({"role": "user", "content": prompt})
        return msg_list

    # ── Try with random key, retry once with different key on 429 ────────────
    key_idx, key = _pick_groq_key()
    tried_keys = {key_idx}
    last_error = ""

    for attempt in range(min(len(_ALL_GROQ_KEYS), 3)):
        msg_list = _build_msg_list(key_idx, key)
        t0 = time.time()
        try:
            client = Groq(api_key=key)
            completion = client.chat.completions.create(
                model=model,
                messages=msg_list,
                temperature=TEMPERATURE,
                max_completion_tokens=MAX_TOKENS,
                stream=False,
            )
            raw_text = completion.choices[0].message.content or ""
            text = _strip_think_tags(raw_text)   # clean <think> blocks from reasoning models
            elapsed_ms = int((time.time() - t0) * 1000)

            # Log success (log raw_text so we can see the reasoning chain in logs)
            _write_ai_log(seq, key_idx, model, msg_list, raw_text, True, "", elapsed_ms, "groq")
            print(f"   🔑 Groq key #{key_idx} used | model: {model} | {elapsed_ms}ms | log #{seq:04d}")
            return {"success": True, "text": text, "model": model, "backend": "groq",
                    "key_used": key_idx, "log_seq": seq}

        except Exception as e:
            elapsed_ms = int((time.time() - t0) * 1000)
            err_str = str(e)
            last_error = err_str

            # Rate limit → try next key
            if "429" in err_str or "rate_limit" in err_str.lower():
                print(f"   ⚠️  Key #{key_idx} rate limited. Trying another key...")
                _write_ai_log(seq, key_idx, model, msg_list, "", False, f"Rate limited: {err_str}", elapsed_ms, "groq")
                key_idx, key = _get_next_key(key_idx)
                while key_idx in tried_keys and len(tried_keys) < len(_ALL_GROQ_KEYS):
                    key_idx, key = _get_next_key(key_idx)
                tried_keys.add(key_idx)
                continue
            else:
                _write_ai_log(seq, key_idx, model, msg_list, "", False, err_str, elapsed_ms, "groq")
                return {"success": False, "error": f"Groq error: {err_str}", "text": "", "backend": "groq", "key_used": key_idx}

    # All keys exhausted
    _write_ai_log(seq, key_idx, model, _build_msg_list(key_idx, key), "", False,
                  f"All keys exhausted: {last_error}", 0, "groq")
    return {"success": False, "error": f"All Groq keys rate limited: {last_error}", "text": "", "backend": "groq"}

# ─── GEMINI (free cloud fallback) ─────────────────────────────────────────────

def call_gemini(prompt: str, system: str = None) -> dict:
    """Call Google Gemini API (free tier)."""
    if not GEMINI_API_KEY:
        return {"success": False, "error": "GEMINI_API_KEY not set", "text": "", "backend": "gemini"}

    full_prompt = (system + "\n\n" + prompt) if system else prompt
    payload = json.dumps({
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"temperature": TEMPERATURE, "maxOutputTokens": MAX_TOKENS}
    }).encode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"success": True, "text": text, "model": GEMINI_MODEL, "backend": "gemini"}
    except Exception as e:
        return {"success": False, "error": str(e), "text": "", "backend": "gemini"}

# ─── MAIN INTERFACE ───────────────────────────────────────────────────────────

def call_llm(prompt: str, system: str = None, backend: Optional[str] = None,
             model: Optional[str] = None, messages: list = None) -> dict:
    """
    Route to the configured backend.
    Supports multi-turn conversations (messages list) and single-turn (prompt).
    Always logs to ai/logs/json/ and ai/logs/md/.
    """
    use_backend = (backend or BACKEND).lower()
    if use_backend == "groq":
        return call_groq(prompt, system, model_override=model, messages=messages)
    elif use_backend == "gemini":
        return call_gemini(prompt, system)
    else:
        return call_ollama(prompt, system, model_override=model)

def extract_json_from_response(text: str) -> dict:
    """Extract JSON from LLM response. Handles markdown code blocks and raw JSON."""
    if not text:
        return {}
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {}

def check_ollama_available() -> dict:
    """Check if Ollama is running and the model is available."""
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m["name"] for m in data.get("models", [])]
            model_ready = any(OLLAMA_MODEL.split(":")[0] in m for m in models)
            return {"available": True, "models": models, "target_model": OLLAMA_MODEL, "model_ready": model_ready}
    except Exception as e:
        return {"available": False, "error": str(e)}

def get_key_pool_status() -> dict:
    """Return info about loaded API keys (masked)."""
    return {
        "total_keys": len(_ALL_GROQ_KEYS),
        "keys": [f"key#{i+1}: {k[:8]}...{k[-4:]}" for i, k in enumerate(_ALL_GROQ_KEYS)],
        "model": GROQ_MODEL,
        "backend": BACKEND
    }

if __name__ == "__main__":
    print(f"Backend: {BACKEND}")
    status = get_key_pool_status()
    print(f"Groq keys loaded: {status['total_keys']}")
    for k in status["keys"]:
        print(f"  {k}")
    print(f"Model: {status['model']}")
    if _ALL_GROQ_KEYS:
        print("\nSending test prompt...")
        result = call_llm(
            'Respond ONLY with this exact JSON: {"status": "ok", "message": "FraudSense AI ready"}',
            system="You are a JSON-only responder. Output only valid JSON, nothing else."
        )
        print(json.dumps(result, indent=2))
