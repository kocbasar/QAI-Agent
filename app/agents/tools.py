
import json
from dataclasses import asdict
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.integrations.jira_client import JiraClient


class GetJiraIssueArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    issue_key: str = Field(
        min_length=3,
        max_length=100,
        pattern=r"^[A-Z][A-Z0-9_]*-\d+$",
    )


class ToolRegistry:
    def __init__(
        self,
        jira_client_factory: Callable[
            [], JiraClient
        ] | None = None,
    ):
        self.jira_client_factory = (
            jira_client_factory or JiraClient.from_env
        )

    def definitions(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_jira_issue",
                    "description": (
                        "Read a Jira issue including its "
                        "summary, description, status, "
                        "issue type and labels."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": (
                                    "Jira issue key, e.g. IKY-30"
                                ),
                                "pattern": (
                                    "^[A-Z][A-Z0-9_]*-[0-9]+$"
                                ),
                            }
                        },
                        "required": ["issue_key"],
                        "additionalProperties": False,
                    },
                },
            }
        ]

    def execute(
        self,
        name: str,
        arguments: str,
        allowed_issue_key: str,
    ) -> dict[str, Any]:
        if name != "get_jira_issue":
            return {
                "error": "Tool is not allowed"
            }

        try:
            raw_args = json.loads(arguments)
            args = GetJiraIssueArgs.model_validate(
                raw_args
            )

        except (ValueError, ValidationError):
            return {
                "error": "Invalid Tool arguments"
            }

        # The Agent can only access its assigned issue.
        if args.issue_key != allowed_issue_key:
            return {
                "error": "Issue access denied"
            }

        client = None

        try:
            client = self.jira_client_factory()
            issue = client.get_issue(
                args.issue_key
            )

            return asdict(issue)

        except Exception:
            # Avoid leaking credentials or HTTP details.
            return {
                "error": "Jira Tool execution failed"
            }

        finally:
            if client is not None:
                client.close()
