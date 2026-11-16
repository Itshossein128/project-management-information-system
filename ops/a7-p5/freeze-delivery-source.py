"""Create an immutable A.7 source candidate using an isolated Git index."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
os.chdir(ROOT)
SCOPES=['apps/api','apps/web','e2e','ops/a7-p5','package.json','pnpm-lock.yaml','pnpm-workspace.yaml','.npmrc','.dockerignore']
def git(*args,env=None):return subprocess.check_output(['git',*args],env=env)
index=Path(git('rev-parse','--git-path','index').decode().strip())
index_before=hashlib.sha256(index.read_bytes()).hexdigest()
base=git('rev-parse','HEAD').decode().strip()
changed=set(git('diff','HEAD','--name-only','-z','--',*SCOPES).decode().split('\0'))
changed.update(git('ls-files','--others','--exclude-standard','-z','--',*SCOPES).decode().split('\0'))
changed.discard('')
with tempfile.TemporaryDirectory(prefix='a7-freeze-') as directory:
 env={**os.environ,'GIT_INDEX_FILE':str(Path(directory)/'index')}
 subprocess.run(['git','read-tree',base],env=env,check=True)
 if changed:subprocess.run(['git','add','--',*sorted(changed)],env=env,check=True)
 tree=git('write-tree',env=env).decode().strip()
 source=git('commit-tree',tree,'-p',base,'-m','feat(a7): freeze complete acceptance source candidate',env=env).decode().strip()
subprocess.run(['git','update-ref',f'refs/heads/codex/a7-delivery-20261116-source-{source[:8]}',source],check=True)
files={}
for entry in git('ls-tree','-rz',source,'--',*SCOPES).split(b'\0'):
 if not entry:continue
 meta,path=entry.split(b'\t',1);mode,kind,oid=meta.split();path=path.decode()
 if kind!=b'blob':continue
 p=ROOT/path
 body=os.readlink(p).encode() if mode==b'120000' else p.read_bytes()
 assert hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()==oid.decode(),path
 files[path]=hashlib.sha256(body).hexdigest()
assert hashlib.sha256(index.read_bytes()).hexdigest()==index_before,'Shared index unexpectedly changed'
assert git('rev-parse','HEAD').decode().strip()==base
E=ROOT/'specs/056-a7-p6-delivery-acceptance/evidence'
(E/'source-files.json').write_text(json.dumps({'source_commit':source,'base_commit':base,'shared_index_sha256':index_before,'source_files_sha256':files},indent=2)+'\n')
print(json.dumps({'source_commit':source,'base_commit':base,'files':len(files),'shared_index_preserved':True}))
