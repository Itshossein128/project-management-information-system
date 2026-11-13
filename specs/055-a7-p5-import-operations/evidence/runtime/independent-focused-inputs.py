import json
from schedule.tests.a7_p5_runtime_matrix import RuntimeMatrix
from schedule.services.import_operations import run_maintenance
assert run_maintenance('recovery')['status']=='ok'
m=RuntimeMatrix('A7P5-INPUTS-','/fixtures/plan.mpp')
result=m.unreadable()
print('INDEPENDENT_INPUTS_JSON '+json.dumps(result))
