# Secret scan

The scanner covers every Markdown and JSON file under `specs/050-a6-p6-delivery-acceptance/evidence/` except intentional negative samples in `fixtures/`, plus the sibling `guide.md`.

It matches assigned secrets, quoted JSON secret fields, HTTP bearer headers, and recovery URLs that carry a token parameter. A match is reported as `secret pattern matched in <path>; value omitted`.

The acceptance scan of the package and the guide exited 0. The negative samples exited 1.
