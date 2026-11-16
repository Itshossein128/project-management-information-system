#!/usr/bin/env bash
# Build only from the already verified compiled frontend and installed lockfile
# dependencies. The temporary context has an explicit allowlist, no private env.
set -euo pipefail
cd "$(dirname "$0")/../.."
web_context=$(mktemp -d /tmp/a7-web-release.XXXXXX)
trap 'rm -rf "$web_context"' EXIT
python3 - "$web_context" <<'PY'
from pathlib import Path
import shutil, sys
target=Path(sys.argv[1])
node=Path(shutil.which('node')).resolve()
shutil.copy2(node,target/'node')
shutil.copy2(node.parent.parent/'LICENSE',target/'node-LICENSE')
for name in ['package.json','pnpm-workspace.yaml']:
    shutil.copy2(name,target/name)
shutil.copytree('node_modules',target/'node_modules',symlinks=True)
web=target/'apps/web';web.mkdir(parents=True)
shutil.copy2('apps/web/package.json',web/'package.json')
for name in ['build','node_modules']:
    shutil.copytree(Path('apps/web')/name,web/name,symlinks=True)
PY
docker build -t a7p5-web:acceptance -f ops/a7-p5/web.Dockerfile "$web_context"
