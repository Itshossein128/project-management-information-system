#!/usr/bin/env bash
# Reassemble the exact immutable offline artifact inside GitHub's network.
set -euo pipefail
release_tag=a7-2026-11-16
archive=a7-delivery-2026-11-16.tar
mkdir artifact-parts
cd artifact-parts
gh release download "$release_tag" --pattern "$archive.part-*" --pattern "$archive.sha256"
parts=("$archive".part-*)
[[ ${#parts[@]} == 25 ]]
cat "${parts[@]}" > "$archive"
sha256sum -c "$archive.sha256"
gh release upload "$release_tag" "$archive" --clobber
expected=$(cut -d ' ' -f1 "$archive.sha256")
actual=$(gh api "repos/$GH_REPO/releases/tags/$release_tag" --jq ".assets[] | select(.name == \"$archive\") | .digest")
[[ "$actual" == "sha256:$expected" ]]
for part in "${parts[@]}"; do
  gh release delete-asset "$release_tag" "$part" --yes
done
echo "Immutable A.7 artifact uploaded and verified: $expected"
