#!/bin/bash
# PreToolUse hook for Bash (.claude/settings.json): agents open pull requests and the user
# merges them. Blocks commands that merge a PR or turn on auto-merge; `git merge` still works.
cmd=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null)
if printf '%s' "$cmd" | grep -Eiq 'gh +pr +merge|pulls/[^[:space:]]*/merge|enablePullRequestAutoMerge'; then
	echo "Blocked: in this repo agents don't merge pull requests or enable auto-merge. Leave the PR open; the user merges it." >&2
	exit 2
fi
exit 0
