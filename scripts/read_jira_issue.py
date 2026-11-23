
import json
import sys
from dataclasses import asdict
from pathlib import Path

# Allow running this script from the project root.
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1]),
)

from app.integrations.jira_client import (
    JiraClient,
    JiraIntegrationError,
)


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/read_jira_issue.py WEB-342")
        sys.exit(1)

    issue_key = sys.argv[1]

    try:
        client = JiraClient.from_env()

        try:
            issue = client.get_issue(issue_key)
        finally:
            client.close()

        print(
            json.dumps(
                asdict(issue),
                indent=2,
                ensure_ascii=False,
            )
        )

    except (
        JiraIntegrationError,
        ValueError,
        KeyError,
    ) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
