#!/usr/bin/env bash
# sync-upstream.sh — Rebase feat/auto onto latest origin/main
# Usage: ./sync-upstream.sh [--push]

set -euo pipefail

BRANCH="feat/auto"
UPSTREAM="origin/main"
PUSH=${1:-""}
STASHED=0

# 1. Ensure merge driver is registered
git config merge.ours.driver true

# 2. Ensure we're on the right branch
CURRENT=$(git branch --show-current)
if [[ "$CURRENT" != "$BRANCH" ]]; then
  echo "ERROR: Must be on $BRANCH (currently on $CURRENT)"
  exit 1
fi

# 3. Warn if uncommitted changes exist
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "WARNING: Uncommitted changes detected. Stashing..."
  git stash push -u -m "wip: auto-stash before sync-upstream"
  STASHED=1
fi

# 4. Fetch upstream
echo "Fetching $UPSTREAM..."
git fetch origin

# 5. Rebase
echo "Rebasing $BRANCH onto $UPSTREAM..."
git rebase "$UPSTREAM"

# 6. Re-apply stash if needed
if [[ "${STASHED}" == "1" ]]; then
  echo "Re-applying stash..."
  git stash pop
fi

# 7. Push (force-with-lease for safety)
if [[ "$PUSH" == "--push" ]]; then
  echo "Pushing $BRANCH..."
  git push --force-with-lease origin "$BRANCH"
fi

echo "Done! Run 'git log --oneline -10' to verify."
