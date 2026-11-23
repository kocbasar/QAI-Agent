
import os
import secrets
from app.core.config import get_settings
from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import JiraEvent, TestRun
from app.schemas import JiraWebhookEvent

app = FastAPI(title="AI QA Agent")

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhooks/jira")
def jira_webhook(
    event: JiraWebhookEvent,
    x_qa_webhook_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    expected_token = get_settings().qa_webhook_token

    if not expected_token:
        raise HTTPException(
            status_code=503,
            detail="Webhook token is not configured",
        )

    if not secrets.compare_digest(
        x_qa_webhook_token or "",
        expected_token,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook token",
        )

    if event.to_status.upper() != "TEST":
        return {"status": "ignored"}

    existing = db.scalar(
        select(JiraEvent).where(
            JiraEvent.event_id == event.event_id
        )
    )

    if existing:
        return {"status": "duplicate"}

    jira_event = JiraEvent(
        event_id=event.event_id,
        issue_key=event.issue_key,
    )

    db.add(jira_event)
    db.flush()

    test_run = TestRun(
        jira_event_id=jira_event.id,
        issue_key=event.issue_key,
        status="QUEUED",
        environment="TEST",
    )

    db.add(test_run)
    db.commit()
    db.refresh(test_run)

    return {
        "status": "accepted",
        "test_run_id": test_run.id,
        "issue_key": test_run.issue_key,
    }


@app.get("/test-runs/{run_id}")
def get_test_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    run = db.get(TestRun, run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Test run not found",
        )

    return {
        "id": run.id,
        "issue_key": run.issue_key,
        "status": run.status,
        "environment": run.environment,
    }
