"""Write private JWT fixtures without printing tokens to the console."""
from pathlib import Path
import json
import os
import subprocess

root=Path(__file__).resolve().parents[2]
compose=['docker','compose','--env-file','ops/a7-p5/.env.acceptance','-f','ops/a7-p5/compose.yml']
script="import json; from schedule.tests.a7_p5_browser_fixture import seed; print(json.dumps(seed()))"
result=subprocess.run(compose+['exec','-T','api','python','manage.py','shell','-c',script],cwd=root,capture_output=True,text=True,check=True)
value=json.loads(result.stdout.strip().splitlines()[-1])
target=root/'ops/a7-p5/.runtime-auth.json'
fd=os.open(target,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
os.fchmod(fd,0o600)
with os.fdopen(fd,'w') as out:json.dump(value,out)
print('Created four isolated browser fixtures; credentials stored privately.')
