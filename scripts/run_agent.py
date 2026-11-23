
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1]),
)

from app.agents.qa_agent import QAAgent
from app.agents.tools import ToolRegistry
from app.core.config import get_settings
from app.llm.client import LLMClient


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python scripts/run_agent.py IKY-30"
        )
        sys.exit(1)

    issue_key = sys.argv[1]
    settings = get_settings()

    if not settings.llm_api_key:
        print("LLM_API_KEY is not configured")
        sys.exit(1)

    llm = LLMClient(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
    )

    try:
        agent = QAAgent(
            llm=llm,
            tools=ToolRegistry(),
            max_steps=settings.agent_max_steps,
        )

        answer = agent.run(issue_key)

        print("\n====== AI QA ANALYSIS ======\n")
        print(answer)

    finally:
        llm.close()


if __name__ == "__main__":
    main()
