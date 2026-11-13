# Fixtures and isolation

`real-data/plan.mpp` was not copied or modified.

- SHA-256: `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`
- Size: 777216 bytes

Supported XML/XER samples used by the new tests live in the existing schedule test modules (`SAMPLE_MSP_XML`, `SAMPLE_XER`). Corrupt input covered by the API test is `<not-project/>`, which is rejected before a job row.

Disposable identities for the acceptance stack, not used by the unit tests:

- Compose project: `a7p5-import`
- Database: `a7p5_import` on host port `55432`
- Redis: host port `56379`
- Queues: `a7p5-import`, `a7p5-maintenance`
- Scratch: `/var/a7p5-scratch` inside those containers

This machine has Java `21.0.12.1`, Docker, and Postgres on `5433`. `/sys/fs/cgroup` is not writable here, so kernel containment was not exercised. Unit tests use the normal test database and do not delete shared uploads.
