
from app.core.config import get_settings
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx


ISSUE_KEY_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*-\d+$")


class JiraIntegrationError(Exception):
    pass


@dataclass(frozen=True)
class JiraIssueContext:
    key: str
    summary: str
    description: str
    status: str
    issue_type: str
    labels: list[str]


def adf_to_text(node: Any) -> str:
    """Convert Jira ADF content into readable plain text."""

    if isinstance(node, str):
        return node

    if isinstance(node, list):
        return "".join(adf_to_text(item) for item in node)

    if not isinstance(node, dict):
        return ""

    node_type = node.get("type", "")

    if node_type == "text":
        return node.get("text", "")

    if node_type == "hardBreak":
        return "\n"

    content = adf_to_text(node.get("content", []))

    if node_type == "listItem":
        return "- " + content.strip() + "\n"

    if node_type in {
        "paragraph",
        "heading",
        "bulletList",
        "orderedList",
        "tableRow",
    }:
        return content.rstrip() + "\n"

    return content


class JiraClient:
    def __init__(
        self,
        base_url: str,
        email: str,
        api_token: str,
        transport: httpx.BaseTransport | None = None,
    ):
        parsed = urlparse(base_url)

        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or parsed.path not in ("", "/")
        ):
            raise ValueError("Invalid Jira base URL")

        if not email or not api_token:
            raise ValueError("Jira credentials are required")

        self.client = httpx.Client(
            base_url=base_url.rstrip("/"),
            auth=httpx.BasicAuth(email, api_token),
            headers={"Accept": "application/json"},
            timeout=httpx.Timeout(10.0),
            follow_redirects=False,
            transport=transport,
        )

    @classmethod
    def from_env(cls) -> "JiraClient":
        settings = get_settings()

        if not all([
            settings.jira_base_url,
            settings.jira_email,
            settings.jira_api_token,
        ]):
            raise ValueError(
                "Jira configuration is incomplete. "
                "Check your .env file."
            )

        return cls(
            base_url=settings.jira_base_url,
            email=settings.jira_email,
            api_token=settings.jira_api_token,
        )

    def get_issue(self, issue_key: str) -> JiraIssueContext:
        if not ISSUE_KEY_PATTERN.fullmatch(issue_key):
            raise ValueError("Invalid Jira issue key")

        try:
            response = self.client.get(
                f"/rest/api/3/issue/{issue_key}",
                params={
                    "fields": (
                        "summary,description,status,"
                        "issuetype,labels"
                    )
                },
            )

            response.raise_for_status()
            data = response.json()

        except (httpx.HTTPError, ValueError) as exc:
            raise JiraIntegrationError(
                "Unable to retrieve Jira issue"
            ) from exc

        fields = data.get("fields", {})

        description = adf_to_text(
            fields.get("description")
        ).strip()

        return JiraIssueContext(
            key=data["key"],
            summary=fields.get("summary", ""),
            description=description,
            status=fields.get("status", {}).get("name", ""),
            issue_type=fields.get(
                "issuetype", {}
            ).get("name", ""),
            labels=fields.get("labels") or [],
        )

    def close(self):
        self.client.close()
