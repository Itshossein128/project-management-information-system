#!/usr/bin/env bash
# Persistent, narrowly delegated resources for production schedule import.
set -euo pipefail
[[ $(id -u) == 0 ]] || { echo 'Run this host setup as root.' >&2; exit 1; }
[[ $(stat -fc %T /sys/fs/cgroup) == cgroup2fs ]] || { echo 'cgroup v2 is required.' >&2; exit 1; }
install -d -m 0755 /usr/local/libexec /var/lib/velora/importscratch
cat > /usr/local/libexec/velora-import-cgroup <<'CG'
#!/usr/bin/env bash
set -euo pipefail
cg=/sys/fs/cgroup/system.slice/velora-import-containment.service
[[ $(systemctl show velora-import-containment.service --property=ControlGroup --value) == /system.slice/velora-import-containment.service ]]
mkdir -p "$cg/manager"
while read -r owner_pid; do
  [[ -z "$owner_pid" ]] || printf '%s\n' "$owner_pid" > "$cg/manager/cgroup.procs"
done < "$cg/cgroup.procs"
printf '+memory +pids +cpu\n' > "$cg/cgroup.subtree_control"
CG
chmod 0755 /usr/local/libexec/velora-import-cgroup
cat > /etc/systemd/system/velora-import-containment.service <<'UNIT'
[Unit]
Description=Delegated Velora import containment
After=local-fs.target
Before=docker.service
[Service]
Type=exec
Delegate=yes
ExecStart=/usr/bin/sleep infinity
ExecStartPost=/usr/local/libexec/velora-import-cgroup
Restart=always
[Install]
WantedBy=multi-user.target
UNIT
cat > /etc/systemd/system/var-lib-velora-importscratch.mount <<'UNIT'
[Unit]
Description=Bounded Velora import scratch
Before=docker.service
[Mount]
What=tmpfs
Where=/var/lib/velora/importscratch
Type=tmpfs
Options=size=256m,mode=0700
[Install]
WantedBy=local-fs.target
UNIT
systemctl daemon-reload
systemctl enable --now var-lib-velora-importscratch.mount velora-import-containment.service
/usr/local/libexec/velora-import-cgroup
[[ $(findmnt -n -o FSTYPE --target /var/lib/velora/importscratch) == tmpfs ]]
[[ $(findmnt -n -b -o SIZE --target /var/lib/velora/importscratch) -le 268435456 ]]
echo 'Production import cgroup and bounded scratch are ready.'
