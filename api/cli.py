import argparse
import json
import sys

import requests


def print_report(payload):
    analysis = payload.get("analysis", payload)
    overview = analysis.get("trend_overview", {})
    metrics = analysis.get("trend_metrics", {})
    growth = analysis.get("growth_analysis", {})
    cross_platform = analysis.get("cross_platform_analysis", {})

    print("\n" + "=" * 78)
    print("TECH TREND INTELLIGENCE REPORT")
    print("=" * 78)
    print(f"Topic       : {overview.get('topic', 'Unavailable')}")
    print(f"Category    : {overview.get('category') or 'Unavailable'}")
    print(f"Status      : {overview.get('trend_status', 'Unavailable')}")
    print(f"Score       : {overview.get('trend_score', 'Unavailable')}/100")
    print(f"Confidence  : {overview.get('confidence', 'Unavailable')}")
    print(f"Analyzed at : {analysis.get('request', {}).get('analysis_timestamp', 'Unavailable')}")

    print("\nEXECUTIVE SUMMARY")
    print("-" * 78)
    print(overview.get("executive_summary", "Unavailable"))

    print("\nTREND METRICS")
    print("-" * 78)
    for name, value in metrics.items():
        label = name.replace("_", " ").title()
        print(f"{label:<24}: {'Unavailable' if value is None else value}")

    print("\nGROWTH ANALYSIS")
    print("-" * 78)
    print(f"Direction   : {growth.get('direction', 'Unavailable')}")
    print(f"Percentage  : {growth.get('percentage', 'Unavailable')}")
    print(f"Period      : {growth.get('period', 'Unavailable')}")
    print(f"Explanation : {growth.get('explanation', 'Unavailable')}")

    print("\nPLATFORM ANALYSIS")
    print("-" * 78)
    print(f"Live source count: {cross_platform.get('platform_count', 0)}")
    print(f"Platforms: {', '.join(cross_platform.get('platforms', [])) or 'None'}")
    for name, platform in analysis.get("platform_analysis", {}).items():
        state = "AVAILABLE" if platform.get("available") else "UNAVAILABLE"
        print(f"\n[{name.upper()} - {state}]")
        print(f"  Records : {platform.get('mentions') if platform.get('mentions') is not None else platform.get('repositories', 'Unavailable')}")
        if platform.get("failure_reason"):
            print(f"  Reason  : {platform['failure_reason']}")
        for source in platform.get("sources", [])[:5]:
            print(f"  - {source.get('title', 'Untitled')}")
            print(f"    Link: {source.get('url') or 'Unavailable'}")

    print("\nKEY DEVELOPMENTS")
    print("-" * 78)
    for item in analysis.get("key_developments", [])[:10]:
        print(f"- {item.get('title', 'Untitled')} [{item.get('importance', 'unavailable')}]")
        print(f"  Source: {item.get('source', 'Unavailable')} | Link: {item.get('url') or 'Unavailable'}")

    print("\nCONTENT OPPORTUNITIES")
    print("-" * 78)
    for item in analysis.get("content_opportunities", []):
        print(f"- {item.get('platform')} {item.get('format')}: {item.get('angle')}")
        print(f"  Hook: {item.get('hook')}")

    print("\nDOWNSTREAM AGENT CONTEXT")
    print("-" * 78)
    context = analysis.get("downstream_agent_context", {})
    print(context.get("content_generation_summary", "Unavailable"))
    print("Facts:")
    for fact in context.get("key_facts", []):
        print(f"  - {fact}")
    print("Do not claim:")
    for limitation in context.get("must_not_claim", []):
        print(f"  - {limitation}")

    print("\n" + "=" * 78)
    print("End of report")
    print("=" * 78 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Print a formatted Tech Trend Intelligence report.")
    parser.add_argument("query", help="Technology topic to analyze")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Running agent API URL")
    parser.add_argument("--json", action="store_true", help="Print the complete raw JSON instead")
    args = parser.parse_args()

    try:
        response = requests.post(
            f"{args.url.rstrip('/')}/analyze",
            params={"query": args.query},
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as error:
        print(f"Analysis request failed: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print_report(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
