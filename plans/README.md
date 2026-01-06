# Plans

This folder holds the input that the “Ralph Wiggum” loop feeds to the coding agent.

## `prd.json`

`prd.json` is a lightweight, JSON-based PRD/TODO list: an array of small, testable work items (similar to user stories) that the agent can pick from.

Each item typically contains:

- `category`: e.g. `functional` or `ui`
- `description`: one-line requirement/behavior
- `steps`: human-readable acceptance steps
- `passes`: boolean that flips to `true` when the work item is completed

### How it’s meant to be used

- Keep items small enough to fit in one agent iteration.
- Have the agent implement **one** item per run, keep checks/tests green, then update `passes`.
- The loop can stop early when everything relevant is marked `passes: true`.

## Example only

The `prd.json` in this repo is intentionally an example/template (chat-app style stories) to demonstrate the format. Replace it with your own product’s requirements.
