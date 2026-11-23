
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class JiraEvent(Base):
    __tablename__ = "jira_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    event_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    issue_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


class TestRun(Base):
    __tablename__ = "test_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    jira_event_id: Mapped[int] = mapped_column(
        ForeignKey("jira_events.id"),
        nullable=False,
    )

    issue_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    environment: Mapped[str] = mapped_column(
        String(50),
        default="TEST",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="QUEUED",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
