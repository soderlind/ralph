#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_PROMPT_FILE="$SCRIPT_DIR/prompts/default.txt"

usage() {
  cat <<USAGE
Usage:
  $0 [--prompt <file>] [--prd <file>] [--allow-profile <safe|dev|locked>] [--allow-tools <toolSpec> ...] [--deny-tools <toolSpec> ...] <iterations>

Options:
  --prompt <file>           Load prompt text from file (otherwise use prompts/default.txt).
  --prd <file>              Use a specific PRD JSON file (default: plans/prd.json).
  --allow-profile <name>    Tool permission profile: safe | dev | locked.
  --allow-tools <toolSpec>  Allow a specific tool (repeatable). Example: --allow-tools write
                            Use quotes if the spec includes spaces: --allow-tools 'shell(git push)'
  --deny-tools <toolSpec>   Deny a specific tool (repeatable). Example: --deny-tools 'shell(rm)'
  -h, --help                Show this help.

Notes:
  - If you use --prompt, you must also pass --allow-profile or at least one --allow-tools.
USAGE
}

prompt_file=""
prd_file="plans/prd.json"
allow_profile=""
declare -a allow_tools
declare -a deny_tools
allow_tools=()
deny_tools=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prompt)
      shift
      if [[ $# -lt 1 || -z "${1:-}" ]]; then
        echo "Error: --prompt requires a file path" >&2
        usage
        exit 1
      fi
      prompt_file="$1"
      shift
      ;;
    --prd)
      shift
      if [[ $# -lt 1 || -z "${1:-}" ]]; then
        echo "Error: --prd requires a file path" >&2
        usage
        exit 1
      fi
      prd_file="$1"
      shift
      ;;
    --prd=*)
      prd_file="${1#--prd=}"
      if [[ -z "$prd_file" ]]; then
        echo "Error: --prd requires a file path" >&2
        usage
        exit 1
      fi
      shift
      ;;
    --allow-profile)
      shift
      if [[ $# -lt 1 || -z "${1:-}" ]]; then
        echo "Error: --allow-profile requires a value" >&2
        usage
        exit 1
      fi
      allow_profile="$1"
      shift
      ;;
    --allow-tools)
      shift
      if [[ $# -lt 1 || -z "${1:-}" ]]; then
        echo "Error: --allow-tools requires a tool spec" >&2
        usage
        exit 1
      fi
      allow_tools+=("$1")
      shift
      ;;
    --deny-tools)
      shift
      if [[ $# -lt 1 || -z "${1:-}" ]]; then
        echo "Error: --deny-tools requires a tool spec" >&2
        usage
        exit 1
      fi
      deny_tools+=("$1")
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Error: unknown option: $1" >&2
      usage
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -lt 1 || -z "${1:-}" ]]; then
  echo "Error: missing <iterations>" >&2
  usage
  exit 1
fi

if ! [[ "$1" =~ ^[0-9]+$ ]] || [[ "$1" -lt 1 ]]; then
  echo "Error: <iterations> must be a positive integer" >&2
  usage
  exit 1
fi

iterations="$1"

# Default model if not provided
MODEL="${MODEL:-gpt-5.2}"

PROMPT=""
if [[ -n "$prompt_file" ]]; then
  if [[ ! -r "$prompt_file" ]]; then
    echo "Error: prompt file not readable: $prompt_file" >&2
    exit 1
  fi
  PROMPT="$(cat "$prompt_file")"
else
  if [[ ! -r "$DEFAULT_PROMPT_FILE" ]]; then
    echo "Error: default prompt file not readable: $DEFAULT_PROMPT_FILE" >&2
    echo "Hint: create it or pass --prompt <file>" >&2
    exit 1
  fi
  PROMPT="$(cat "$DEFAULT_PROMPT_FILE")"
fi

if [[ ! -r "$prd_file" ]]; then
  echo "Error: PRD file not readable: $prd_file" >&2
  exit 1
fi

progress_file="progress.txt"
if [[ ! -r "$progress_file" ]]; then
  echo "Error: progress file not readable: $progress_file" >&2
  exit 1
fi

if [[ -n "$prompt_file" ]] && [[ -z "$allow_profile" ]] && [[ ${#allow_tools[@]} -eq 0 ]]; then
  echo "Error: when using --prompt, you must specify --allow-profile or at least one --allow-tools" >&2
  usage
  exit 1
fi

declare -a copilot_tool_args
declare -a available_tools
available_tools=()

# Always deny a small set of dangerous commands.
copilot_tool_args+=(--deny-tool 'shell(rm)')
copilot_tool_args+=(--deny-tool 'shell(git push)')

if [[ ${#allow_tools[@]} -eq 0 ]]; then
  if [[ -n "$allow_profile" ]]; then
    case "$allow_profile" in
      dev)
        copilot_tool_args+=(--allow-all-tools)
        copilot_tool_args+=(--allow-tool 'write')
        copilot_tool_args+=(--allow-tool 'shell(pnpm)')
        copilot_tool_args+=(--allow-tool 'shell(git)')
        ;;
      safe)
        copilot_tool_args+=(--allow-tool 'write')
        copilot_tool_args+=(--allow-tool 'shell(pnpm)')
        copilot_tool_args+=(--allow-tool 'shell(git)')
        available_tools+=('write' 'shell(pnpm)' 'shell(git)')
        ;;
      locked)
        copilot_tool_args+=(--allow-tool 'write')
        available_tools+=('write')
        ;;
      *)
        echo "Error: unknown --allow-profile: $allow_profile" >&2
        usage
        exit 1
        ;;
    esac
  else
    # Preserve previous default behavior when not using a custom prompt.
    if [[ -z "$prompt_file" ]]; then
      copilot_tool_args+=(--allow-all-tools)
      copilot_tool_args+=(--allow-tool 'write')
      copilot_tool_args+=(--allow-tool 'shell(pnpm)')
      copilot_tool_args+=(--allow-tool 'shell(git)')
      available_tools+=('write' 'shell(pnpm)' 'shell(git)')
    fi
  fi
fi

for tool in "${allow_tools[@]:-}"; do
  copilot_tool_args+=(--allow-tool "$tool")
  available_tools+=("$tool")
done

for tool in "${deny_tools[@]:-}"; do
  copilot_tool_args+=(--deny-tool "$tool")
done

# Copilot CLI requires --allow-all-tools for non-interactive tool execution.
# When we have a specific allowlist (safe/locked or explicit --allow-tools),
# also restrict the tool set via --available-tools to avoid unintended tools.
copilot_tool_args+=(--allow-all-tools)
if [[ "${allow_profile:-}" != "dev" ]] && [[ ${#available_tools[@]} -gt 0 ]]; then
  copilot_tool_args+=(--available-tools "${available_tools[@]}")
fi

for ((i=1; i<=iterations; i++)); do
  echo -e "\nIteration $i"
  echo "------------------------------------"

  # Copilot CLI 0.0.377+ may produce no output when a prompt contains multiple
  # @file attachments. Combine PRD + progress into a single attachment.
  context_file="$(mktemp ".ralph-context.${i}.XXXXXX")"
  {
    echo "# Context"
    echo
    echo "## PRD ($prd_file)"
    cat "$prd_file"
    echo
    echo "## progress.txt"
    cat "$progress_file"
    echo
  } >"$context_file"

  # Copilot may return non-zero (auth/rate limit/etc). Don't let that kill the loop.
  set +e
  if command -v script >/dev/null 2>&1; then
    transcript_file="$(mktemp -t ralph-copilot.XXXXXX)"
    script -q -F "$transcript_file" \
      copilot --add-dir "$PWD" --model "$MODEL" \
        -p "@$context_file $PROMPT" \
        "${copilot_tool_args[@]}" \
      >/dev/null 2>&1
    status=$?
    result="$(cat "$transcript_file" 2>/dev/null || true)"
    rm -f "$transcript_file" >/dev/null 2>&1 || true
  else
    result=$(
      copilot --add-dir "$PWD" --model "$MODEL" \
        -p "@$context_file $PROMPT" \
        "${copilot_tool_args[@]}" \
        2>&1
    )
    status=$?
  fi
  set -e

  rm -f "$context_file" >/dev/null 2>&1 || true

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
