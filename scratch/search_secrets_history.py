import subprocess
import re

terms = ["API_KEY", "AIza", "ghp_", "token", "secret", "password"]

print("=== 1. SEARCH IN WORKING TREE (tracked & untracked excluding .venv) ===")
# Use git grep
for term in terms:
    try:
        out = subprocess.run(
            ["git", "grep", "-I", "-i", term, "--", ":(exclude).venv/*"],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        lines = [l for l in out.stdout.splitlines() if l.strip()]
        print(f"[{term}] found {len(lines)} matches:")
        for l in lines[:10]:
            print("  ", l[:120])
    except Exception as e:
        print(f"Error searching {term}: {e}")

print("\n=== 2. SEARCH IN GIT HISTORY (git log --all -p) ===")
for term in terms:
    try:
        out = subprocess.run(
            ["git", "log", "--all", "-p", "-G", term, "--", ":(exclude).venv/*"],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        # Search diffs for added lines containing term
        added = [l for l in out.stdout.splitlines() if l.startswith("+") and not l.startswith("+++") and term.lower() in l.lower()]
        print(f"[{term}] in git history: {len(added)} added lines:")
        for l in added[:8]:
            print("  ", l[:120])
    except Exception as e:
        print(f"Error searching history for {term}: {e}")
