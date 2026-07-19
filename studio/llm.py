"""Provider-independent chat client.

Any OpenAI-compatible /chat/completions endpoint works. Configuration is
environment-only so no provider details leak into project files:

    STUDIO_LLM_BASE_URL   default https://api.groq.com/openai/v1
    STUDIO_LLM_MODEL      default llama-3.3-70b-versatile
    STUDIO_LLM_API_KEY    or GROQ_API_KEY / OPENAI_API_KEY as fallbacks

Pure stdlib (urllib) by design — see DECISION_LOG D-004.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "llama-3.3-70b-versatile"


class LLMError(RuntimeError):
    pass


def _api_key() -> str:
    for var in ("STUDIO_LLM_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY"):
        val = os.environ.get(var, "").strip()
        if val:
            return val
    raise LLMError(
        "No LLM API key. Set STUDIO_LLM_API_KEY (or GROQ_API_KEY — free at "
        "console.groq.com/keys), or run with --offline.")


def chat_json(system: str, user: str, *, retries: int = 2) -> dict:
    """One chat turn that must return a JSON object. Retries on transient
    HTTP errors and once on invalid JSON (with the error fed back)."""
    base = os.environ.get("STUDIO_LLM_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    model = os.environ.get("STUDIO_LLM_MODEL", DEFAULT_MODEL)
    key = _api_key()

    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user}]
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        body = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{base}/chat/completions",
            data=body,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {key}",
                     # some gateways (Cloudflare) reject urllib's default UA
                     "User-Agent": "OpenVideoStudio/0.1"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            content = payload["choices"][0]["message"]["content"]
            return json.loads(content)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            last_err = LLMError(f"LLM HTTP {exc.code}: {detail}")
            if exc.code in (429, 500, 502, 503) and attempt < retries:
                time.sleep(2 * (attempt + 1))
                continue
            raise last_err from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = LLMError(f"LLM request failed: {exc}")
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
                continue
            raise last_err from exc
        except (KeyError, json.JSONDecodeError, ValueError) as exc:
            last_err = LLMError(f"LLM returned invalid JSON: {exc}")
            if attempt < retries:
                messages.append({"role": "user", "content":
                                 f"Your previous reply was not a valid JSON "
                                 f"object ({exc}). Reply again with ONLY the "
                                 f"JSON object."})
                continue
            raise last_err from exc
    raise last_err or LLMError("unreachable")
