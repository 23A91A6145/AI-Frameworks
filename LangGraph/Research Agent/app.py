from graph import app_graph


topic = input(
    "Enter Research Topic: "
)

result = app_graph.invoke(
    {
        "query": topic,

        "research_notes": "",

        "analysis": "",

        "report": "",

        "final_report": "",

        "saved_file": "",

        "pdf_file": "",

        "db_saved": False
    }
)

print("\n")
print("=" * 80)

print(
    "\nFINAL REVIEWED REPORT\n"
)

print(
    result["final_report"]
)

print("\n")
print("=" * 80)

print(
    f"\nMarkdown File:\n{result['saved_file']}"
)

print(
    f"\nPDF File:\n{result['pdf_file']}"
)

print(
    f"\nDatabase Saved:\n{result['db_saved']}"
)