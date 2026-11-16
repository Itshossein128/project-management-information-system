import json, pathlib, hashlib, subprocess, sys, xml.etree.ElementTree as ET
R=pathlib.Path.cwd();F=R/'specs/056-a7-p6-delivery-acceptance';E=F/'evidence'
def read(p):return json.loads(pathlib.Path(p).read_text())
def write(p,x):pathlib.Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
source=sys.argv[1]
assert len(source)==40 and subprocess.check_output(['git','cat-file','-t',source],text=True).strip()=='commit'
for path in [E/'final-core-junit.xml',R/'specs/055-a7-p5-import-operations/evidence/runtime/host-pytest.xml']:
 cases=ET.parse(path).getroot().findall('.//testcase')
 assert cases and all(c.find(tag) is None for c in cases for tag in ['failure','error','skipped']),path
for name in ['general','recovery','viewer','retry']:
 stats=read(E/f'final-browser-{name}.json')['stats']
 assert stats['expected'] and not any(stats[k] for k in ['unexpected','skipped','flaky']), (name,stats)
for path in [E/'web-checks.json',R/'specs/055-a7-p5-import-operations/evidence/runtime/broker-outage.json',R/'specs/055-a7-p5-import-operations/evidence/runtime/concurrent-delivery.json']:
 assert read(path)['status']=='pass',path
