
from typing import Any

import httpx


class LLMError(Exception):
    pass


class LLMClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        transport: httpx.BaseTransport | None = None,
    ):
        if not api_key or not model:
            raise ValueError(
                "LLM API key and model are required"
            )

        self.model = model

        self.client = httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(
                connect=10.0,
                read=300.0,
                write=30.0,
                pool=10.0,
            ),
            follow_redirects=False,
            transport=transport,
        )

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "reasoning_effort": "none",
            "max_tokens": 1200,
        }

        try:
            response = self.client.post(
                "chat/completions",
                json=payload,
            )

            response.raise_for_status()
            data = response.json()

            choices = data.get("choices", [])

            if not choices:
                raise LLMError(
                    "LLM returned no choices"
                )

            message = choices[0].get("message")

            if not isinstance(message, dict):
                raise LLMError(
                    "Invalid LLM response"
                )

            return message

        except (httpx.HTTPError, ValueError) as exc:
            raise LLMError(
                "LLM request failed"
            ) from exc

    def close(self):
        self.client.close()
