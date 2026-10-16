import json
import os
import re
import time
import hashlib
from datetime import datetime

from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_CACHE_FILE


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# Simple file-backed cache to avoid repeated Gemini calls for the same event
def _load_cache():
    try:
        if os.path.exists(GEMINI_CACHE_FILE):
            with open(GEMINI_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_cache(cache):
    try:
        with open(GEMINI_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _cache_key_for_event(event):
    key_source = (event.get('link') or event.get('title') or '')
    key_source = key_source.strip().lower()
    if not key_source:
        key_source = json.dumps(event, sort_keys=True)
    return hashlib.sha256(key_source.encode('utf-8')).hexdigest()


def clear_ai_cache():
    """Utility to clear the local AI cache file."""
    try:
        if os.path.exists(GEMINI_CACHE_FILE):
            os.remove(GEMINI_CACHE_FILE)
            return True
    except Exception:
        pass
    return False


def analyze_event(event):

    # Improved AI prompt plus local verification fallback.
    current_date = datetime.now().strftime(
        "%Y-%m-%d"
    )

    # Few-shot examples help the model be consistent with JSON output.
    examples = '''
# EXAMPLE - ACCEPTED
{
  "relevant": true,
  "event_name": "Trichy Data Science Workshop 2026",
  "organizer": "ABC Institute",
  "date": "2026-10-15",
  "time": "10:00 AM - 4:00 PM",
  "location": "SRM Trichy",
  "mode": "Offline",
  "deadline": "2026-10-10",
  "fee": "Free",
  "certificate": "Yes",
  "prize": "None",
  "registration_link": "https://example.com/register",
  "score": 1,
  "reason": "Page includes an event page with explicit date and registration link."
}

# EXAMPLE - REJECTED
{
  "relevant": false,
  "event_name": "Unknown",
  "organizer": "Unknown",
  "date": "Unknown",
  "time": "Unknown",
  "location": "Unknown",
  "mode": "Unknown",
  "deadline": "Unknown",
  "fee": "Unknown",
  "certificate": "Unknown",
  "prize": "None",
  "registration_link": "Unknown",
  "score": 0,
  "reason": "Article summarises past event and contains no registration or scheduling details."
}
'''

    prompt = f"""
You are an event verification system that MUST return a single valid JSON object (no surrounding backticks or commentary).
Only declare an event 'relevant': true when there is clear evidence of an upcoming event (dates, registration, schedule, or official event page).
If any fact cannot be verified from the provided title/description/URL/content, use the value "Unknown". Do not invent.

CURRENT DATE: {current_date}

INPUT TITLE:
{event.get('title','')}

INPUT DESCRIPTION:
{event.get('description','')}

INPUT PUBLISHED:
{event.get('published','')}

INPUT SOURCE:
{event.get('source','')}

INPUT URL:
{event.get('link','')}

{examples}

Return ONLY JSON for the single event following the schema shown in the examples.
"""

    # Helper: lightweight date extraction from text
    def parse_date_from_text(text):
        # Try common patterns like "15 October 2026", "Oct 15, 2026", "15/10/2026", "2026-10-15"
        patterns = [
            r"\b(\d{1,2})[\-/](\d{1,2})[\-/](\d{2,4})\b",
            r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})\b",
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(20\d{2})\b",
            r"\b(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b",
        ]
        for pat in patterns:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                try:
                    # Normalize common matches
                    groups = m.groups()
                    # handle year-first
                    if len(groups) >= 3 and re.match(r"20\d{2}", groups[0]):
                        y, mo, d = groups[0], groups[1], groups[2]
                        # if numeric month/day, try to reorder
                    # Fallback: return matched substring as-is (model or downstream code can parse)
                    found = m.group(0)
                    # Prefer ISO-like formatting when possible
                    iso = None
                    try:
                        # try several common parse attempts
                        from datetime import datetime as _dt
                        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%B %d %Y", "%b %d %Y", "%d %B %Y", "%B %d, %Y", "%b %d, %Y"):
                            try:
                                dobj = _dt.strptime(found, fmt)
                                iso = dobj.strftime("%Y-%m-%d")
                                break
                            except Exception:
                                continue
                    except Exception:
                        iso = None
                    return iso or found
                except Exception:
                    continue
        return None

    # Local helpers from event_sources for page inspection
    try:
        from event_sources import fetch_webpage, extract_page_text, extract_links
    except Exception:
        fetch_webpage = None
        extract_page_text = None
        extract_links = None

    try:
        # Check cache first
        cache = _load_cache()
        key = _cache_key_for_event(event)
        if key in cache:
            cached = cache[key]
            print("Using cached AI result for event.")
            return cached

        print("Calling Gemini...")

        # The google genai client may not accept a top-level 'temperature' kwarg for this helper;
        # pass the prompt without temperature to remain compatible. If a different SDK param is
        # required for temperature, it can be added later after confirming the installed SDK.
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        print("Gemini response received.")

        result = response.text.strip()

        if result.startswith("```json"):
            result = result[7:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]

        result = result.strip()

        data = json.loads(result)

        # Defensive normalization
        if not isinstance(data, dict):
            raise ValueError("AI returned non-object JSON")

        # If date or registration_link are Unknown, try to fetch the page for evidence
        page_text = None
        page_links = []
        url = event.get('link') or ''
        if (not data.get('date') or data.get('date') in ["Unknown", "unknown", ""] ) and fetch_webpage and url:
            try:
                html = fetch_webpage(url)
                if html and extract_page_text:
                    page_text = extract_page_text(html)
                    parsed = parse_date_from_text(page_text)
                    if parsed:
                        data['date'] = parsed
                        data['reason'] = (data.get('reason','') + ' | Date inferred from page text.').strip()
            except Exception as e:
                # ignore page fetch failures
                pass

        # If registration link missing, try to find anchors with register/registration/signup
        if (not data.get('registration_link') or data.get('registration_link') in ["Unknown", "unknown", ""]) and extract_links and url:
            try:
                html = fetch_webpage(url) if not page_text else html
                if html:
                    links = extract_links(html, url)
                    for l in links:
                        txt = (l.get('text') or '').lower()
                        href = (l.get('url') or '').strip()
                        if any(k in txt for k in ['register', 'registration', 'signup', 'apply', 'form']) or any(k in href.lower() for k in ['register', 'registration', 'signup', 'apply', 'form']):
                            data['registration_link'] = href
                            data['reason'] = (data.get('reason','') + ' | Registration link extracted from page.').strip()
                            break
            except Exception:
                pass

        # Normalize score: combine AI binary score (0/1) with candidate_score (if present)
        try:
            ai_score_val = int(float(data.get('score', 0)))
        except Exception:
            ai_score_val = 0
        candidate_score = int(event.get('candidate_score', 0) or 0)
        final_score = min(100, ai_score_val * 80 + candidate_score)
        data['score'] = final_score

        # Ensure required keys exist
        required_keys = [
            'relevant', 'event_name', 'organizer', 'date', 'time', 'location',
            'mode', 'deadline', 'fee', 'certificate', 'prize', 'registration_link', 'score', 'reason'
        ]
        for k in required_keys:
            if k not in data:
                data[k] = "Unknown" if k != 'relevant' else False

        # Save to cache
        try:
            cache[key] = data
            cache[key]['_cached_at'] = int(time.time())
            _save_cache(cache)
        except Exception:
            pass

        return data

    except Exception as e:
        print("Gemini analysis failed:", e)
        return {
            "relevant": False,
            "event_name": "Unknown",
            "organizer": "Unknown",
            "date": "Unknown",
            "time": "Unknown",
            "location": "Unknown",
            "mode": "Unknown",
            "deadline": "Unknown",
            "fee": "Unknown",
            "certificate": "Unknown",
            "prize": "None",
            "registration_link": "Unknown",
            "score": 0,
            "reason": str(e)
        }