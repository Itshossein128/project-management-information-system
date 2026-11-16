"""Verify that ready labels cannot conceal stale identity or failing evidence."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

E=Path(__file__).resolve().parent
ROOT=E.parents[2]
def invoke():
 r=subprocess.run([sys.executable,str(E/'validate_package.py')],cwd=ROOT,capture_output=True,text=True)
 return r.returncode,json.loads(r.stdout)
assert invoke()[0]==0
results=[]
def check(name,changes,expected):
 backup={path:path.read_bytes() for path in changes}
 try:
  for path,value in changes.items():path.write_bytes(value)
  code,result=invoke()
  assert code!=0 and any(expected in e for e in result['errors']),(name,result)
  results.append({'case':name,'status':'pass','rejected_reason':expected})
 finally:
  for path,value in backup.items():path.write_bytes(value)
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
rows=json.loads((E/'audit-disposition.json').read_text());rows[0]['title']='Changed audit meaning'
check('faithful_original_audit_titles',{E/'audit-disposition.json':encoded(rows)},'differs from the original audit')
pkg=json.loads((E/'package.json').read_text());pkg['version_id']='stale-candidate'
check('matching_candidate_version',{E/'package.json':encoded(pkg)},'version does not match package')
sc=json.loads((E/'scenarios.json').read_text());sc[0]['technical_result']='not_run'
check('no_unrun_scenario_when_ready',{E/'scenarios.json':encoded(sc)},'ready_for_acceptance requires pass')
proof=json.loads((E/'release-verification.json').read_text());proof['checks']['core']['sha256']='0'*64
check('immutable_final_report_hash',{E/'release-verification.json':encoded(proof)},'missing or changed final report')
proof=json.loads((E/'release-verification.json').read_text());proof['source_files_sha256'].pop(next(iter(proof['source_files_sha256'])))
check('complete_immutable_source_manifest',{E/'release-verification.json':encoded(proof)},'complete candidate source tree')
# Even a freshly rehashed report cannot turn an actual failing testcase into pass.
core=E/'final-core-junit.xml';xml=ET.fromstring(core.read_bytes());ET.SubElement(xml.find('.//testcase'),'failure').text='Deliberate validator negative control'
body=ET.tostring(xml,encoding='utf-8',xml_declaration=True)
proof=json.loads((E/'release-verification.json').read_text());proof['checks']['core']['sha256']=hashlib.sha256(body).hexdigest()
check('reject_failure_even_after_report_rehash',{core:body,E/'release-verification.json':encoded(proof)},'did not pass without skips')
assert invoke()[0]==0
(E/'validator-negative-checks.json').write_text(json.dumps({'status':'pass','cases':results,'restored_package_passes':True},indent=2)+'\n')
print(json.dumps({'status':'pass','negative_controls':len(results),'original_restored':True}))
