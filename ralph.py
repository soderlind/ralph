#!/usr/bin/env python3
"""
Ralph loop wrapper for GitHub Copilot CLI (programmatic mode).
Repeatedly runs Copilot targeting ONE PRD story at a time.

Based on Ralph Wiggum loop principle:
- PRD: all stories are passes=true
- Tests: story tests pass before flipping passes=true
- Repo state: git working tree is clean (no uncommitted changes)
"""

from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_COMPLETION = "COMPLETE"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def log(msg: str) -> None:
    print(f"[{now_iso()}] {msg}", flush=True)


def run_streaming(
    cmd: List[str] | str,
    *,
    cwd: Optional[Path] = None,
    check: bool = True,
    label: Optional[str] = None,
) -> Tuple[int, str]:
    """Run a command and stream combined stdout/stderr to the terminal."""
    start = time.time()
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=isinstance(cmd, str),
    )
    assert proc.stdout is not None
    lines: List[str] = []
    prefix = f"[{label}] " if label else ""
    for line in proc.stdout:
        lines.append(line.rstrip("\n"))
        print(prefix + line, end="", flush=True)
    
    rc = proc.wait()
    elapsed = time.time() - start
    
    if label:
        log(f"{label} finished with exit code {rc} in {elapsed:.1f}s")
    
    if check and rc != 0:
        raise subprocess.CalledProcessError(rc, cmd, output="\n".join(lines))
    
    return rc, "\n".join(lines).strip()


def sh(cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=check,
    )


def git_clean() -> bool:
    p = sh(["git", "status", "--porcelain"], check=True)
    return p.stdout.strip() == ""


def git_porcelain() -> str:
    return sh(["git", "status", "--porcelain"], check=True).stdout.strip()


def git_diff_stat() -> str:
    return sh(["git", "diff", "--stat"], check=True).stdout.strip()


def git_branch() -> str:
    p = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"], check=True)
    return p.stdout.strip()


def ensure_git_repo() -> None:
    sh(["git", "rev-parse", "--is-inside-work-tree"], check=True)


def load_json(path: Path) -> Dict[str, Any] | List[Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Dict[str, Any] | List[Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def pick_next_story(prd: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Pick next story to work on based on priority."""
    failing = [s for s in prd if not s.get("passes", False)]
    if not failing:
        return None
    
    failing.sort(key=lambda s: (int(s.get("priority", 9999)), str(s.get("id", ""))))
    return failing[0]


def union_tests(prd: List[Dict[str, Any]]) -> List[str]:
    """Collect all test commands from all stories."""
    seen: List[str] = []
    for s in prd:
        for t in (s.get("tests") or []):
            if t not in seen:
                seen.append(t)
    return seen


def run_tests(commands: List[str]) -> Tuple[bool, str]:
    """Run test commands and return (success, log)."""
    if not commands:
        return True, "(no tests specified)"
    
    logs: List[str] = []
    for cmd in commands:
        log(f"Running test: {cmd}")
        logs.append(f"$ {cmd}")
        try:
            _, combined = run_streaming(cmd, check=True, label="test")
            if combined:
                logs.append(combined)
        except subprocess.CalledProcessError as e:
            combined = (getattr(e, "output", None) or "").strip()
            if combined:
                logs.append(combined)
            logs.append(f"[FAIL] {cmd} exited with {e.returncode}")
            return False, "\n".join(logs)
    
    return True, "\n".join(logs)


def append_progress(progress_path: Path, text: str) -> None:
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    with progress_path.open("a", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")


def stage_all() -> None:
    sh(["git", "add", "-A"], check=True)


def commit_if_needed(message: str) -> bool:
    if git_clean():
        return False
    
    stage_all()
    sh(["git", "commit", "-m", message], check=True)
    return True


def build_prompt(
    prd_data: List[Dict[str, Any]],
    story: Dict[str, Any],
    progress_tail: str,
    completion_token: str,
    prompt_prefix: str = "",
) -> str:
    """Build the prompt for Copilot."""
    steps = "\n".join([f"- {s}" for s in (story.get("steps") or [])])
    
    base_prompt = f"""You are acting as an autonomous coding agent inside a git repo.

GOAL
Implement exactly ONE PRD story per iteration: {story.get("id")} - {story.get("description")}

STEPS
{steps if steps.strip() else "- (no steps provided)"}

TESTS TO PASS FOR THIS STORY
{chr(10).join([f"- {t}" for t in (story.get("tests") or [])]) if story.get("tests") else "- (no tests listed; you MUST add tests to prd.json before marking passes=true)"}

RULES (NON-NEGOTIABLE)
1) Work ONLY on this story. Do not start other stories.
2) Make the smallest set of changes that satisfy the steps.
3) Update prd.json: set this story's passes=true ONLY when tests pass.
4) Ensure repository is left clean (no uncommitted changes) by committing your work.
5) Do not emit the token {completion_token} unless ALL stories in prd.json are passes=true AND all final tests pass AND git is clean.

