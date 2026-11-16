> **Current A.7 delivery overlay — 2026-11-16:** source `2090da13f90756e9512070ffcd4feb87dcf5fd7a`, API image `sha256:0e4bef19068e6b36da9f7de2169486cd3fe73b7ec1f2f3a1c96ae60a62067066`, schedule digest `095000ea6961e55eb8b9c0a8ed67692a826bda99ba602a28321c1e06abb1dc10`. Current matrix 13/13, broker/concurrent checks, 110 host regressions and 29 final browser checks pass; see `../056-a7-p6-delivery-acceptance/evidence/release-verification.json`. Earlier versions/independent-operator entries below are historical. Current final runs are implementer-run and do not imply employer sign-off.

# US2: effective containment

The rebuilt image `sha256:9f3b7c98d5a7f6d4a6392a2830794c221730e7fa086f9efa0307030b3cfd03d5` passed the resource group, including memory, pids, output, disk, synchronous preview and start limits, and a healthy import afterward. JPype and the configured Java CLI both stored 6/72/72 from the unchanged reference file. Peaks and outcomes are in [runtime/manifest.json](runtime/manifest.json) group `resource_limit`.



Linux cgroup-v2 delegation is limited to transient a7p5-containment.service. Containers bind only its subtree; helper groups use1GiB memory, swap0, pids32 and one-CPU quota. Dedicated scratch is a256MiB tmpfs, prepared output128MiB, diagnostic capture64KiB, JVM heap512MiB, one processing slot. Conversion shares a60-second deadline across routes; full preparation75seconds and kill grace2seconds. The final preflight records effective settings and responding dedicated queue consumers.

Actual root runtime enforced kernel OOM, output expansion, scratch ENOSPC,75-second sleep timeout and parent SIGKILL. Each failure left no partial domain data or owned helper workspace and a healthy import succeeded afterward. Kernel regression probes additionally attach a real child, read exact effective controls, terminate/reap/remove its group and cause a real32MiB test-group OOM. Final runtime extends this with actual pids exhaustion and synchronous preview/start output-limit rejection.

JPype and configured Java CLI both converted the employer file in a fresh contained helper and stored matching figures. CLI uses the class present in configured jars (current org.mpxj or legacy net.sf.mpxj), heap/temp bounds and bounded diagnostic reads. Timeout/resource failures cannot start fallback. The tested JRE/MPXJ/JPype versions and source/image identity come from runtime/manifest.json and reproduction.md. No universal MSP-version compatibility is claimed.

These are private engineering acceptance limits, not a customer throughput SLA. Host inline tests are not counted as conversion/worker containment proof.

Final independent clean matrix passed all10 groups on source44c00c17b99275157900da0c3fe0f23d9b9d307ae033d36c21b55a13cf3bff36. See runtime/manifest.json for exact attempts, counts, controls, versions and results. Recovery/purge each processed201 rows (1.449s/1.796s; bounds2553s/6093s), including a temporary real row lock, later arrival and competing leader;201 owned scratch workspaces were removed with unrelated content preserved. These are fixture-sized observations under the recorded engineering profile, not a throughput SLA. Additional broker/concurrent/browser checks are in reproduction.md.
