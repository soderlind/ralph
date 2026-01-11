#!/usr/bin/env bash
set -euo pipefail

RALPH_VERSION="1.1.0"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<USAGE
Usage:
  $0 --prompt <file> [--prd <file>] [--skill <a[,b,...]>] [--allow-profile <safe|dev|locked>] [--allow-tools <toolSpec> ...] [--deny-tools <toolSpec> ...] <iterations>

Options:
  --prompt <file>           Load prompt text from file (required).
  --prd <file>              Optionally attach a PRD JSON file.
  --skill <a[,b,...]>       Prepend one or more skills from skills/<name>/SKILL.md (comma-separated).
  --allow-profile <name>    Tool permission profile: safe | dev | locked.
  --allow-tools <toolSpec>  Allow a specific tool (repeatable). Example: --allow-tools write
                            Use quotes if the spec includes spaces: --allow-tools 'shell(git push)'
  --deny-tools <toolSpec>   Deny a specific tool (repeatable). Example: --deny-tools 'shell(rm)'
  -h, --help                Show this help.

Notes:
  - You must pass --allow-profile or at least one --allow-tools.
USAGE
}

prompt_file=""
prd_file=""
skills_csv=""
allow_profile=""
declare -a allow_tools
declare -a deny_tools
allow_tools=()
deny_tools=()

trim() {
  local s="$1"
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

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
    --skill)
      shift
      if [[ $# -lt 1 || -z "${1:-}" ]]; then
        echo "Error: --skill requires a value" >&2
        usage
        exit 1
      fi
      if [[ -n "$skills_csv" ]]; then
        skills_csv+=",$1"
      else
        skills_csv="$1"
      fi
      shift
      ;;
    --skill=*)
      v="${1#--skill=}"
      if [[ -z "$v" ]]; then
        echo "Error: --skill requires a value" >&2
        usage
        exit 1
      fi
      if [[ -n "$skills_csv" ]]; then
        skills_csv+=",$v"
      else
        skills_csv="$v"
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

if [[ -z "$prompt_file" ]]; then
  echo "Error: --prompt is required" >&2
  usage
  exit 1
fi

if [[ ! -r "$prompt_file" ]]; then
  echo "Error: prompt file not readable: $prompt_file" >&2
  exit 1
fi

if [[ -n "$prd_file" ]] && [[ ! -r "$prd_file" ]]; then
  echo "Error: PRD file not readable: $prd_file" >&2
  exit 1
fi

progress_file="progress.txt"
if [[ ! -r "$progress_file" ]]; then
  echo "Error: progress file not readable: $progress_file" >&2
  exit 1
fi

declare -a skills
skills=()
if [[ -n "$skills_csv" ]]; then
  IFS=',' read -r -a skills <<<"$skills_csv"
fi

if [[ -z "$allow_profile" ]] && [[ ${#allow_tools[@]} -eq 0 ]]; then
  echo "Error: you must specify --allow-profile or at least one --allow-tools" >&2
  usage
  exit 1
fi

declare -a copilot_tool_args

# Always deny a small set of dangerous commands.
copilot_tool_args+=(--deny-tool 'shell(rm)')
copilot_tool_args+=(--deny-tool 'shell(git push)')

if [[ ${#allow_tools[@]} -eq 0 ]]; then
  if [[ -n "$allow_profile" ]]; then
    case "$allow_profile" in
      dev)
        copilot_tool_args+=(--allow-all-tools)
        copilot_tool_args+=(--allow-tool 'write')
        copilot_tool_args+=(--allow-tool 'shell(pnpm:*)')
        copilot_tool_args+=(--allow-tool 'shell(git:*)')
        ;;
      safe)
        copilot_tool_args+=(--allow-tool 'write')
        copilot_tool_args+=(--allow-tool 'shell(pnpm:*)')
        copilot_tool_args+=(--allow-tool 'shell(git:*)')
        ;;
      locked)
        copilot_tool_args+=(--allow-tool 'write')
        ;;
      *)
        echo "Error: unknown --allow-profile: $allow_profile" >&2
        usage
        exit 1
        ;;
    esac
  fi
fi

for tool in "${allow_tools[@]}"; do
  copilot_tool_args+=(--allow-tool "$tool")
done

for tool in "${deny_tools[@]}"; do
  copilot_tool_args+=(--deny-tool "$tool")
done



for ((i=1; i<=iterations; i++)); do
  echo -e "\nIteration $i"
  echo "------------------------------------"

  # Copilot CLI 0.0.377+ may produce no output when a prompt contains multiple
  # @file attachments. Combine PRD + progress into a single attachment.
  context_file="$(mktemp ".ralph-context.${i}.XXXXXX")"
  {
    echo "# Context"
    echo
    if [[ ${#skills[@]} -gt 0 ]]; then
      echo "## Skills"
      for raw in "${skills[@]}"; do
        skill="$(trim "$raw")"
        if [[ -z "$skill" ]]; then
          continue
        fi
        skill_file="skills/$skill/SKILL.md"
        if [[ ! -r "$skill_file" ]]; then
          echo "Error: skill not found/readable: $skill_file" >&2
          exit 1
        fi
        echo
        echo "### $skill"
        echo
        cat "$skill_file"
      done
      echo
    fi
    if [[ -n "$prd_file" ]]; then
      echo "## PRD ($prd_file)"
      cat "$prd_file"
      echo
    fi
    echo "## progress.txt"
    cat "$progress_file"
    echo
  } >"$context_file"

  # Copilot may return non-zero (auth/rate limit/etc). Don't let that kill the loop.
  set +e
  combined_prompt_file="$(mktemp ".ralph-prompt.${i}.XXXXXX")"
  {
    cat "$context_file"
    echo
    echo "# Prompt"
    echo
    # Keep the prompt content as-is (including newlines).
    cat "$prompt_file"
    echo
  } >"$combined_prompt_file"

  if command -v script >/dev/null 2>&1; then
    transcript_file="$(mktemp -t ralph-copilot.XXXXXX)"
    script -q -F "$transcript_file" \
      copilot --add-dir "$PWD" --model "$MODEL" \
        --no-color --stream off --silent \
        -p "@$combined_prompt_file Follow the attached prompt." \
        "${copilot_tool_args[@]}" \
      >/dev/null 2>&1
    status=$?
    result="$(cat "$transcript_file" 2>/dev/null || true)"
    rm -f "$transcript_file" >/dev/null 2>&1 || true
  else
    result=$(
      copilot --add-dir "$PWD" --model "$MODEL" \
        --no-color --stream off --silent \
        -p "@$combined_prompt_file Follow the attached prompt." \
        "${copilot_tool_args[@]}" \
        2>&1
    )
    status=$?
  fi
  set -e

  rm -f "$context_file" >/dev/null 2>&1 || true
  rm -f "$combined_prompt_file" >/dev/null 2>&1 || true

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
