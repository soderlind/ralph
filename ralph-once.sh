#!/usr/bin/env bash
set -euo pipefail

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

copilot --model "$MODEL" \
  -p "@plans/prd.json @progress.txt $PROMPT" \
  --allow-all-tools \
  --allow-tool 'write' \
  --allow-tool 'shell(pnpm)' \
  --allow-tool 'shell(git)' \
  --deny-tool 'shell(rm)' \
  --deny-tool 'shell(git push)'
