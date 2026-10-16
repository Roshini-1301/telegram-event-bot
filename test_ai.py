print("TEST STARTED")


try:

    from ai_filter import analyze_event

    print("ai_filter imported successfully")


    test_event = {

        "title": "Data Analytics Workshop 2026",

        "description": """
        A hands-on workshop covering Python, Pandas,
        data visualization and exploratory data analysis.

        Participants will learn practical data analytics
        techniques and receive a certificate.
        """,

        "published": "August 22, 2026",

        "link": "https://example.com/data-analytics-workshop",

        "source": "Test"
    }


    print("Sending event to Gemini...")


    result = analyze_event(test_event)


    print("\n========== GEMINI RESULT ==========\n")


    print(result)


    print("\nTEST FINISHED")


except Exception as e:

    print("\n========== ERROR ==========\n")

    print(type(e).__name__)

    print(str(e))