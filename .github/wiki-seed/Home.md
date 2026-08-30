# Verona Wiki

Welcome to the **Project Management Information System (Verona)** wiki.

This wiki is for **human-friendly guides** (how we work, how GitHub tools fit together). Long engineering specs stay in the repo under `docs/`.

## Quick links in this wiki

- [[GitHub-Tools-Guide]] — what Actions, Agents, Wiki, and Projects are for (start here if you are new)
- [[Local-Development]] — how to run API + web locally
- [[CI-and-Actions]] — what each workflow in `.github/workflows` does
- [[Architecture-Overview]] — monorepo map and where code lives
- [[Using-Custom-Agents]] — how to run the Copilot agents in `.github/agents/`

## Repo docs (source of truth)

| Doc | Purpose |
| --- | --- |
| `docs/مهندسی و معماری نرم‌افزار (Engineering & Blueprint)/معماری و نقشه محدوده سیستم (Architecture & Scope Map)/بلوپرینت مهندسی Verona (Engineering Blueprint).md` | Full target design |
| `docs/مهندسی و معماری نرم‌افزار (Engineering & Blueprint)/معماری و نقشه محدوده سیستم (Architecture & Scope Map)/نقشه محدوده سیستم Verona (Verona Scope Map).md` | Blueprint ↔ code status |
| `AGENTS.md` | Cursor Cloud / agent setup notes |
| `.github/agents/*.agent.md` | Copilot custom agents |

## Default branch

Day-to-day work targets **`develop`**. `main` is the stable line.

## Stack reminder

- `apps/web` — React Router 7 + Vite
- `apps/api` — Django 4.2 + DRF + PostgreSQL
- Auth — JWT (`phone_number` login)
