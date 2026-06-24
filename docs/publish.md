# Publishing the monorepo

After the squash import commit, publish to GitHub:

```bash
# 1. Create the new repo (GitHub CLI)
gh repo create Itshossein128/building-management --public --source=. --remote=monorepo

# Or manually create https://github.com/Itshossein128/building-management then:
git remote add monorepo https://github.com/Itshossein128/building-management.git
git push -u monorepo main

# 2. Archive legacy repos (GitHub UI or CLI)
gh repo archive Itshossein128/building-management-front --yes
gh repo archive Itshossein128/building-management-back --yes

# 3. Add archive notice to old repo READMEs pointing to building-management
```

Current `origin` still points at `building-management-front` until you switch remotes.
