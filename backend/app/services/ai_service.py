import anthropic
import json
import logging
from app.core.config import settings
from app.models.ticket import CategoryEnum, PriorityEnum

logger = logging.getLogger(__name__)

# All valid categories in one place
CATEGORIES = [c.value for c in CategoryEnum]
PRIORITIES = [p.value for p in PriorityEnum]


def analyze_ticket(title: str, description: str) -> dict:
    """
    Send ticket to Claude API and get back:
    - category + confidence
    - one-sentence summary
    - priority suggestion
    """
    if not settings.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set in environment variables")

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = f"""You are a customer support ticket analyzer. Analyze the following support ticket and return a JSON object.

Ticket Title: {title}
Ticket Description: {description}

Return ONLY a valid JSON object with exactly these fields:
{{
  "category": one of {CATEGORIES},
  "category_confidence": a float between 0.0 and 1.0,
  "summary": a single sentence summarizing the ticket,
  "priority_suggestion": one of {PRIORITIES}
}}

Rules:
- category must be exactly one of the values listed
- category_confidence must be between 0.0 and 1.0
- summary must be one sentence, under 150 characters
- priority_suggestion must be exactly one of the values listed
- Return ONLY the JSON object, no explanation, no markdown, no code blocks"""

    logger.info(f"Sending ticket to Claude API for analysis: {title}")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    raw_response = message.content[0].text
    logger.info(f"Received response from Claude API")

    # Parse the JSON response
    result = json.loads(raw_response)

    # Validate the fields are what we expect
    if result["category"] not in CATEGORIES:
        result["category"] = "OTHER"
    if result["priority_suggestion"] not in PRIORITIES:
        result["priority_suggestion"] = "MEDIUM"

    return result


def find_similar_tickets(new_ticket_text: str, existing_tickets: list) -> list:
    """
    Compare a new ticket against existing tickets using Claude.
    Returns a list of similar tickets with similarity scores.
    """
    if not existing_tickets:
        return []

    if not settings.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set")

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    # Format existing tickets for the prompt
    tickets_text = "\n".join([
        f"ID {t['id']}: {t['title']} - {t['description'][:100]}"
        for t in existing_tickets
    ])

    prompt = f"""You are comparing support tickets for similarity.

New ticket:
{new_ticket_text}

Existing tickets:
{tickets_text}

Return ONLY a valid JSON array of tickets that are semantically similar to the new ticket.
Only include tickets with similarity above 0.5.
Format:
[
  {{"ticket_id": <id>, "title": "<title>", "similarity_score": <float between 0.0 and 1.0>}}
]

If no tickets are similar, return an empty array: []
Return ONLY the JSON array, no explanation."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    raw_response = message.content[0].text
    result = json.loads(raw_response)

    # Sort by similarity score, highest first
    result.sort(key=lambda x: x["similarity_score"], reverse=True)

    return result[:5]  # Return top 5 similar tickets max