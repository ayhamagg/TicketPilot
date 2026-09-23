# Handles all GitHub REST API communication
import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com"


def create_github_issue(ticket) -> dict:
    """
    Convert a support ticket into a GitHub Issue.
    Returns the created issue data including URL and ID.
    """
    if not settings.GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN is not set in environment variables")

    if not settings.GITHUB_OWNER or not settings.GITHUB_REPOSITORY:
        raise ValueError("GITHUB_OWNER and GITHUB_REPOSITORY must be set")

    # Build the issue body in markdown format
    body = f"""## Customer Support Ticket #{ticket.id}

**Customer:** {ticket.customer_name}
**Email:** {ticket.customer_email}
**Channel:** {ticket.channel.value}
**Priority:** {ticket.priority.value}
**Category:** {ticket.category.value if ticket.category else 'Uncategorized'}

---

## Description

{ticket.description}

---

*This issue was automatically created from TicketPilot*
*Ticket ID: {ticket.id} | Created: {ticket.created_at}*
"""

    # Build labels from ticket data
    labels = ["support"]
    if ticket.priority:
        labels.append(f"priority:{ticket.priority.value.lower()}")
    if ticket.category:
        labels.append(f"category:{ticket.category.value.lower()}")

    payload = {
        "title": f"[Support #{ticket.id}] {ticket.title}",
        "body": body,
        "labels": labels,
    }

    headers = {
        "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    url = f"{GITHUB_API_URL}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPOSITORY}/issues"

    logger.info(f"Creating GitHub issue for ticket {ticket.id}")

    with httpx.Client(timeout=10.0) as client:
        response = client.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        data = response.json()
        logger.info(f"GitHub issue created: {data['html_url']}")
        return {
            "github_issue_id": data["number"],
            "github_issue_url": data["html_url"],
        }
    elif response.status_code == 401:
        raise ValueError("GitHub token is invalid or expired")
    elif response.status_code == 404:
        raise ValueError(f"Repository {settings.GITHUB_OWNER}/{settings.GITHUB_REPOSITORY} not found")
    elif response.status_code == 422:
        raise ValueError(f"GitHub rejected the request: {response.json()}")
    else:
        raise Exception(f"GitHub API error {response.status_code}: {response.text}")