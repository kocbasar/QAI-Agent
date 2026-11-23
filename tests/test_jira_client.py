
import httpx
import pytest

from app.integrations.jira_client import (
    JiraClient,
    JiraIntegrationError,
    adf_to_text,
)


MOCK_ISSUE = {
    "key": "WEB-342",
    "fields": {
        "summary": "Sepete kupon alanı eklenmesi",
        "status": {"name": "TEST"},
        "issuetype": {"name": "Story"},
        "labels": ["frontend", "checkout"],
        "components": [{"name": "Web Platform"}],
        "assignee": {"displayName": "Test User"},
        "environment": "TEST",
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Kupon uygulanabilmeli."
                        }
                    ],
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Geçersiz kupon reddedilmeli."
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                },
            ],
        },
    },
}


def test_adf_to_text():
    text = adf_to_text(
        MOCK_ISSUE["fields"]["description"]
    )

    assert "Kupon uygulanabilmeli." in text
    assert "- Geçersiz kupon reddedilmeli." in text


def test_get_issue():
    def mock_handler(request: httpx.Request):
        assert request.method == "GET"
        assert request.url.path.endswith(
            "/rest/api/3/issue/WEB-342"
        )
        requested_fields = request.url.params["fields"]
        assert "components" in requested_fields
        assert "assignee" in requested_fields
        assert "environment" in requested_fields

        return httpx.Response(
            status_code=200,
            json=MOCK_ISSUE,
        )

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="fake-token",
        transport=httpx.MockTransport(mock_handler),
    )

    try:
        issue = client.get_issue("WEB-342")
    finally:
        client.close()

    assert issue.key == "WEB-342"
    assert issue.status == "TEST"
    assert issue.issue_type == "Story"
    assert "Kupon uygulanabilmeli." in issue.description
    assert issue.labels == ["frontend", "checkout"]
    assert issue.components == ["Web Platform"]
    assert issue.assignee == "Test User"
    assert issue.environment == "TEST"


def test_jira_api_failure():
    def mock_handler(request: httpx.Request):
        return httpx.Response(
            status_code=403,
            json={"errorMessages": ["Forbidden"]},
        )

    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="fake-token",
        transport=httpx.MockTransport(mock_handler),
    )

    try:
        with pytest.raises(JiraIntegrationError):
            client.get_issue("WEB-342")
    finally:
        client.close()


def test_invalid_issue_key():
    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="fake-token",
    )

    try:
        with pytest.raises(ValueError):
            client.get_issue("../admin")
    finally:
        client.close()
