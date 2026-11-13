#!/usr/bin/env bash
set -euo pipefail
# Owns only this named transient unit and dedicated scratch mount.
unit=a7p5-containment.service
cg=/sys/fs/cgroup/system.slice/$unit
scratch=/run/a7p5-scratch
if ! systemctl is-active --quiet "$unit"; then
  sudo systemd-run --unit="$unit" --property=Delegate=yes --property=Type=exec /bin/sleep infinity
fi
[[ $(systemctl show "$unit" --property=ControlGroup --value) == /system.slice/$unit ]]
sudo mkdir -p "$cg/manager"
while read -r owner_pid; do
  [[ -z "$owner_pid" ]] || printf '%s\n' "$owner_pid" | sudo tee "$cg/manager/cgroup.procs" >/dev/null
done < "$cg/cgroup.procs"
printf '+memory +pids +cpu\n' | sudo tee "$cg/cgroup.subtree_control" >/dev/null
sudo chown "$(id -u):$(id -g)" "$cg" "$cg/cgroup.procs" "$cg/cgroup.subtree_control"
sudo mkdir -p "$scratch"
if ! mountpoint -q "$scratch"; then
  sudo mount -t tmpfs -o "size=256m,mode=0700,uid=$(id -u),gid=$(id -g)" a7p5-scratch "$scratch"
fi
[[ $(findmnt -n -o FSTYPE --target "$scratch") == tmpfs ]]
sudo chown "$(id -u):$(id -g)" "$scratch"
printf 'A7P5_CGROUP_HOST_ROOT=%s\nA7P5_SCRATCH_HOST_ROOT=%s\n' "$cg" "$scratch"
