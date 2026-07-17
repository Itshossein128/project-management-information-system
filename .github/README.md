# GitHub configuration for IPCAS

This folder wires up **Actions**, **Agents**, issue/PR templates, and a **Wiki seed**.

For a plain-language tour of Actions vs Agents vs Wiki vs Projects, start with:

`.github/wiki-seed/GitHub-Tools-Guide.md`

(Publish that file to the GitHub Wiki — see `wiki-seed/README.md`.)

## Layout

| Path | What it is |
| --- | --- |
| `workflows/` | GitHub Actions (CI, e2e, labeler, stale, …) |
| `dependabot.yml` | Weekly dependency update PRs |
| `labeler.yml` | Path → PR label rules |
| `agents/*.agent.md` | Copilot custom agents |
| `ISSUE_TEMPLATE/` | Bug + feature forms |
| `PULL_REQUEST_TEMPLATE.md` | Default PR checklist |
| `wiki-seed/` | Ready-to-publish Wiki pages |

## You already had

- `workflows/ci.yml` — web typecheck/build + API tests
- `workflows/e2e.yml` — Playwright
- `workflows/integration-smoke.yml` — stack smoke

## Newly added samples

- Dependabot + PR labeler + stale bot
- Three custom agents (API review, Playwright, sprint scope)
- Issue/PR templates + labels (`frontend`, `backend`, `docs`, …)
- Wiki seed pages teaching the four GitHub tools

## Manual steps (UI / token scopes)

1. **Wiki:** Wiki → Create first page → Save, then push `wiki-seed/*.md` (see `wiki-seed/README.md`).
2. **Projects:** Projects → New project → template **Board** → name `IPCAS Sprint Board` → link issues `#103`–`#105`.
3. **CLI projects API (optional):** `gh auth refresh -s project,read:project`
4. **Agents:** After merging `.github/agents/`, open the **Agents** tab and pick a profile.
