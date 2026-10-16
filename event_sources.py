import json
import feedparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
from datetime import datetime
import re


# ============================================================
# CONFIGURATION
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 15


# ============================================================
# GOOGLE NEWS RSS
# ============================================================

def google_news_rss(query):

    encoded_query = quote(query)

    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded_query}"
        "&hl=en-IN"
        "&gl=IN"
        "&ceid=IN:en"
    )

    events = []

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        feed = feedparser.parse(
            response.content
        )

        for entry in feed.entries:

            title = entry.get(
                "title",
                ""
            ).strip()

            description = entry.get(
                "summary",
                ""
            ).strip()

            link = entry.get(
                "link",
                ""
            ).strip()

            published = entry.get(
                "published",
                ""
            )

            if not title:
                continue

            events.append({
                "title": title,
                "description": BeautifulSoup(
                    description,
                    "html.parser"
                ).get_text(" ", strip=True),
                "link": link,
                "published": published,
                "source": "Google News"
            })

    except Exception as e:

        print(
            f"Google News error for '{query}': {e}"
        )

    return events


# ============================================================
# GOOGLE SEARCH VIA GOOGLE NEWS
# ============================================================

def search_google_news_queries(queries):

    results = []

    for query in queries:

        print(
            f"Searching: {query}"
        )

        found = google_news_rss(
            query
        )

        print(
            f"  Possible events found: {len(found)}"
        )

        results.extend(found)

    return results


# ============================================================
# DIRECT WEBPAGE FETCH
# ============================================================

