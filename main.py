import json

from event_sources import collect_events
from ai_filter import analyze_event
from config import AUTO_POST_ENABLED, AUTO_POST_TOP_N
from telegram_bot import send_telegram_message
import time


# ============================================================
# CONFIGURATION
# ============================================================

MAX_AI_CANDIDATES = 30
MAX_FINAL_EVENTS = 10


# ============================================================
# AI VERIFICATION
# ============================================================

def verify_candidates(candidates):

    print(
        "\n======================================"
    )

    print(
        "AI EVENT VERIFICATION"
    )

    print(
        "======================================"
    )

    total = min(
        len(candidates),
        MAX_AI_CANDIDATES
    )

    print(
        f"Sending top {total} candidates to Gemini."
    )

    final_events = []

    for index, event in enumerate(
        candidates[:MAX_AI_CANDIDATES],
        start=1
    ):

        print(
            "\n" + "=" * 60
        )

        print(
            f"[{index}/{total}]"
        )

        print(
            "Checking:",
            event.get(
                "title",
                ""
            )
        )

        print(
            "Source:",
            event.get(
                "source",
                ""
            )
        )

        try:

            result = analyze_event(
                event
            )

            if result.get(
                "relevant"
            ) is True:

                print(
                    "✅ ACCEPTED"
                )

                print(
                    "Event:",
                    result.get(
                        "event_name",
                        "Unknown"
                    )
                )

                print(
                    "Date:",
                    result.get(
                        "date",
                        "Unknown"
                    )
                )

                print(
                    "Location:",
                    result.get(
                        "location",
                        "Unknown"
                    )
                )

                final_events.append(
                    result
                )

            else:

                print(
                    "❌ Rejected"
                )

                print(
                    "Reason:",
                    result.get(
                        "reason",
                        "Unknown"
                    )
                )

        except Exception as e:

            print(
                "AI verification error:",
                e
            )

    return final_events


# ============================================================
# REMOVE DUPLICATE FINAL EVENTS
# ============================================================

def remove_duplicate_events(events):

    unique = {}

    for event in events:

        name = str(
            event.get(
                "event_name",
                ""
            )
        ).lower().strip()

        date = str(
            event.get(
                "date",
                ""
            )
        ).lower().strip()

        key = (
            name + "|" + date
        )

        if key not in unique:

            unique[key] = event

    return list(
        unique.values()
    )


# ============================================================
# DISPLAY
# ============================================================

def display_events(events):

    print(
        "\n"
        + "=" * 60
    )

    print(
        "FINAL UPCOMING EVENTS"
    )

    print(
        "=" * 60
    )

    if not events:

        print(
            "\nNo upcoming events found."
        )

        return

    for index, event in enumerate(
        events[:MAX_FINAL_EVENTS],
        start=1
    ):

        print(
            "\n" + "-" * 60
        )

        print(
            f"EVENT #{index}"
        )

        print(
            "-" * 60
        )

        fields = [

            ("Name", "event_name"),

            ("Organizer", "organizer"),

            ("Date", "date"),

            ("Time", "time"),

            ("Location", "location"),

            ("Mode", "mode"),

            ("Deadline", "deadline"),

            ("Fee", "fee"),

            ("Certificate", "certificate"),

            ("Prize", "prize"),

            ("Registration", "registration_link"),

            ("Score", "score"),

            ("Reason", "reason"),
        ]

        for label, key in fields:

            print(
                f"{label}:",
                event.get(
                    key,
                    "Unknown"
                )
            )


# ============================================================
# SAVE
# ============================================================

def save_events(events):

    filename = "events.json"

    try:

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                events,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"\nEvents saved to {filename}"
        )

    except Exception as e:

        print(
            "Could not save events:",
            e
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 60
    )

    print(
        "DAILY DATA SCIENCE EVENT BOT"
    )

    print(
        "=" * 60
    )

    print(
        "\nSearching for events..."
    )

    # --------------------------------------------------------
    # COLLECT
    # --------------------------------------------------------

    raw_events = collect_events()

    print(
        "\nFound",
        len(raw_events),
        "event candidates."
    )

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    final_events = verify_candidates(
        raw_events
    )

    # --------------------------------------------------------
    # DEDUPLICATE
    # --------------------------------------------------------

    final_events = remove_duplicate_events(
        final_events
    )

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    display_events(
        final_events
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    save_events(
        final_events
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "BOT FINISHED"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # AUTO POST TO TELEGRAM
    # --------------------------------------------------------
    try:
        if AUTO_POST_ENABLED and final_events:
            n = AUTO_POST_TOP_N
            print(f"Auto-posting top {n} events to Telegram as a single message...")

            def _esc(s):
                if not s:
                    return ''
                return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

            lines = []
            for i, e in enumerate(final_events[:n], start=1):
                name = _esc(e.get('event_name') or e.get('title') or 'Unknown event')
                org = _esc(e.get('organizer',''))
                date = _esc(e.get('date','Unknown'))
                loc = _esc(e.get('location','Unknown'))
                reg = e.get('registration_link','Unknown') or ''
                # compact one-line summary to keep message short
                line = f"{i}. <b>{name}</b> — {org} — {date} — {loc}\nRegister: {reg}"
                lines.append(line)

            # join all into one message, ensure within Telegram 4096 char limit
            message = "\n\n".join(lines)
            if len(message) > 3800:
                # truncate gracefully if too long
                message = message[:3800] + "\n\n...and more events available in the app."

            try:
                resp = send_telegram_message(message)
                print(f"Auto-post message sent -> message_id {resp.get('result',{}).get('message_id')}")
            except Exception as ex:
                print("Failed to send auto-post message:", ex)
    except Exception as e:
        print("Auto-posting failed:", e)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()