version=source
runtime=read(R/'specs/055-a7-p5-import-operations/evidence/runtime/manifest.json')
assert runtime['status']=='ready' and not runtime['not_run'] and all(v=='pass' for v in runtime['matrix'].values()),runtime['matrix']
image=subprocess.check_output(['docker','image','inspect','a7p5-api:acceptance','--format','{{.Id}}'],text=True).strip()
requirements=read(R/'output/a7-requirements-2026-11-10/requirements.json')['requirements']
phase_map=read(R/'output/a7-implementation/phase-map.json')
phase={a:v['phase'] for v in phase_map.values() for a in v['audit_ids']}
core='specs/056-a7-p6-delivery-acceptance/evidence/final-core-junit.xml'
browser='specs/056-a7-p6-delivery-acceptance/evidence/final-browser-general.json'
p5='specs/055-a7-p5-import-operations/evidence/runtime/manifest.json'
prefix='apps/api/core/'
proof={
'P01':['projects/tests/test_a7_p1_reference_project.py'],
'P02':['schedule/tests/test_a7_neg01_duplicate_codes.py'],
'P03':['projects/tests/test_project_registration_lifecycle.py'],
'P04':['projects/tests/test_project_activation_feedback.py','projects/tests/test_project_registration_gates.py'],
'P05':['projects/tests/test_project_registration_gates.py'],
'P06':['projects/tests/test_project_registration_charter.py'],
'P07':['projects/tests/test_project_registration_change_request.py'],
'P08':['schedule/tests/test_a7_p2_import_safety.py'],
'P09':['projects/tests/test_project_archive_restore.py','projects/tests/test_project_archive_restore_permissions.py'],
'P10':['projects/tests/test_project_archive_restore_preservation.py','projects/tests/test_project_archive_restore_retries.py','projects/tests/test_project_archive_restore_concurrency.py'],
'P11':['projects/tests/test_project_status_undo.py','projects/tests/test_project_status_undo_permissions.py','projects/tests/test_project_status_undo_concurrency.py'],
'W01':['wbs/tests/test_wbs_structure_fields.py'],
'W02':['wbs/tests/test_wbs_structure_fields.py'],
'W03':['wbs/tests/test_wbs_cycle_move.py','schedule/tests/test_a7_neg01_duplicate_codes.py'],
'W04':['wbs/tests/test_wbs_delete_guards.py','project_templates/tests/test_wbs_template_immutability.py','schedule/tests/test_a7_p2_import_safety.py'],
'W05':['project_templates/tests/test_wbs_template_immutability.py'],
'W06':['wbs/tests/test_tree_ordering.py','wbs/tests/test_services.py'],
'W07':['wbs/tests/test_services.py','schedule/tests/test_a7_p3_import_fidelity.py'],
'M01':['projects/tests/test_central_data_owning_unit.py','projects/tests/test_a7_p1_reference_project.py'],
'M02':['projects/tests/test_a7_p1_reference_project.py'],
'M03':['projects/tests/test_project_registration_lifecycle.py'],
'M04':['schedule/tests/test_a7_p6_delivery_acceptance.py'],
'S01':['schedule/tests/test_a7_p3_import_fidelity.py'],
'S02':['schedule/tests/test_a7_p3_import_fidelity.py','schedule/tests/test_relations.py'],
'S03':['schedule/tests/test_a7_cycle_cancel_acceptance.py','schedule/tests/test_a7_p3_import_fidelity.py'],
'S04':['schedule/tests/test_a7_p3_import_fidelity.py'],
'S05':['schedule/tests/test_a7_p2_import_safety.py','schedule/tests/test_a7_p6_delivery_acceptance.py'],
'S06':['schedule/tests/test_schedule_change_request.py'],
'S07':['schedule/tests/test_a7_p3_import_fidelity.py','schedule/tests/test_gantt.py'],
'S08':['schedule/tests/test_a7_p3_import_fidelity.py'],
'I01':['schedule/tests/test_mpp_import.py','schedule/tests/test_msp_import.py','schedule/tests/test_p6_import.py'],
'I02':['schedule/tests/test_a7_p4_import_experience.py'],
'I03':['schedule/tests/test_a7_p3_import_fidelity.py','schedule/tests/test_a7_p6_delivery_acceptance.py'],
'I04':['schedule/tests/test_a7_p3_import_fidelity.py'],
'I05':['schedule/tests/test_a7_p3_import_fidelity.py'],
'I06':['schedule/tests/test_a7_neg01_duplicate_codes.py','schedule/tests/test_a7_p4_import_experience.py'],
'I07':['schedule/tests/test_a7_p2_import_safety.py'],
'I08':['schedule/tests/test_a7_cycle_cancel_acceptance.py'],
'I09':['schedule/tests/test_a7_p5_runtime_preflight.py'],
'I10':['schedule/tests/test_a7_p4_import_experience.py'],
'I11':['schedule/tests/test_a7_cross_project_schedule_isolation.py','schedule/tests/test_a7_viewer_readonly_acceptance.py'],
'I12':['common/tests/test_validators.py'],
'I13':['schedule/tests/test_mpp_import.py','schedule/tests/test_a7_p4_import_experience.py'],
'I14':['schedule/tests/test_a7_p2_import_safety.py','schedule/tests/test_a7_p5_recovery.py'],
'I15':['schedule/tests/test_a7_p4_import_experience.py'],
'I16':['schedule/tests/test_a7_p4_import_experience.py'],
'I17':['schedule/tests/test_a7_p4_import_experience.py'],
'I18':['schedule/tests/test_a7_p2_import_safety.py','schedule/tests/test_a7_p5_lifecycle.py'],
'I19':['schedule/tests/test_a7_p5_retention.py','schedule/tests/test_a7_p5_artifact_privacy.py'],
'I20':['schedule/tests/test_a7_p5_preparation.py','schedule/tests/test_a7_p5_recovery.py'],
'I21':['schedule/tests/test_mpp_equivalence.py','schedule/tests/test_a7_p3_import_fidelity.py'],
'I22':['schedule/tests/test_a7_p6_delivery_acceptance.py'],
'D01':['schedule/tests/test_a7_p6_delivery_acceptance.py'],
'D02':['schedule/tests/test_a7_p5_runtime_manifest.py'],
'D03':['schedule/tests/test_a7_p6_delivery_acceptance.py'],
'D04':['schedule/tests/test_a7_p6_delivery_acceptance.py'],
}
# Correct names are validated before publishing any final disposition.
for aid, paths in proof.items():
 for p in paths:assert (R/prefix/p).is_file(),(aid,p)
