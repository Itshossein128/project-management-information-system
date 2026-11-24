# B03 synthetic outputs for B05

These downloads and print previews use the labeled synthetic `SIM-A1-001` fixture in isolated Velora databases. The artifact set supports B05's independent reconciliation and B06's later employer acceptance.

## Daily cases

- Reference report, `fb9bcd42-a786-4b19-ba7b-1548c9526393`, number `SIM-A1-001-12-1406-03-01`. [FA Excel](normal-fa.xlsx), [FA PDF](normal-fa.pdf), [EN Excel](normal-en.xlsx), [EN PDF](normal-en.pdf), [A4 print preview](normal-fa-print-preview.pdf).
- Inactive holiday, `84b5f113-d71f-5ac8-a194-5759e9052047`. [Excel](inactive-fa.xlsx), [PDF](inactive-fa.pdf).
- Measured zero, `a7051254-2a55-5675-9386-3acdf09c7cb5`. [Excel](zero-fa.xlsx), [PDF](zero-fa.pdf).
- Unknown hours, `e2bbd5dc-ac69-5c69-8afd-2e87fd43db58`. [Excel](unknown-fa.xlsx), [PDF](unknown-fa.pdf).
- Three worked shifts, `b21661df-88e7-59f9-befc-718e1ab746fa`. [Excel](three-shift-fa.xlsx), [PDF](three-shift-fa.pdf).
- Long bilingual draft, `49248f37-a9a5-5db4-9d73-6c1f8b54091d`, 56 activity rows. [Excel](long-fa.xlsx), [FA PDF](long-fa.pdf), [EN PDF](long-en.pdf), [A4 print preview](long-fa-print-preview.pdf).
- The inclusive limit sample contains 31 current approved dates, 12 activity rows per date, and one worksheet per date from 1406-03-11 through 1406-04-10. [Range workbook](range-31.xlsx).

## Unit files

- Buildings draft, `03a7296e-50b7-5713-bc0e-f063f566ca7e`. [FILE 5](civil-subreport-1406-03-01.xlsx), [PDF](unit-daily-report-buildings-1406-03-01.pdf).
- Electrical draft, `e583436f-9196-5769-bb6e-82a0e375f775`. [FILE 6](electrical-subreport-1406-03-01.xlsx), [PDF](unit-daily-report-electrical-1406-03-01.pdf).
- Mechanical draft, `28c52e9a-4ee1-5e96-8ea8-ca49364f92a4`. [PDF](unit-daily-report-mechanical-1406-03-01.pdf).
- Machinery draft, `5db0ea20-970d-5051-b671-c293a35b007c`. [PDF](unit-daily-report-machinery-1406-03-01.pdf).
- Warehouse draft, `b40c8193-2504-5580-b793-dc4643906517`. [PDF](unit-daily-report-warehouse-1406-03-01.pdf).
- Security draft, `fde41cb0-b5de-562d-918f-d2585c464580`. [PDF](unit-daily-report-security-1406-03-01.pdf).
- Long buildings draft, `a3775c16-c494-5a4c-b3d7-d2b25a286550`. It reuses all 56 activity descriptions from the long daily draft and sets recorded progress to 45.5%. [FILE 5](long-unit-fa.xlsx), [A4 print preview](long-unit-fa-print-preview.pdf), [FA PDF](long-unit-fa.pdf), [EN PDF](long-unit-en.pdf).

## Source and verification

- [B01 source fixture](../../../apps/api/core/field_reports/fixtures/sim_a1_001_1406_03_01.json)
- [B03 fixture preparation](../prepare-fixtures.py)
- [Implementation evidence](../implementation-evidence.md)
- [Export contract](../contracts/exports.md)
