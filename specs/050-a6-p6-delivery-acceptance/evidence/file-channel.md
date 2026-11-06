# Live file channel

version_id: `a46161d3530edfb78c8ebf94b4786d991bea0ba7`

`file_service`: `blocked_external`

`AWS_S3_ENDPOINT_URL` is set in the local environment, and ports 9000 and 9001 were not listening. `apps/api/core/storage/tests_integration.py` did not return; the client waited on the object store and the process was stopped. No upload, other-project download, or post-revoke download was recorded.

`apps/api/core/storage/tests/test_stored_file_access.py` passed inside the direct-request suite. That result stays in the API channel. It is not this live-file result.
