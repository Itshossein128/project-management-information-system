# MPP compatibility corpus

Themes required by `specs/029-native-mpp-import`:

| File | Purpose |
|------|---------|
| `duration-test9.mpp` | Readable genuine MPP (hierarchy / durations) |
| `duration-test9.xml` | Paired MSPDI from same schedule (equivalence) |
| `password-protected.mpp` | Password-protected → `mpp_password_protected` |
| `renamed-not-mpp.mpp` | Wrong content + `.mpp` name → `invalid_file_type` |
| `truncated-ole.mpp` | OLE magic only → corrupt/unreadable |

Requires JRE + MPXJ classpath (`MPP_MPXJ_CLASSPATH` or `/tmp/mpxj.jar` + `/tmp/mpxj-lib/*.jar`) for live conversion tests.
