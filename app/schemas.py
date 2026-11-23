
from pydantic import BaseModel, Field


class JiraWebhookEvent(BaseModel):
    event_id: str = Field(min_length=1)
    issue_key: str = Field(min_length=1)
    from_status: str
    to_status: str


class TestRunResponse(BaseModel):
    id: int
    issue_key: str
    status: str
    environment: str
