#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || -z "${1:-}" ]]; then
  echo "Usage: $0 <iterations>"
  exit 1
fi

if ! [[ "$1" =~ ^[0-9]+$ ]] || [[ "$1" -lt 1 ]]; then
  echo "Error: <iterations> must be a positive integer"
  exit 1
fi

iterations="$1"

# Default model if not provided
MODEL="${MODEL:-gpt-5}"

PROMPT=$(
  cat <<'PROMPT'
Work in the current repo. Use these files as your source of truth:
- plans/prd.json
- progress.txt

1. Find the highest-priority feature to work on and work only on that feature.
   This should be the one YOU decide has the highest priority - not necessarily the first in the list.
2. Check that the types check via pnpm typecheck and that the tests pass via pnpm test.
3. Update the PRD with the work that was done (plans/prd.json).
4. Append your progress to progress.txt.
   Use this to leave a note for the next person working in the codebase.
5. Make a git commit of that feature.
ONLY WORK ON A SINGLE FEATURE.
If, while implementing the feature, you notice the PRD is complete, output <promise>COMPLETE</promise>.
PROMPT
)

for ((i=1; i<=iterations; i++)); do
  echo "Iteration $i"
  echo "------------------------------------"

  # Copilot may return non-zero (auth/rate limit/etc). Don't let that kill the loop.
  set +e
  result=$(
    copilot --model "$MODEL" \
      -p "@plans/prd.json @progress.txt $PROMPT" \
      --allow-all-tools \
      --allow-tool 'write' \
      --allow-tool 'shell(pnpm)' \
      --allow-tool 'shell(git)' \
      --deny-tool 'shell(rm)' \
      --deny-tool 'shell(git push)' \
      2>&1
  )
  status=$?
  set -e

  echo "$result"

  if [[ $status -ne 0 ]]; then
    echo "Copilot exited with status $status; continuing to next iteration."
    continue
  fi

  if [[ "$result" == *"<promise>COMPLETE</promise>"* ]]; then
    echo "PRD complete, exiting."
    if command -v tt >/dev/null 2>&1; then
      tt notify "PRD complete after $i iterations"
    fi
    exit 0
  fi
done

echo "Finished $iterations iterations without receiving the completion signal."
