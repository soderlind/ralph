#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage:
  ./test/run-prompts.sh [--only <prompt1[,prompt2...]>]

What it does:
  - Finds all *.txt prompts in ./prompts
  - Creates a git worktree per prompt
  - Runs ./ralph-once.sh with that prompt inside the worktree
  - Logs stdout/stderr to ./test/log/<timestamp>/
  - Removes the worktree and its temp branch

Options:
  --only <prompt1[,prompt2...]>  Only run the selected prompt(s). Values can be
                                basenames like default.txt, or names like default.
                                Repeatable.

Environment variables:
  MAIN_BRANCH   Base branch for worktrees (default: main)
  MODEL         Copilot model (default: gpt-5.2)
USAGE
}

declare -a ONLY_LIST
ONLY_LIST=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --only)
      shift
      if [[ $# -lt 1 || -z "${1:-}" ]]; then
        echo "Error: --only requires a value" >&2
        usage
        exit 1
      fi
      IFS=',' read -r -a _only_parts <<<"$1"
      for part in "${_only_parts[@]}"; do
        part="${part%.txt}"
        ONLY_LIST+=("${part}.txt")
      done
      shift
      ;;
    --only=*)
      v="${1#--only=}"
      if [[ -z "$v" ]]; then
        echo "Error: --only requires a value" >&2
        usage
        exit 1
      fi
      IFS=',' read -r -a _only_parts <<<"$v"
      for part in "${_only_parts[@]}"; do
        part="${part%.txt}"
        ONLY_LIST+=("${part}.txt")
      done
      shift
      ;;
    *)
      echo "Error: unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: must run inside a git repository" >&2
  exit 1
}

MAIN_BRANCH="${MAIN_BRANCH:-main}"
MODEL="${MODEL:-gpt-5.2}"

# Prefer logging into the main-branch worktree if it exists; otherwise use current worktree.
LOG_ROOT="$ROOT"
if git -C "$ROOT" worktree list --porcelain | awk -v b="refs/heads/$MAIN_BRANCH" '
    $1=="worktree"{path=$2}
    $1=="branch" && $2==b{print path; exit}
  ' >/tmp/ralph-main-worktree-path.$$ 2>/dev/null; then
  MAIN_WT_PATH="$(cat /tmp/ralph-main-worktree-path.$$ || true)"
  rm -f /tmp/ralph-main-worktree-path.$$ || true
  if [[ -n "$MAIN_WT_PATH" ]]; then
    LOG_ROOT="$MAIN_WT_PATH"
  fi
fi

TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_LOG_DIR="$LOG_ROOT/test/log/$TS"
mkdir -p "$RUN_LOG_DIR"

PROMPTS_DIR="$ROOT/prompts"
if [[ ! -d "$PROMPTS_DIR" ]]; then
  echo "Error: prompts folder not found at: $PROMPTS_DIR" >&2
  exit 1
fi