def fetch_webpage(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code != 200:
            return None

        return response.text

    except Exception as e:

        print(
            f"Webpage fetch failed: {url}"
        )

        return None


# ============================================================
# EXTRACT TEXT FROM WEBPAGE
# ============================================================

def extract_page_text(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    for element in soup(
        ["script", "style", "noscript"]
    ):

        element.decompose()

    text = soup.get_text(
        " ",
        strip=True
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text[:15000]


# ============================================================
# EXTRACT LINKS FROM WEBPAGE
# ============================================================

def extract_links(
    html,
    base_url
):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    links = []

    for a in soup.find_all("a"):

        href = a.get(
            "href"
        )

        text = a.get_text(
            " ",
            strip=True
        )

        if not href:
            continue

        full_url = urljoin(
            base_url,
            href
        )

        links.append({
            "text": text,
            "url": full_url
        })

    return links


# ============================================================
# UNSTOP DISCOVERY
# ============================================================

def unstop_search():

    # Broadened Unstop queries to include registration / scheduled keywords
    queries = [
        "site:unstop.com hackathon data science India",
        "site:unstop.com hackathon machine learning India",
        "site:unstop.com competition data analytics India",
        "site:unstop.com datathon India",
        "site:unstop.com workshop data science India",
        "site:unstop.com competition Python India",
        "site:unstop.com hackathon AI ML India",
        "site:unstop.com data analytics challenge India",
        "site:unstop.com \"register\" data science",
        "site:unstop.com \"registration\" data science",
        "site:unstop.com \"starts on\" data science",
    ]

    events = []
    print(
        "SEARCHING UNSTOP"
    )

    for query in queries:

        found = google_news_rss(
            query
        )

        for event in found:

            event["source"] = "Unstop / Google News"

            events.append(
                event
            )

    print(
        f"Unstop candidates found: {len(events)}"
    )

    return events


# ============================================================
# COLLEGE WEBSITE SEARCH
# ============================================================

def college_search():

    # Expanded college and university targets across Trichy, Tamil Nadu and India
    colleges = [
        # Trichy and nearby
        "site:trichy.srmtrichy.edu.in",
        "site:sastra.edu workshop data science",
        "site:care.ac.in workshop data science",
        "site:srmuniv.ac.in trichy workshop data science",
        "site:iem.edu.in trichy data science workshop",
        "site:prist.ac.in trichy data science workshop",
        "site:mamcet.com data science workshop",
        "site:mookambika.com data science workshop",

        # Major Tamil Nadu universities and colleges
        "site:iitm.ac.in data science workshop",
        "site:annauniv.edu data science workshop",
        "site:vit.ac.in data science workshop",
        "site:srmist.edu.in data science workshop",
        "site:sathyabama.ac.in data science workshop",
        "site:amrita.edu data science workshop Tamil Nadu",
        "site:psgtech.edu data science workshop",
        "site:coep.ac.in data science workshop",
        "site:cit.edu.in data science workshop",
        "site:kongu.ac.in data science workshop",
        "site:kct.ac.in data science workshop",
        "site:karunya.edu data science workshop",
        "site:saveetha.ac.in data science workshop",
        "site:hindustanuniv.ac.in data science workshop",
        "site:veltech.edu.in data science workshop",
        "site:rmkec.ac.in data science workshop",
        "site:rajalakshmi.org data science workshop",

        # Broader India — look for event pages on university domains
        "site:iitmadras.ac.in \"data science\" workshop",
        "site:iitb.ac.in \"data science\" workshop",
        "site:iitk.ac.in \"data science\" workshop",
        "site:iisc.ac.in \"data science\" workshop",
        "site:iiit.ac.in \"data science\" workshop",
        "site:universityofcalcutta.ac.in \"data science\" workshop",
        "site:du.ac.in \"data science\" workshop",
        "site:bits-pilani.ac.in \"data science\" workshop",
        "site:amrita.edu \"data science\" workshop",

        # Generic patterns for symposiums and hackathons on .ac.in domains
        "site:ac.in symposium data science Tamil Nadu",
        "site:ac.in hackathon data science Tamil Nadu",
        "site:ac.in datathon Tamil Nadu",
        "site:ac.in technical symposium data analytics Tamil Nadu",

        # Registration-specific checks on college sites
        "site:ac.in \"register\" data science",
        "site:ac.in \"registration\" data science",
    ]

    events = []

    print(
        "\n======================================"
    )

    print(
        "SEARCHING COLLEGE WEBSITES"
    )

    print(
        "======================================"
    )

    for query in colleges:

        print(
            f"Searching college source: {query}"
        )

        found = google_news_rss(
            query
        )

        for event in found:

            event["source"] = (
                "College Website / Google News"
            )

            events.append(
                event
            )

    print(
        f"College candidates found: {len(events)}"
    )

    return events


# ============================================================
# GENERAL EVENT SEARCH
# ============================================================

def general_event_search():

    # Expanded queries including popular event platforms and registration cues
    queries = [
        # Trichy
        '"data science" event Trichy',
        '"data analytics" event Trichy',
        '"machine learning" event Trichy',
        '"artificial intelligence" event Trichy',
        '"technical symposium" Trichy',
        '"hackathon" Trichy',
        '"datathon" Trichy',
        '"workshop" "Trichy" Python',
        '"workshop" "Trichy" SQL',
        '"workshop" "Trichy" "Power BI"',

        # Tamil Nadu
        '"data science" event "Tamil Nadu"',
        '"data analytics" event "Tamil Nadu"',
        '"machine learning" event "Tamil Nadu"',
        '"AI" hackathon "Tamil Nadu"',
        '"data science" hackathon "Tamil Nadu"',
        '"datathon" "Tamil Nadu"',
        '"technical symposium" "Tamil Nadu"',

        # India
        '"data science" workshop India',
        '"data analytics" workshop India',
        '"machine learning" workshop India',
        '"AI ML" hackathon India',
        '"data science" hackathon India',
        '"data analytics" competition India',
        '"datathon" India',
        '"data science" conference India',
        '"data science" symposium India',

        # Online
        '"data science" webinar online',
        '"data analytics" webinar online',
        '"machine learning" webinar online',
        '"data science" workshop online',
        '"data analytics" workshop online',
        '"Power BI" webinar online',
        '"SQL" workshop online',
        '"Python" data science workshop online',
        '"datathon" online',

        # Event platforms (Eventbrite, Devpost, Meetup)
        'site:eventbrite.com "data science" India',
        'site:eventbrite.com "machine learning" India',
        'site:eventbrite.com "data analytics" India',
        'site:devpost.com "hackathon" "data"',
        'site:devpost.com "hackathon" India',
        'site:meetup.com "data science" India',
        'site:meetup.com "machine learning" India',

        # Strong registration / schedule cues
        '"register" "data science" India',
        '"registration" "data science" India',
        '"starts on" "data science"',
        '"scheduled" "data science"',
        '"to be held on" "data science"',
        '"starts on" Trichy',
    ]

    return search_google_news_queries(
        queries
    )


# ============================================================
# REMOVE OBVIOUS NON-EVENTS
# ============================================================

def looks_like_article(event):

    title = event.get(
        "title",
        ""
    ).lower()

    description = event.get(
        "description",
        ""
    ).lower()

    text = f"{title} {description}"

    reject_keywords = [

        "how to",

        "how can you",

        "what is",

        "why ",

        "tips for",

        "guide to",

        "best practices",

        "career scope",

        "career opportunities",

        "top data science courses",

        "best data science courses",

        "online courses",

        "course comparison",

        "salary",

        "jobs",

        "hiring",

        "admission",

        "cutoff",

        "curriculum",

        "syllabus",

        "research paper",

        "research article",

        "scientific reports",

        "journal article",

        "receives award",

        "received award",

        "wins award",

        "won award",

        "hosts",

        "hosted",

        "held",

        "conducted",

        "concludes",

        "concluded",

        "inaugurates",

        "inaugurated",

        "celebrated",

        "celebrates",

        "winners",

        "winner",

        "announces",

        "announced",

        "reported",

        "reports",

        "said",

        # Additional rejects to filter news reports and post-event coverage
        "win",
        "wins",
        "won",
        "shines",
        "begins",
        "begins registration",
        "begins recruitment",
        "registration closed",
        "announces winners",
        "announced winners",
        "results",
        "result",
        "finalists",
        "finalist",
        "was held",
        "was conducted",
        "was organised",
        "past event",
    ]

    for keyword in reject_keywords:

        if keyword in text:

            return True

    return False


# ============================================================
# EVENT SIGNAL
# ============================================================

def looks_like_event(event):

    title = event.get(
        "title",
        ""
    ).lower()

    description = event.get(
        "description",
        ""
    ).lower()

    text = f"{title} {description}"

    event_keywords = [

        "workshop",

        "webinar",

        "symposium",

        "conference",

        "hackathon",

        "datathon",

        "competition",

        "challenge",

        "bootcamp",

        "technical symposium",

        "paper presentation",

        "poster presentation",

        "call for papers",

        "register",

        "registration",

    ]

    return any(
        keyword in text
        for keyword in event_keywords
    )


# ============================================================
# SCORE
# ============================================================

def score_candidate(event):

    title = event.get(
        "title",
        ""
    ).lower()

    description = event.get(
        "description",
        ""
    ).lower()

    text = f"{title} {description}"

    score = 0

    event_scores = {

        "hackathon": 15,

        "datathon": 15,

        "workshop": 10,

        "symposium": 12,

        "conference": 8,

        "competition": 10,

        "webinar": 8,

        "meetup": 8,

        "bootcamp": 8,

    }

    for keyword, value in event_scores.items():

        if keyword in text:

            score += value

    domain_scores = {

        "data science": 10,

        "data analytics": 10,

        "data analysis": 8,

        "machine learning": 7,

        "artificial intelligence": 5,

        "power bi": 6,

        "tableau": 6,

        "sql": 5,

        "python": 7,

        "statistics": 4,

    }

    for keyword, value in domain_scores.items():

        if keyword in text:

            score += value

    if "trichy" in text:
        score += 20

    if "tiruchirappalli" in text:
        score += 20

    if "tamil nadu" in text:
        score += 12

    if "online" in text:
        score += 3

    if "register" in text:
        score += 8

    if "registration" in text:
        score += 8

    if "deadline" in text:
        score += 5

    if re.search(
        r"\b20(20|21|22|23|24|25|26|27|28|29)\b",
        text
    ):

        score += 8

    # Prefer preferred domains when present in the link
    try:
        from config import PREFERRED_DOMAINS
        link = event.get('link','') or ''
        for d in PREFERRED_DOMAINS:
            if d in link:
                score += 15
                break
        # Deprioritize Unstop-only results slightly
        if 'unstop.com' in link:
            score -= 5
    except Exception:
        pass

    return score


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicates(events):

    unique = {}

    for event in events:

        title = event.get(
            "title",
            ""
        ).lower().strip()

        title = re.sub(
            r"\s+",
            " ",
            title
        )

        if not title:
            continue

        if title not in unique:

            unique[title] = event

    return list(
        unique.values()
    )


# ============================================================
# MAIN COLLECTION
# ============================================================

def collect_events():

    print(
        "\n======================================"
    )

    print(
        "STARTING EVENT COLLECTION"
    )

    print(
        "======================================"
    )

    all_events = []

    # --------------------------------------------------------
    # 1. GENERAL SEARCH
    # --------------------------------------------------------

    general = general_event_search()

    all_events.extend(
        general
    )

    # --------------------------------------------------------
    # 2. UNSTOP
    # --------------------------------------------------------

    unstop = unstop_search()

    all_events.extend(
        unstop
    )

    # --------------------------------------------------------
    # 3. COLLEGE SOURCES
    # --------------------------------------------------------

    colleges = college_search()

    all_events.extend(
        colleges
    )

    print(
        "\n======================================"
    )

    print(
        "RAW COLLECTION COMPLETE"
    )

    print(
        f"Total raw results: {len(all_events)}"
    )

    # --------------------------------------------------------
    # FILTER with pre-AI threshold, schema.org extraction and past-date checks
    # --------------------------------------------------------

    from config import PRE_AI_SCORE_THRESHOLD

    def _extract_external_url_from_html(html):
        # Find first external http(s) URL in HTML that is not news.google or accounts.google
        try:
            candidates = re.findall(r"https?://[^\"'\s<>]+", html)
            for c in candidates:
                if 'news.google' in c or 'accounts.google' in c or 'google.com' in c:
                    continue
                # prefer longer urls (heuristic)
                if c.endswith(')'):
                    c = c[:-1]
                return c
        except Exception:
            pass
        return None

    def resolve_redirects(url):
        try:
            r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            if r.status_code == 200:
                final = r.url
                html = r.text
                # If final is still a Google News URL, try to find canonical/original URL in meta tags
                try:
                    soup = BeautifulSoup(html, 'html.parser')
                    # look for og:url or link rel=canonical
                    og = soup.find('meta', property='og:url')
                    if og and og.get('content'):
                        return og.get('content'), html
                    canonical = soup.find('link', rel='canonical')
                    if canonical and canonical.get('href'):
                        return canonical.get('href'), html
                    # sometimes article link is inside anchors
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if href.startswith('http') and 'news.google' not in href:
                            return href, html
                    # fallback: regex extract external url
                    external = _extract_external_url_from_html(html)
                    if external:
                        return external, html
                except Exception:
                    pass
                return final, html
            return url, None
        except Exception:
            return url, None

    def extract_jsonld_events(html):
        events = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    payload = script.string
                    if not payload:
                        continue
                    data = json.loads(payload.strip())
                    # data may be a list or dict
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        # item might contain '@graph'
                        if isinstance(item, dict) and '@graph' in item:
                            nodes = item.get('@graph') or []
                        else:
                            nodes = [item]
                        for node in nodes:
                            if not isinstance(node, dict):
                                continue
                            t = node.get('@type') or node.get('type')
                            if isinstance(t, list):
                                is_event = 'Event' in t
                            else:
                                is_event = (t and 'Event' in t)
                            if is_event:
                                events.append(node)
                except Exception:
                    continue
        except Exception:
            return []
        return events

    def parse_date_from_text_local(text):
        # reuse simple patterns similar to ai_filter.parse_date_from_text
        patterns = [
            r"\b(\d{1,2})[\-/](\d{1,2})[\-/](\d{2,4})\b",
            r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})\b",
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(20\d{2})\b",
            r"\b(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b",
        ]
        for pat in patterns:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                found = m.group(0)
                # try normalize
                try:
                    from datetime import datetime as _dt
                    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%B %d %Y", "%b %d %Y", "%d %B %Y", "%B %d, %Y", "%b %d, %Y"):
                        try:
                            dobj = _dt.strptime(found, fmt)
                            return dobj.date()
                        except Exception:
                            continue
                except Exception:
                    return None
                return None
        return None

    # First pass: quick scoring and pre-AI threshold filtering (no page fetches)
    candidates = []
    for event in all_events:
        if looks_like_article(event):
            continue
        if not looks_like_event(event):
            continue
        score = score_candidate(event)
        event["candidate_score"] = score
        if score < PRE_AI_SCORE_THRESHOLD:
            continue
        candidates.append(event)

    # Sort candidates and limit how many we'll fetch/process further to avoid long blocking runs
    from config import TOP_PRE_AI_FETCH
    candidates.sort(key=lambda x: x.get('candidate_score', 0), reverse=True)
    top_n = min(len(candidates), TOP_PRE_AI_FETCH)

    print(f"Candidates passing pre-AI threshold: {len(candidates)}. Processing top {top_n} for schema/date enrichment...")

    filtered = []

    for idx, event in enumerate(candidates[:top_n], start=1):
        # progress indicator
        if idx % 20 == 0 or idx == 1:
            print(f"  Processing candidate {idx}/{top_n} (score={event.get('candidate_score')})")

        # resolve google news redirect if present
        link = event.get('link','') or ''
        html = None
        if 'news.google' in link:
            final_url, html = resolve_redirects(link)
            if final_url and final_url != link:
                event['link'] = final_url
                event['source'] = 'Original Source / Google News'
        else:
            final_url = link

        # try schema.org extraction if we have or can fetch html
        if not html and event.get('link'):
            try:
                html = fetch_webpage(event.get('link'))
            except Exception:
                html = None

        jsonld_events = []
        if html:
            jsonld_events = extract_jsonld_events(html)

        # if we found structured Event data, enrich and boost score
        if jsonld_events:
            node = jsonld_events[0]
            if node.get('name'):
                event['title'] = node.get('name')
            if node.get('description'):
                event['description'] = node.get('description')
            start = node.get('startDate') or node.get('startdate')
            end = node.get('endDate') or node.get('enddate')
            if start:
                event['extracted_date'] = start
            if end:
                event['extracted_end_date'] = end
            loc = node.get('location')
            if isinstance(loc, dict):
                event['extracted_location'] = loc.get('name') or loc.get('address')
            else:
                event['extracted_location'] = loc
            potential_url = node.get('url') or node.get('sameAs')
            if potential_url:
                event['extracted_registration'] = potential_url
            event['candidate_score'] = min(100, event['candidate_score'] + 30)

        # past-date filtering: look for dates in title/description/published/extracted_date
        text_for_dates = ' '.join([event.get('title',''), event.get('description',''), event.get('published','')])
        parsed = parse_date_from_text_local(text_for_dates)
        now_date = datetime.now().date()
        past = False
        if parsed:
            try:
                if parsed < now_date:
                    past = True
            except Exception:
                pass
        if not parsed and event.get('extracted_date'):
            try:
                d = None
                try:
                    d = datetime.fromisoformat(event.get('extracted_date')).date()
                except Exception:
                    m = re.search(r"20\d{2}", str(event.get('extracted_date')))
                    if m:
                        year = int(m.group(0))
                        if year < now_date.year:
                            past = True
                if d and d < now_date:
                    past = True
            except Exception:
                pass

        if past:
            continue

        filtered.append(event)

    # Note: candidates beyond top_n are intentionally skipped to keep runs fast; adjust TOP_PRE_AI_FETCH in config if desired

    # --------------------------------------------------------
    # DEDUPLICATE
    # --------------------------------------------------------

    filtered = remove_duplicates(
        filtered
    )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    filtered.sort(
        key=lambda x: x.get(
            "candidate_score",
            0
        ),
        reverse=True
    )

    print(
        f"Filtered event candidates: "
        f"{len(filtered)}"
    )

    print(
        "\n======================================"
    )

    print(
        "TOP CANDIDATES"
    )

    print(
        "======================================"
    )

    for event in filtered[:20]:

        print(
            f"\n[{event.get('candidate_score', 0)}] "
            f"{event.get('title', '')}"
        )

        print(
            f"Source: {event.get('source', '')}"
        )

        print(
            f"URL: {event.get('link', '')}"
        )

    return filtered