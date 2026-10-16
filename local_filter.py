import re
from datetime import datetime


REJECT_KEYWORDS = [

    "cutoff",
    "cut off",
    "admission",
    "admissions",
    "results",
    "result",
    "career",
    "job",
    "jobs",
    "recruitment",
    "appointed",
    "appoints",
    "secures first",
    "won",
    "winner",
    "finalist",
    "conducted",
    "inaugurated",
    "organized",
    "organised",
    "held",
    "concludes",
    "completed",
    "past event",
    "how can you",
    "best practices",
    "who is",
    "what is",
    "guide",
    "tips"
]


EVENT_KEYWORDS = [

    "workshop",
    "webinar",
    "conference",
    "symposium",
    "hackathon",
    "datathon",
    "competition",
    "meetup",
    "summit",
    "bootcamp",
    "challenge"
]


def local_filter(event):

    title = event.get("title", "").lower()
    description = event.get("description", "").lower()

    text = title + " " + description

    # Reject obvious non-event content
    for keyword in REJECT_KEYWORDS:

        if keyword in text:

            return False

    # Require at least one event keyword
    has_event_keyword = any(
        keyword in text
        for keyword in EVENT_KEYWORDS
    )

    if not has_event_keyword:

        return False

    return True