CONTEXT
- Current branch: {git_branch()}
- Git status: {git_porcelain() or "(clean)"}
- Diff stat: {git_diff_stat() or "(none)"}

RECENT PROGRESS LOG (tail)
{progress_tail}

OUTPUT FORMAT
- Start with a short plan.
- Then do the work.
- End with:
  - "STORY_DONE" if you believe this story is done (tests passing + committed + prd.json updated).
  - Or "STORY_BLOCKED: <reason>" if you cannot proceed.
  - Only end with {completion_token} if absolutely all conditions are met.
"""
    
    if prompt_prefix:
        return f"{prompt_prefix}\n\n{base_prompt}"
    return base_prompt


def build_final_tests_fix_prompt(
    prd_data: List[Dict[str, Any]],
    test_log: str,
    progress_tail: str,
    completion_token: str,
) -> str:
    """Build prompt for fixing final tests."""
    # For now, use union of all tests as final tests
    final_tests = union_tests(prd_data)
    tests_list = "\n".join([f"- {t}" for t in final_tests])
    
    # Truncate test log to last 80 lines
    test_log_lines = test_log.splitlines()
    if len(test_log_lines) > 80:
        test_log = "\n".join(test_log_lines[-80:])
    
    return f"""You are acting as an autonomous coding agent inside a git repo.

GOAL
All PRD stories are marked as passing, but the FINAL TESTS are failing. Fix the failing tests.

FAILING TESTS
{tests_list}

TEST OUTPUT (failures)
{test_log}

RULES (NON-NEGOTIABLE)
1) Analyze the test failures and fix the underlying code issues.
2) Do NOT modify the tests unless they are clearly incorrect.
3) Make the smallest set of changes that fix the failures.
4) Ensure repository is left clean (no uncommitted changes) by committing your work.
5) Do not emit the token {completion_token} unless all final tests pass AND git is clean.

CONTEXT
- Current branch: {git_branch()}
- Git status: {git_porcelain() or "(clean)"}
- Diff stat: {git_diff_stat() or "(none)"}

RECENT PROGRESS LOG (tail)
{progress_tail}

