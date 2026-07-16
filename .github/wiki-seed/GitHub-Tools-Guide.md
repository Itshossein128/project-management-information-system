# GitHub Tools Guide (for IPCAS)

You asked what each GitHub tool is for. Here is a practical map for **this** repo.

## Cheat sheet

| Tool | One-line purpose | Best for IPCAS |
| --- | --- | --- |
| **Actions** | Automated jobs on push/PR/schedule | CI (typecheck, pytest), e2e, Dependabot, labeling |
| **Agents** | Specialized Copilot helpers (prompt + tools) | API review, Playwright coverage, sprint scoping |
| **Wiki** | Editable docs next to the repo | Onboarding, process, “how we use GitHub” |
| **Projects** | Kanban / roadmap board linked to Issues & PRs | Sprint board: Backlog → In progress → Review → Done |
| **Issues** | Work items / bugs / features | Trackable tasks that appear on the Project board |

They work together:

```text
Idea → Issue (template)
     → Project column "Backlog"
     → You or an Agent implements
     → Pull Request
     → Actions run CI
     → Review → merge → Issue moves to Done
```

---

## 1. Actions

**What:** YAML workflows in `.github/workflows/` that run on GitHub’s runners.

**Already in this repo**

| Workflow | When | What it does |
| --- | --- | --- |
| `ci.yml` | push/PR to `main` (apps paths) | Web typecheck/build + API pytest with Postgres/RabbitMQ/MinIO |
| `e2e.yml` | (see file) | Playwright end-to-end |
| `integration-smoke.yml` | (see file) | Stack smoke checks |
| `pr-labeler.yml` | PR open/sync | Labels PRs `frontend` / `backend` / `docs` / … |
| `stale.yml` | weekly + manual | Marks inactive issues/PRs |

**Also:** `.github/dependabot.yml` opens weekly dependency update PRs (npm, pip, Actions).

**How to try**

1. Open the **Actions** tab.
2. Pick a workflow → **Run workflow** (if it has `workflow_dispatch`).
3. Or open a small PR that touches `apps/web` and watch `CI` + `PR Labeler`.

**Tip:** Keep product docs in `docs/`; use Actions for *verification*, not documentation.

---

## 2. Agents (Copilot custom agents)

**What:** Markdown “agent profiles” in `.github/agents/*.agent.md`. Each one is a specialist persona Copilot can load (CLI, IDE, or github.com Agents).

**Samples added for IPCAS**

| File | Use when… |
| --- | --- |
| `django-api-reviewer.agent.md` | Reviewing `apps/api` PRs for services/permissions/security |
| `playwright-e2e.agent.md` | Adding e2e coverage under `apps/web/e2e` |
| `sprint-scope.agent.md` | Mapping a feature request to blueprint + file paths |

**How to try**

1. Open the **Agents** tab on GitHub (or Copilot Chat → agent picker).
2. Choose e.g. **Sprint Scope Guide**.
3. Ask: “Where should material balance live, and what’s already done?”

See also [[Using-Custom-Agents]].

**Not the same as Actions:** Agents *help you write/review code*; Actions *run scripts in CI*.

---

## 3. Wiki

**What:** A separate git repo of Markdown pages attached to the project. Good for living process docs.

**Use wiki for:** onboarding, glossaries, “how we ship”, tool guides (this page).

**Keep in `docs/` instead:** blueprint, scope map, formal ADRs — those should version with code reviews.

**How to edit**

- On GitHub: Wiki → page → Edit.
- Or: `git clone https://github.com/Itshossein128/project-management-information-system.wiki.git`

---

## 4. Projects

**What:** A board (or table/roadmap) that organizes Issues and PRs. Classic columns: Backlog, Ready, In progress, In review, Done.

**Use projects for:** sprint planning, seeing WIP limits, linking related bugs/features.

**How to try**

1. Open **Projects** → open **IPCAS Sprint Board** (created as a sample).
2. Drag an Issue between columns.
3. From an Issue sidebar, link it to the Project.

**Tip:** One Issue = one vertical slice when possible (API + UI + test). Large epics stay as parent issues with checklist children.

---

## Suggested learning path (30 minutes)

1. Read this page.
2. Open **Actions** and click into the latest `CI` run — expand a failed/passed job.
3. Open **Agents** and ask Sprint Scope Guide about a module you care about.
4. Create a tiny Issue with the **Feature request** template.
5. Add that Issue to the Project board and move it to **Ready**.