mapfile -t PROMPT_FILES < <(find "$PROMPTS_DIR" -maxdepth 1 -type f -name "*.txt" | sort)
if [[ ${#PROMPT_FILES[@]} -eq 0 ]]; then
  echo "Error: no prompt files found in $PROMPTS_DIR" >&2
  exit 1
fi

if [[ ${#ONLY_LIST[@]} -gt 0 ]]; then
  declare -a FILTERED_PROMPT_FILES
  FILTERED_PROMPT_FILES=()
  for p in "${PROMPT_FILES[@]}"; do
    base="$(basename "$p")"
    for want in "${ONLY_LIST[@]}"; do
      if [[ "$base" == "$want" ]]; then
        FILTERED_PROMPT_FILES+=("$p")
        break
      fi
    done
  done
  PROMPT_FILES=("${FILTERED_PROMPT_FILES[@]}")
  if [[ ${#PROMPT_FILES[@]} -eq 0 ]]; then
    echo "Error: --only filter matched no prompts" >&2
    exit 1
  fi
fi

render_progress() {
  local current="$1"
  local total="$2"
  local label="$3"
  local width=28
  local filled=$(( current * width / total ))
  local empty=$(( width - filled ))
  local bar_filled bar_empty

  printf -v bar_filled "%*s" "$filled" ""
  bar_filled=${bar_filled// /#}
  printf -v bar_empty "%*s" "$empty" ""
  bar_empty=${bar_empty// /-}

  printf "\r[%s%s] %d/%d %s" "$bar_filled" "$bar_empty" "$current" "$total" "$label" >&2
}

echo "Logging to: $RUN_LOG_DIR"

echo "prompt\tstatus\tworktree" >"$RUN_LOG_DIR/summary.tsv"

run_one_prompt() {
  local prompt_path="$1"
  local prompt_file
  local prompt_name
  local prd_file
  local prd_src
  local needs_prd
  local wt_dir
  local branch
  local log_file

  prompt_file="$(basename "$prompt_path")"
  prompt_name="${prompt_file%.txt}"
  prd_file="plans/prd-${prompt_name}.json"
  prd_src="$ROOT/$prd_file"
  needs_prd=1

  wt_dir="$ROOT/test/worktrees/${TS}-${prompt_name}"
  branch="ralph-test/${TS}-${prompt_name}"
  log_file="$RUN_LOG_DIR/${prompt_name}.log"

  mkdir -p "$(dirname "$wt_dir")"

  # Some prompts intentionally do not use a PRD.
  case "$prompt_file" in
    pest-coverage.txt)
      needs_prd=0
      prd_file=""
      prd_src=""
      ;;
  esac

  if [[ $needs_prd -eq 1 ]]; then
    # Prefer per-prompt PRDs, but fall back to the default PRD when none exists.
    if [[ ! -r "$prd_src" ]]; then
      prd_file="plans/prd.json"
      prd_src="$ROOT/$prd_file"
      if [[ ! -r "$prd_src" ]]; then
        echo "Error: default PRD file not readable: $prd_file" | tee -a "$log_file" >&2
        echo "Hint: create it at: $prd_src" | tee -a "$log_file" >&2
        echo -e "${prompt_file}\tSKIP(missing-prd)\t-" >>"$RUN_LOG_DIR/summary.tsv"
        return 0
      fi
    fi
  fi

  # Ensure cleanup even if the copilot run fails.
  cleanup() {
    set +e
    git -C "$ROOT" worktree remove --force "$wt_dir" >/dev/null 2>&1 || true
    git -C "$ROOT" branch -D "$branch" >/dev/null 2>&1 || true
    git -C "$ROOT" worktree prune >/dev/null 2>&1 || true
  }
  trap cleanup RETURN

  echo "==> [$prompt_name] creating worktree: $wt_dir" | tee -a "$log_file"
  git -C "$ROOT" worktree add -b "$branch" "$wt_dir" "$MAIN_BRANCH" >>"$log_file" 2>&1

  pushd "$wt_dir" >/dev/null

  # Use the current working tree versions of prompts and runner scripts so tests
  # reflect local changes even if they aren't committed yet.
  mkdir -p prompts
  cp "$ROOT/prompts/$prompt_file" "prompts/$prompt_file"

  # For the WordPress prompt, stage the vendored skills into the canonical
  # top-level `skills/` folder so the skill instructions can reference them.
  if [[ "$prompt_file" == "wordpress-plugin-agent.txt" ]]; then
    mkdir -p skills
    rm -rf skills/wp-plugin-development skills/wp-project-triage
    cp -R "$ROOT/test/skills/wp-plugin-development" skills/ || true
    cp -R "$ROOT/test/skills/wp-project-triage" skills/ || true
  fi

  # Prompt-specific tool policy (kept in the runner, not in prompt files).
  # Feel free to tweak these mappings as you add more prompts.
  declare -a args
  args=("--prompt" "prompts/$prompt_file")
  if [[ $needs_prd -eq 1 ]]; then
    mkdir -p "$(dirname "$prd_file")"
    cp "$prd_src" "$prd_file"
    args+=("--prd" "$prd_file")
  fi

  # Build Copilot CLI tool flags (kept in the harness, not in prompt files).
  declare -a copilot_tool_args
  copilot_tool_args=()

  # Always deny a small set of dangerous commands.
  copilot_tool_args+=(--deny-tool 'shell(rm)')
  copilot_tool_args+=(--deny-tool 'shell(git push)')

  case "$prompt_file" in
    wordpress-plugin-agent.txt)
      # Explicit allowlist for WP prompt.
      copilot_tool_args+=(--allow-tool 'write')
      copilot_tool_args+=(--allow-tool 'shell(git:*)')
      copilot_tool_args+=(--allow-tool 'shell(npx:*)')
      copilot_tool_args+=(--allow-tool 'shell(composer:*)')
      copilot_tool_args+=(--allow-tool 'shell(npm:*)')
      ;;
    safe-write-only.txt)
      # Locked: write-only.
      copilot_tool_args+=(--allow-tool 'write')
      ;;
    *)
      # Default: safe profile (write + pnpm + git).
      copilot_tool_args+=(--allow-tool 'write')
      copilot_tool_args+=(--allow-tool 'shell(pnpm:*)')
      copilot_tool_args+=(--allow-tool 'shell(git:*)')
      ;;
  esac

  echo "==> [$prompt_name] running copilot (pseudo-TTY)" | tee -a "$log_file"
  echo "==> [$prompt_name] prompt: ${args[*]}" | tee -a "$log_file"
  echo "==> [$prompt_name] tools: ${copilot_tool_args[*]}" | tee -a "$log_file"

  echo "--- COPILOT OUTPUT START ---" | tee -a "$log_file"

  # Copilot CLI output may go directly to the TTY. Use `script` to capture it.
  set +e
  status=0
  transcript_file="$(mktemp -t ralph-copilot.XXXXXX)"

  # Combine PRD + progress into a single attachment to avoid multi-@ parsing issues.
  context_file="$(mktemp .ralph-context.XXXXXX)"
  local preflight_failed=0
  {
    echo "# Context"
    echo
    if [[ "$prompt_file" == "wordpress-plugin-agent.txt" ]]; then
      skill_file="skills/wp-plugin-development/SKILL.md"
      if [[ -r "$skill_file" ]]; then
        echo "## Skill (wp-plugin-development)"
        cat "$skill_file"
        echo
      else
        echo "[HARNESS] Error: WordPress skill not readable: $skill_file" >&2
        preflight_failed=1
      fi
    fi
    if [[ $needs_prd -eq 1 ]]; then
      echo "## PRD ($prd_file)"
      cat "$prd_file"
      echo
    fi
    echo "## progress.txt"
    cat "progress.txt"
    echo
  } >"$context_file"

  if [[ $preflight_failed -eq 1 ]]; then
    echo "[ASSERT] Missing required WordPress skill files" | tee -a "$log_file" >&2
    rm -f "$context_file" >/dev/null 2>&1 || true
    popd >/dev/null
    echo -e "${prompt_file}\tFAIL(missing-skill)\t$wt_dir" >>"$RUN_LOG_DIR/summary.tsv"
    return 0
  fi

  if command -v script >/dev/null 2>&1; then
    env MODEL="$MODEL" script -q -F "$transcript_file" \
      copilot --add-dir "$PWD" --model "$MODEL" \
        -p "@$context_file $(cat "prompts/$prompt_file")" \
        "${copilot_tool_args[@]}" \
      >/dev/null 2>&1
    status=$?
  else
    # Fallback: best-effort capture via stdout/stderr.
    out=$(
      copilot --add-dir "$PWD" --model "$MODEL" \
        -p "@$context_file $(cat "prompts/$prompt_file")" \
        "${copilot_tool_args[@]}" \
        2>&1
    )
    status=$?
    printf '%s\n' "$out" >"$transcript_file"
  fi

  cat "$transcript_file" >>"$log_file" 2>&1 || true
  rm -f "$transcript_file" >/dev/null 2>&1 || true
  rm -f "$context_file" >/dev/null 2>&1 || true

  set -e

  echo "--- COPILOT OUTPUT END ---" | tee -a "$log_file"

  # Guard against false positives: if we captured no copilot output at all, treat as failure.
  if ! awk '
      $0=="--- COPILOT OUTPUT START ---" {capturing=1; next}
      $0=="--- COPILOT OUTPUT END ---" {capturing=0}
      capturing {print}
    ' "$log_file" | grep -q '[^[:space:]]'; then
    echo "[ASSERT] No Copilot output captured" | tee -a "$log_file" >&2
    status=3
  fi

  # Basic expectations for certain prompts.
  if [[ "$prompt_file" == "wordpress-plugin-agent.txt" ]]; then
    if ! grep -qiE "wp-env start|composer lint|composer test" "$log_file"; then
      echo "[ASSERT] Missing expected WordPress checks in output" | tee -a "$log_file" >&2
      status=2
    fi
    if grep -qiE "\bpnpm\b" "$log_file"; then
      echo "[ASSERT] Unexpected pnpm mention in output" | tee -a "$log_file" >&2
      status=2
    fi
  fi

  popd >/dev/null

  if [[ $status -eq 0 ]]; then
    echo -e "${prompt_file}\tPASS\t$wt_dir" >>"$RUN_LOG_DIR/summary.tsv"
  else
    echo -e "${prompt_file}\tFAIL($status)\t$wt_dir" >>"$RUN_LOG_DIR/summary.tsv"
  fi

  return 0
}

total_prompts=${#PROMPT_FILES[@]}
current_prompt=0

for p in "${PROMPT_FILES[@]}"; do
  current_prompt=$((current_prompt + 1))
  render_progress "$current_prompt" "$total_prompts" "$(basename "$p")"
  run_one_prompt "$p" || true
done

printf "\n" >&2

echo "Done. Summary: $RUN_LOG_DIR/summary.tsv"