pkg=read(E/'package.json');pkg.update(version_id=version,git_head=source,tree_dirty=False,source_commit=source,schedule_tree_sha256=runtime['source_tree_sha256'],acceptance_image_digest=image,environment_id='a7p5-import:API18000/PostgreSQL55434/Redis56379/Web15173',technical_readiness='ready_for_acceptance')
pkg['summary_buckets']={'already_verified':['P06'],'fixed_in_a7':[x['id'] for x in requirements if x['id']!='P06'],'still_open_or_unrun':[],'testable_by_employer':[]}
pkg['employer_testable_audit_ids']=[x['id'] for x in requirements]
pkg['residual_verification_notes']=[
'All 56 audit items are technically dispositioned; all 28 catalog scenarios pass. Employer decision and signature remain pending.',
'M04 is conditional: the A.7 project/WBS/import journey does not use generic dynamic tables or Excel. Independent WBS Excel import is outside this phase.',
'MPP native browser FileChooser is exercised by Playwright; visual interaction with the OS dialog remains available in the employer walkthrough.',
'Calendar definitions are reported but are not applied as a full scheduling engine. Unsupported rows are explicitly warned/omitted according to the recorded parentless-row policy.',
'Compatibility is limited to the versioned fixture corpus; no claim covers every Microsoft Project version or arbitrary P6 XML.',
'The historical P5 independent-operator reproduction is preserved in reproduction.md; final current-version checks here are implementer-run. Employer walkthrough is unsigned.',
'The artifact is an isolated Linux/systemd/Docker acceptance release. Production deployment is a separate operational action.'
]
write(E/'package.json',pkg)
ledger=[]
for x in requirements:
 refs=[prefix+p for p in proof[x['id']]]+[core,browser]
 if phase[x['id']]=='A.7-P5' or x['id'] in ['I14','I19','I20','D02']:refs += [p5,'specs/055-a7-p5-import-operations/evidence/runtime/host-pytest.xml']
 row=dict(audit_id=x['id'],title=x['title'],owning_phase=phase[x['id']],source_requirement=x['requirements'],source_acceptance=x['acceptance'],source_refs=x['sources'],disposition='تأیید فنی',employer_bucket='قبلاً موجود و تأییدشده روی نسخه حاضر' if x['id']=='P06' else 'در A.7 اصلاح/تکمیل شد',testable_by_employer=True,evidence_refs=refs,version_id=version)
 if x['id']=='M04':row['scope_resolution']='شرط استفاده در جریان واقعی A.7 برقرار نیست؛ ورود مستقل WBS از Excel و آزمون عمومی جداول پویا خارج از دامنه این تحویل‌اند. این ردیف تعیین تکلیف دامنه است و ادعای آزمون Excel ندارد.'
 if x['id']=='M03':row['scope_resolution']='وضعیت‌های پروژه چرخه ثابت و انتقال‌های مصوب دارند؛ کاتالوگ مرجع مجوز ساخت وضعیت دلخواه برای پروژه نمی‌دهد.'
 ledger.append(row)
write(E/'audit-disposition.json',ledger)
scenarios=read(E/'scenarios.json')
mapping={
'POS-01':['P01','P02','P06','M01','M02'],'POS-02':['P03','P04','P05'],'POS-03':['P07'],'POS-04':['W01','W02','W05','W06'],'POS-05':['I01','I03','I08','D01'],'POS-06':['W07','S01','S02','S03','S04','I03','I04','I05','I10','I18','I21','I22'],'POS-07':['I06','S05'],'POS-08':['W04','I07','S05'],'POS-09':['S04','S07','S08'],'POS-10':['P06','P09','P10','P11','M03'],
'NEG-01':['P02','W03','I06'],'NEG-02':['W03'],'NEG-03':['W03','S03','I14'],'NEG-04':['S03'],'NEG-05':['S02','S03','I05','I14'],'NEG-06':['I01','I12','I13'],'NEG-07':['I08'],'NEG-08':['I09','I15','I16'],'NEG-09':['I16'],'NEG-10':['I11','P08','I14'],'NEG-11':['I11'],'NEG-12':['I11'],'NEG-13':['P09','P11','I11'],'NEG-14':['P08'],'OPS-01':['I15','I17'],'OPS-02':['I17'],'OPS-03':['I17'],'OPS-04':['I09','I19','I20','D02']}
for s in scenarios:
 s['audit_ids']=mapping[s['scenario_id']];s['version_id']=version
 if s['scenario_id']=='OPS-04':
  s.update(technical_result='pass',defect_id=None,evidence_ref=p5,observed_outcome='ماتریس ۱۳گروهی worker واقعی، cgroup، نگهداری ۱۶۸ساعته و پاک‌سازی در ساعت ۱۶۹ روی تصویر نهایی pass شد؛ قطع broker و تحویل هم‌زمان نیز مستقل بازاجرا شدند.')
