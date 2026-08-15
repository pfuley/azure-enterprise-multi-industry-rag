from src.guardrails.content_safety import (
    analyze_text_safety,
)


normal_result = analyze_text_safety(
    "What is retrieval augmented generation?"
)

print("\nNORMAL TEST")
print("=" * 60)

print(
    "Maximum Severity:",
    normal_result.max_severity,
)

print(
    "Blocklist Match:",
    normal_result.blocklist_match_detected,
)


blocked_result = analyze_text_safety(
    "This message contains BLOCKME123."
)

print("\nBLOCKLIST TEST")
print("=" * 60)

print(
    "Maximum Severity:",
    blocked_result.max_severity,
)

print(
    "Blocklist Match:",
    blocked_result.blocklist_match_detected,
)

print(
    "Matches:",
    blocked_result.blocklist_matches,
)