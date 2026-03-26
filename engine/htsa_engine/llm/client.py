"""
Provider-agnostic chat completions client.

Works with any API that implements the OpenAI chat completions spec:
  OpenAI          https://api.openai.com/v1
  Groq            https://api.groq.com/openai/v1
  Together        https://api.together.xyz/v1
  Mistral         https://api.mistral.ai/v1
  Ollama          http://localhost:11434/v1
  OpenRouter      https://openrouter.ai/api/v1
  Azure OpenAI    https://{resource}.openai.azure.com/openai/deployments/{model}
  Any compatible  {base_url}/chat/completions

Zero external dependencies — uses urllib from the standard library.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request


class ChatCompletionsClient:
    """
    Minimal chat completions client. One POST request. Any provider.

    Usage:
        client = ChatCompletionsClient(
            base_url="https://api.openai.com/v1",
            api_key="sk-...",
            model="gpt-4o",
        )
        response = client.complete([
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
        ])
    """

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        model: str = "",
        temperature: float = 0.3,
        timeout: int = 120,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.endpoint = base_url.rstrip("/") + "/chat/completions"
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.extra_headers = headers or {}

    def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        json_mode: bool = False,
        model: str | None = None,
    ) -> str:
        """Send a chat completion request. Returns the response content string."""
        body: dict = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        headers.update(self.extra_headers)

        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint, data=data, headers=headers, method="POST"
        )

        # Simple retry: once on 429 or 5xx
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    return result["choices"][0]["message"]["content"]
            except urllib.error.HTTPError as e:
                if attempt == 0 and e.code in (429, 500, 502, 503):
                    time.sleep(2)
                    continue
                error_body = e.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"Chat completions error {e.code}: {error_body}"
                ) from e

        raise RuntimeError("Max retries exceeded")