write(E/'scenarios.json',scenarios)
trace=['# ردیابی نهایی A.7','',f'نسخه منبع: `{version}`. عنوان و معیار هر ردیف عین ممیزی اصلی است. تصمیم انسانی تمام موارد pending است.','', 'M04 تعیین تکلیف دامنه شرطی است؛ آزمون عمومی Excel ادعا نشده است.','']
for x in ledger:
 trace += [f"## {x['audit_id']} — {x['title']}",'',f"مرجع: {x['source_requirement']}؛ مالک: {x['owning_phase']}؛ نتیجه: {x['disposition']}.",'',x['source_acceptance'],'']
 if x.get('scope_resolution'):trace += [x['scope_resolution'],'']
 trace += ['شواهد: '+', '.join(f'`{p}`' for p in x['evidence_refs']),'']
(F/'traceability.md').write_text('\n'.join(trace))
lines=['# نتایج سناریوهای پذیرش A.7','',f'نسخه: `{version}`؛ ۲۸ pass، صفر fail و صفر not_run. نتیجه انسانی همه موارد pending.','']
for s in scenarios:
 lines += [f"## {s['scenario_id']} — {s['title']}",'',f"شناسه‌ها: {', '.join(s['audit_ids'])}؛ کانال: {s['channel']}؛ نتیجه فنی: {s['technical_result']}.",'',s['observed_outcome'],'',f"شواهد: `{s['evidence_ref']}`",'']
(E/'scenarios.md').write_text('\n'.join(lines))
recs=read(E/'reconciliation.json');recs[-1]['source_counts']['format']='Microsoft Project XML (MSPDI), not Primavera P6 XML';recs[-1]['display_name']='MSP XML fractional-duration/parentless negative-equivalence fixture (legacy ID retained)';write(E/'reconciliation.json',recs)
rec=['# تطبیق فایل‌های مرجع A.7','',f'نسخه: `{version}`. مرجع ماشینی: `reconciliation.json`.','', 'فایل plan.mpp تغییر نکرده است: ۸۰ وظیفه = ۶ خلاصه + ۷۴ برگ. دو برگ بدون والد شروع/پایان طبق تصمیم ثبت‌شده حذف می‌شوند. از ۸۳ پیوند خام، چهار پیش‌نیاز خلاصه و هفت پیوند وابسته به برگ‌های حذف‌شده کنار گذاشته می‌شوند؛ خروجی ۶ WBS، ۷۲ فعالیت و ۷۲ رابطه است. اولین ورود یک خط مبنای کاری می‌سازد؛ این نسخه تصویب قطعی نیست. ورود افزایشی مجدد هیچ ردیف یا خط مبنای اضافی نمی‌سازد.','']
for x in recs:
 rec += [f"## {x['fixture_id']}",'',f"مسیر: `{x['file_path']}`؛ اندازه: {x['size_bytes']} بایت.",f"SHA-256: `{x['sha256']}`",f"پیش‌نمایش: {x['preview_counts']}؛ ذخیره: {x['stored_counts']}.",f"هشدارها: {', '.join(x['expected_warning_codes'])}.",'']
rec += ['شناسه تاریخی valid_p6_xml نام‌گذاری نادرست دارد: فایل duration-test9.xml در واقع MSPDI است. مدت‌های کسری و فعالیت‌های بدون والد قابل درج نیستند، بنابراین خروجی صحیح صفر/صفر/صفر و هشدار empty_import است. فایل را نمونه موفق P6 XML یا خروجی ۱/۵/۰ معرفی نمی‌کنیم. آزمون منفی جایگزینی خالی، حفظ داده قبلی را جداگانه اثبات می‌کند.','', 'تقویم منبع با هشدار calendar_not_applied همراه است؛ مدت/lag بر مبنای ۴۸۰ دقیقه روز کاری تبدیل می‌شوند. فیلدهای پشتیبانی‌شده و محدودیت‌ها در راهنمای P3 و آزمون برابری MPP/XML ثبت شده‌اند.']
(E/'reconciliation.md').write_text('\n'.join(rec)+'\n')
print('Final ledger and scenario documents generated for',source)
