# Using Custom Agents

Custom agents are Copilot profiles checked into the repo:

```text
.github/agents/
  django-api-reviewer.agent.md
  playwright-e2e.agent.md
  sprint-scope.agent.md
```

Each file has YAML frontmatter (`name`, `description`, `tools`) plus Markdown instructions.

## On github.com

1. Open the repo **Agents** tab.
2. Start a session and pick an agent (or attach the profile).
3. Give a concrete task, e.g.:
   - Sprint Scope: “Map overtime requests to blueprint modules and files.”
   - API Reviewer: “Review the documents upload service for path traversal.”
   - Playwright: “Find the weakest covered flow in `apps/web/e2e` and add a test.”

## In Copilot CLI

```bash
copilot --agent sprint-scope --prompt "Where does equipment utilization live?"
```

(Exact flags depend on your Copilot CLI version; `/agent` in interactive mode also works.)

## In the IDE

Open Copilot Chat → Agent mode → agent picker → choose the repo agent.

## Good prompts (copy/paste)

**Sprint Scope Guide**

> Read `docs/ipcas-scope-map.md`. For “labor productivity”, say status, API paths, web routes, and a first-PR slice.

**Django API Reviewer**

> Review `apps/api/core/documents/services/upload_service.py` against our security lessons in `.jules/sentinel.md`.

**Playwright E2E Agent**

> Compare `apps/web/e2e/COVERAGE_MAP.md` to existing specs and propose the next test only (no code yet).

## Tips

- Prefer agents for *repeatable* roles; use Issues + Projects for *tracking*.
- Keep agent instructions short and path-specific so they stay accurate as the repo grows.
- Agents do not replace CI — still require green Actions on PRs.
