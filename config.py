import os
from dotenv import load_dotenv


# Load .env file
load_dotenv()


# ============================================================
# GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


# ============================================================
# TELEGRAM
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)


# ============================================================
# EVENT FILTER
# ============================================================

# Gemini must give at least this score
# for an event to be accepted.

MIN_RELEVANCE_SCORE = 7


# Maximum number of candidates
# sent to Gemini.

MAX_GEMINI_CANDIDATES = 8


# Gemini model and temperature (tune to adjust creativity/confidence)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
try:
    GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.0"))
except Exception:
    GEMINI_TEMPERATURE = 0.0

# Local AI cache file to avoid repeated calls for same event
GEMINI_CACHE_FILE = os.getenv("GEMINI_CACHE_FILE", "ai_cache.json")

# Pre-AI candidate score threshold. Candidates below this score are skipped before sending to Gemini.
PRE_AI_SCORE_THRESHOLD = int(os.getenv("PRE_AI_SCORE_THRESHOLD", "20"))

# How many top candidates (by candidate_score) to fetch pages and perform schema/date resolution on.
# Keeps the collector from fetching thousands of pages during one run.
TOP_PRE_AI_FETCH = int(os.getenv("TOP_PRE_AI_FETCH", "200"))

# Automatic posting configuration
AUTO_POST_ENABLED = os.getenv("AUTO_POST_ENABLED", "true").lower() in ("1", "true", "yes")
AUTO_POST_TOP_N = int(os.getenv("AUTO_POST_TOP_N", "10"))

# Preferred domains to boost in scoring (helps diversify away from Unstop-heavy results)
PREFERRED_DOMAINS = [
    "eventbrite.com",
    "devpost.com",
    "meetup.com",
    "hackerearth.com",
    "insider.in",
    "iitmadras.ac.in",
    "iitb.ac.in",
    "iitk.ac.in",
    "iitkgp.ac.in",
]

# Scheduler script path (for convenience)
SCHEDULER_SCRIPT = os.getenv("SCHEDULER_SCRIPT", "run_daily.ps1")