from event_sources import collect_events

print("===================================")
print("TESTING EVENT SOURCES")
print("===================================")

events = collect_events()

print("\n===================================")
print(f"TOTAL EVENTS: {len(events)}")
print("===================================\n")

for i, event in enumerate(events, start=1):

    print(f"EVENT {i}")
    print("-----------------------------------")

    print("TITLE:", event["title"])

    print(
        "DESCRIPTION:",
        event["description"][:300]
    )

    print("DATE:", event["published"])

    print("SOURCE:", event["source"])

    print("URL:", event["link"])

    print()