"""Package the verified A.7 candidate without touching the user's Git index."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
E = ROOT / 'specs/056-a7-p6-delivery-acceptance/evidence'
pkg = json.loads((E/'package.json').read_text())
source = pkg['source_commit']
assert pkg['technical_readiness'] == 'ready_for_acceptance'
subprocess.run([sys.executable, str(E/'validate_package.py')], check=True)
out = ROOT / 'output/a7-delivery-2026-11-16'
out.mkdir(parents=True, exist_ok=True)
# Only the delivery-owned documentation is added to a separate temporary index.
with tempfile.TemporaryDirectory(prefix='a7-package-index-') as directory:
    env = {**os.environ, 'GIT_INDEX_FILE': str(Path(directory)/'index')}
    subprocess.run(['git','read-tree',source], env=env, check=True)
    subprocess.run(['git','add','--',*[f'specs/{name}' for name in [
        '051-a7-p1-project-reference','052-a7-p2-import-safety',
        '053-a7-p3-import-fidelity','054-a7-p4-import-experience',
        '055-a7-p5-import-operations','056-a7-p6-delivery-acceptance']]], env=env, check=True)
    tree = subprocess.check_output(['git','write-tree'],env=env,text=True).strip()
    delivery = subprocess.check_output(['git','commit-tree',tree,'-p',source,'-m','docs(a7): freeze verified employer acceptance handoff'],env=env,text=True).strip()
branch = f'codex/a7-delivery-20261116-{source[:8]}'
subprocess.run(['git','update-ref',f'refs/heads/{branch}',delivery],check=True)
# A depth-2 source copy includes the exact code and evidence commits, without
# shipping unrelated repository history or any local remotes/credentials.
with tempfile.TemporaryDirectory(prefix='a7-export-') as directory:
    clone = Path(directory)/'source'
    subprocess.run(['git','clone','--quiet','--depth=2','--branch',branch,ROOT.as_uri(),str(clone)],check=True)
    subprocess.run(['git','-C',str(clone),'remote','remove','origin'],check=True)
    assert subprocess.check_output(['git','-C',str(clone),'status','--porcelain'],text=True) == ''
    subprocess.run([sys.executable,str(clone/'specs/056-a7-p6-delivery-acceptance/evidence/validate_package.py')],cwd=clone,check=True)
    with tarfile.open(out/'source.tar.gz','w:gz',compresslevel=1) as archive:
        archive.add(clone,arcname='source')
images = ['a7p5-api:acceptance','a7p5-web:acceptance','postgres:16-alpine','redis:7-alpine']
image_ids = {name:subprocess.check_output(['docker','image','inspect',name,'--format','{{.Id}}'],text=True).strip() for name in images}
assert image_ids['a7p5-api:acceptance'] == pkg['acceptance_image_digest']
with (out/'runtime-images.tar.gz').open('wb') as target:
    save = subprocess.Popen(['docker','save',*images],stdout=subprocess.PIPE)
    compress = subprocess.Popen(['gzip','-1'],stdin=save.stdout,stdout=target)
    save.stdout.close()
    assert compress.wait() == 0 and save.wait() == 0
with tarfile.open(out/'web-build.tar.gz','w:gz',compresslevel=1) as archive:
    archive.add(ROOT/'apps/web/build',arcname='apps/web/build')
for filename in ['guide.md','handoff.md','quickstart.md']:
    shutil.copy2(E.parent/filename,out/filename)
shutil.copy2(E/'minutes.md',out/'minutes.md')
shutil.copy2(E/'release-verification.json',out/'release-verification.json')
shutil.copy2(E/'package-validator.json',out/'package-validator.json')
release = {'source_commit':source,'delivery_commit':delivery,'branch':branch,'images':image_ids,'employer_decision':'pending','technical_readiness':'ready_for_acceptance'}
(out/'RELEASE.json').write_text(json.dumps(release,ensure_ascii=False,indent=2)+'\n')
(out/'README-fa.md').write_text(f'''# بسته تحویل فنی A.7 — ۲۰۲۶/۱۱/۱۶

نسخه منبع: `{source}`
نسخه حاوی شواهد و راهنما: `{delivery}`

آمادگی فنی `ready_for_acceptance` است. نتیجه انسانی `pending` و صورت‌جلسه بدون امضا است. دامنه و محدودیت‌های مصوب در guide.md آمده است. این بسته برای پذیرش مستقل در Linux x86_64 دارای systemd، cgroup v2 و Docker Compose آماده شده است. تمام سرویس‌ها روی localhost هستند.

## کنترل و راه‌اندازی بدون دانلود وابستگی

از همین پوشه:

```bash
sha256sum -c SHA256SUMS
gunzip -c runtime-images.tar.gz | docker load
tar -xzf source.tar.gz
cd source
ops/a7-p5/prepare-host.sh
cp -n ops/a7-p5/.env.acceptance.example ops/a7-p5/.env.acceptance
chmod 600 ops/a7-p5/.env.acceptance
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml -f ops/a7-p5/compose.web.yml up -d --no-build --pull never
```

تصاویر API، workerها، وب کامپایل‌شده، PostgreSQL و Redis داخل آرشیو هستند. برای شروع نیاز به pnpm، نصب package یا build مجدد ندارید. Runtime وب همان باینری Node آزموده‌شده و وابستگی‌های قفل‌شده را دارد؛ لایه پایه آن با API مشترک است. اگر پوشه خروجی وب جداگانه لازم است، از ریشه source، فایل ../web-build.tar.gz را باز کنید.

پس از healthy شدن API و آماده شدن worker:

```bash
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml exec -T api python manage.py verify_import_runtime --preflight
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml exec -T api python manage.py maintain_import_jobs --operation recovery
python3 ops/a7-p5/seed-delivery.py
```

preflight تا آماده شدن worker ممکن است نیاز به تکرار داشته باشد. بازکردن `http://127.0.0.1:15173/login` و ورود با پنج حساب فایل خصوصی ops/a7-p5/.runtime-delivery.json، نقطه شروع guide.md است. فایل حساب‌ها فقط روی همین محیط با مجوز 0600 ساخته می‌شود و داخل بسته عمومی نیست. اسکریپت seed تنها روی دیتابیس خصوصی a7p5 اجرا می‌شود.

API روی 18000، پایگاه خصوصی روی 55434، Redis خصوصی روی 56379 و وب روی 15173 است. پورت پایگاه با A7P5_POSTGRES_PORT قابل تغییر است. فایل plan.mpp و fixtureها در source/real-data و specs هستند. منبع دارای Git با تاریخچه محدود به دو commit تحویل است؛ هیچ remote خصوصی یا تاریخچه نامرتبطی صادر نشده است.

## بازبینی و آزمون

از ریشه source با Python 3:

```bash
python3 specs/056-a7-p6-delivery-acceptance/evidence/validate_package.py
git log --oneline -2
```

اعتبارسنج بدون سرویس، تمامیت شواهد ثبت‌شده، نسخه و منبع را بررسی می‌کند؛ اجرای دوباره آزمون‌ها از quickstart.md به وابستگی‌های توسعه، Node/pnpm، مرورگر Playwright و PostgreSQL/Redis تست میزبان نیاز دارد. تصاویر آماده برای اجرای نمایش کارفرما به این ابزارهای توسعه نیاز ندارند. محیط پذیرش، حساب‌ها و داده آزمایشی مستقل‌اند؛ اتصال داده واقعی یا انتشار عمومی جزء اجرای این راه‌اندازی نیست.

مستندات: guide.md مسیر نمایش؛ minutes.md محل ثبت نظر و امضای نماینده؛ handoff.md و release-verification.json هویت و شواهد؛ RELEASE.json شناسه تصویرها؛ SHA256SUMS کنترل فایل‌ها. تمام ۵۶ ردیف و ۲۸ سناریو در source/specs/056-a7-p6-delivery-acceptance/evidence قرار دارند. M04 تعیین تکلیف شرطی دامنه است و ادعای آزمون Excel عمومی ندارد.

برای توقف فقط همین محیط از همان دو فایل Compose و دستور down استفاده کنید. حذف داده‌های پذیرش با down -v تنها پس از نگهداری شواهد جلسه انجام شود. سرویس‌های مشترک و تولیدی را تغییر ندهید.
''')
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as src:
        for chunk in iter(lambda:src.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
files=sorted(p for p in out.iterdir() if p.is_file() and p.name!='SHA256SUMS')
(out/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in files))
print(json.dumps({'output':str(out),'source_commit':source,'delivery_commit':delivery,'files':len(files)},indent=2))
