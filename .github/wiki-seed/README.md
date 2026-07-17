# Wiki seed (copy into GitHub Wiki)

GitHub Wiki is a **separate git repo**. These Markdown files are ready-made pages for IPCAS.

## One-time publish (after the first empty Wiki page exists)

1. On GitHub open **Wiki** → **Create the first page** → leave title `Home` → click **Save page** (even with placeholder text).
2. Then from your machine:

```bash
git clone https://github.com/Itshossein128/project-management-information-system.wiki.git
cd project-management-information-system.wiki
cp ../building-management/.github/wiki-seed/*.md .
# do not copy this README.md into the wiki root unless you want it
rm -f README.md
git add *.md
git commit -m "Add IPCAS wiki guides (Actions, Agents, Projects)"
git push
```

Or paste each file’s contents via the Wiki UI (New page).

## Pages

| File | Topic |
| --- | --- |
| `Home.md` | Landing + links |
| `GitHub-Tools-Guide.md` | **Start here** — Actions vs Agents vs Wiki vs Projects |
| `CI-and-Actions.md` | What each workflow does |
| `Using-Custom-Agents.md` | How to run `.github/agents/*` |
| `Local-Development.md` | Run API + web |
| `Architecture-Overview.md` | Monorepo map |