OUTPUT FORMAT
- Start with a short analysis of what's failing and why.
- Then fix the code.
- Commit your changes.
- End with "FIXES_APPLIED" if you believe the fixes are done.
- Only end with {completion_token} if all final tests pass AND git is clean.
"""


def call_copilot(
    copilot_bin: str,
    prompt: str,
    extra_args: List[str],
    repo_dir: Path,
) -> str:
    """Call copilot in programmatic mode."""
    cmd = [
        copilot_bin,
        "--add-dir", str(repo_dir),
        "--no-color",
        "--stream", "off",
        "--silent",
        "--no-ask-user",
        "-p", prompt
    ] + extra_args
    
    log("Calling Copilot (programmatic mode)...")
    try:
        rc, combined = run_streaming(cmd, check=False, label="copilot")
    except FileNotFoundError:
        return f"[ERROR] Copilot binary not found: {copilot_bin}"
    
    if rc != 0:
        combined = (combined + f"\n\n[ERROR] copilot exited with {rc}").strip()
    
    return combined


def main() -> int:
    ap = argparse.ArgumentParser(description="Ralph loop for GitHub Copilot CLI")
    ap.add_argument("--prd", type=Path, default=Path("plans/prd.json"))
    ap.add_argument("--progress", type=Path, default=Path(".ralph/progress.txt"))
    ap.add_argument("--state", type=Path, default=Path(".ralph/state.json"))
    ap.add_argument("--max-iterations", type=int, default=20)
    ap.add_argument(
        "--once",
        action="store_true",
        help="Run only one iteration (equivalent to --max-iterations 1)",
    )
    ap.add_argument("--sleep", type=float, default=0.3)
    ap.add_argument("--completion-token", type=str, default=DEFAULT_COMPLETION)
    ap.add_argument("--copilot-bin", type=str, default="copilot")
    ap.add_argument("--model", type=str, default="claude-haiku-4.5")
    ap.add_argument(
        "--allow-profile",
        type=str,
        choices=["safe", "dev", "locked", "yolo"],
        help="Tool permission profile"
    )
    ap.add_argument(
        "--allow-tool",
        action="append",
        default=[],
        help="Extra tool to allow (repeatable)",
    )
    ap.add_argument(
        "--deny-tool",
        action="append",
        default=[],
        help="Extra tool to deny (repeatable)",
    )
    ap.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow starting with uncommitted changes (use with caution)",
    )
    ap.add_argument(
        "--prompt-prefix",
        type=Path,
        help="Optional file with additional prompt instructions prepended to each story prompt",
    )
    ap.add_argument(
        "--no-default-prompt",
        action="store_true",
        help="Disable auto-loading of prompts/default.txt (use only if you want no prefix at all)",
    )
    
    args = ap.parse_args()
    
    # Handle --once flag
    if args.once:
        args.max_iterations = 1
    
    log("Starting Ralph loop")
    ensure_git_repo()
    
    log(f"Using PRD: {args.prd}")
    log(f"Using progress log: {args.progress}")
    log(f"Using state file: {args.state}")
    log(f"Max iterations: {args.max_iterations}")
    log(f"Completion token: {args.completion_token}")
    
    if not args.allow_dirty and not git_clean():
        print(
            "Refusing to start: git working tree is not clean.\nRun: git status --porcelain\n"
            "Or use --allow-dirty to proceed anyway (ralph will commit changes at each story completion).",
            file=sys.stderr,
        )
        return 2
    
    # Build copilot args
    copilot_args = [
        "--model", args.model,
        "--deny-tool", "shell(rm)",
        "--deny-tool", "shell(git push)",
    ]
    
    if args.allow_profile:
        if args.allow_profile == "dev":
            copilot_args.extend(["--allow-all-tools"])
            copilot_args.extend(["--allow-tool", "write"])
            copilot_args.extend(["--allow-tool", "shell(pnpm:*)"])
            copilot_args.extend(["--allow-tool", "shell(git:*)"])
        elif args.allow_profile == "safe":
            copilot_args.extend(["--allow-tool", "write"])
            copilot_args.extend(["--allow-tool", "shell(pnpm:*)"])
            copilot_args.extend(["--allow-tool", "shell(git:*)"])
        elif args.allow_profile == "locked":
            copilot_args.extend(["--allow-tool", "write"])
        elif args.allow_profile == "yolo":
            copilot_args.append("--yolo")
    
    for tool in args.allow_tool:
        copilot_args.extend(["--allow-tool", tool])
    
    for tool in args.deny_tool:
        copilot_args.extend(["--deny-tool", tool])
    
    # Initialize state
    args.state.parent.mkdir(parents=True, exist_ok=True)
    if args.state.exists():
        state = load_json(args.state)
    else:
        state = {"created_at": now_iso(), "runs": 0}
        save_json(args.state, state)
        log("Created new state file")
    
    repo_dir = Path.cwd()
    
    # Load optional prompt prefix
    prompt_prefix = ""
    
    if args.prompt_prefix:
        # User specified explicit prefix - takes priority
        if not args.prompt_prefix.exists():
            print(f"Error: prompt prefix file not found: {args.prompt_prefix}", file=sys.stderr)
            return 2
        prompt_prefix = args.prompt_prefix.read_text(encoding="utf-8").strip()
        log(f"Using prompt prefix from: {args.prompt_prefix}")
    elif not args.no_default_prompt:
        # Try to auto-detect prompts/default.txt
        default_prompt = Path("prompts/default.txt")
        if default_prompt.exists():
            prompt_prefix = default_prompt.read_text(encoding="utf-8").strip()
            log(f"Auto-detected prompt prefix: {default_prompt}")
        else:
            log("No prompt prefix found (using dynamic prompts from PRD only)")
    else:
        log("Prompt prefix disabled (using dynamic prompts from PRD only)")
    
    # Main loop
    for i in range(1, args.max_iterations + 1):
        log(f"Iteration {i}/{args.max_iterations}: loading PRD")
        prd = load_json(args.prd)
        
        story = pick_next_story(prd)
        
        if story is None:
            log("All stories passing; running final tests")
            final_tests = union_tests(prd)
            
            if not final_tests:
                log("No tests defined; skipping final test phase")
                ok, final_test_log = True, "(no tests)"
            else:
                ok, final_test_log = run_tests(final_tests)
            
            if not ok:
                append_progress(args.progress, f"[{now_iso()}] FINAL_TESTS_FAIL\n{final_test_log}\n")
                log(f"Final tests failed; calling Copilot to fix (iteration {i})")
                
                # Get progress tail
                if args.progress.exists():
                    tail = args.progress.read_text(encoding="utf-8").splitlines()[-30:]
                    progress_tail = "\n".join(tail)
                else:
                    progress_tail = "(none yet)"
                
                fix_prompt = build_final_tests_fix_prompt(
                    prd, final_test_log, progress_tail, args.completion_token
                )
                copilot_out = call_copilot(args.copilot_bin, fix_prompt, copilot_args, repo_dir)
                append_progress(
                    args.progress,
                    f"[{now_iso()}] ITERATION {i} FINAL_TESTS_FIX\n{copilot_out}\n",
                )
                
                log("Copilot run complete; continuing loop")
                time.sleep(args.sleep)
                continue
            
            # Commit tracking files before final clean check
            log("Final tests passed; committing any tracking changes")
            commit_if_needed("ralph: update progress and state")
            
            if not git_clean():
                append_progress(args.progress, f"[{now_iso()}] FINAL_NOT_CLEAN\n{git_porcelain()}\n")
                log("Repo not clean at final check; refusing to complete")
                time.sleep(args.sleep)
                continue
            
            append_progress(
                args.progress,
                f"[{now_iso()}] ALL_PASS + FINAL_TESTS_PASS + CLEAN => {args.completion_token}\n",
            )
            log("All completion conditions met")
            print(args.completion_token, flush=True)
            
            state["runs"] = int(state.get("runs", 0)) + 1
            state["last_completed_at"] = now_iso()
            save_json(args.state, state)
            return 0
        
        # Get progress tail
        if args.progress.exists():
            tail = args.progress.read_text(encoding="utf-8").splitlines()[-30:]
            progress_tail = "\n".join(tail)
        else:
            progress_tail = "(none yet)"
        
        prompt = build_prompt(prd, story, progress_tail, args.completion_token, prompt_prefix)
        
        log(f"Selected story {story.get('id')}: {story.get('description')}")
        print(f"\n=== ITERATION {i}/{args.max_iterations} | Story {story.get('id')} ===", flush=True)
        
        copilot_out = call_copilot(args.copilot_bin, prompt, copilot_args, repo_dir)
        
        log("Copilot run complete; appending transcript to .ralph/progress.txt")
        append_progress(
            args.progress,
            f"[{now_iso()}] ITERATION {i} STORY {story.get('id')} ({story.get('description')})\n"
            f"{copilot_out}\n",
        )
        
        # Reload PRD to see if story was updated
        prd2 = load_json(args.prd)
        story2 = next((s for s in prd2 if s.get("id") == story.get("id")), None)
        
        if not story2:
            append_progress(args.progress, f"[{now_iso()}] ERROR: story disappeared from prd.json\n")
            print("Story disappeared from PRD; fix PRD and re-run.")
            return 3
        
        # Check if story has tests
        tests = story2.get("tests") or []
        if not tests:
            append_progress(args.progress, f"[{now_iso()}] ERROR: story has no tests; refusing to mark pass.\n")
            log("Story has no tests listed in PRD; add tests and re-run")
            time.sleep(args.sleep)
            continue
        
        # Run story tests
        log(f"Running story tests for {story2.get('id')}")
        ok, test_log = run_tests(tests)
        
        if not ok:
            append_progress(args.progress, f"[{now_iso()}] TESTS_FAIL for {story2.get('id')}\n{test_log}\n")
            log("Tests failed; continuing loop")
            time.sleep(args.sleep)
            continue
        
        # Mark story as passing
        story2["passes"] = True
        save_json(args.prd, prd2)
        
        commit_msg = f"ralph: {story2.get('id')} {story2.get('description')}"
        log(f"Tests passed; committing changes: {commit_msg}")
        commit_if_needed(commit_msg)
        
        if not git_clean():
            append_progress(args.progress, f"[{now_iso()}] ERROR: repo not clean after commit.\n{git_porcelain()}\n")
            log("Repo not clean after commit; fix manually")
            return 5
        
        append_progress(args.progress, f"[{now_iso()}] STORY_PASS {story2.get('id')} (tests pass + committed + clean)\n")
        
        state["runs"] = int(state.get("runs", 0)) + 1
        state["last_iteration_at"] = now_iso()
        state["last_story"] = story2.get("id")
        save_json(args.state, state)
        
        time.sleep(args.sleep)
    
    print(f"Did not finish within max iterations ({args.max_iterations}).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
