# Summary: `data base shiraz (1).xlsx`

## Overview
Primary historical operations database for the **2,000-Unit National Housing Project in Komeil Abad, Shiraz (پروژه مسکن ملی کمیل‌آباد شیراز)** executed by **Pey Chin Co. (شرکت پی چین)**. It consolidates daily site activities, weather logs, site obstacles, labor camp occupancy, personnel headcounts, and machinery utilization from `1402/06/28` through `1404/09/30`.

## File Metadata
- **Source File**: `data base shiraz (1).xlsx`
- **File Size**: ~4.68 MB (4,678,781 bytes)
- **Total Sheets**: 9
- **Date Coverage**: `1402/06/28` – `1404/09/30` (primarily `1403` through end of `1404/06`, with machinery/weather logs extending to `1404/09/30`)

## Sheet Breakdown
| Sheet Name | Non-Empty Rows | Description & Key Columns |
| :--- | :---: | :--- |
| `ACTIVITY ` | 11,275 | Daily construction activity log (`1402/06/28` – `1404/06/31`). Tracks date, activity description, shift, contractor, headcount, zone (`قطعه`), block (`بلوک`), floor (`طبقه`), location, quantity, and unit. |
| `Sheet12` | 615 | Dedicated work log for structural contractor **Mr. Khaneka (آقای خنکا)** starting `1403/05/29` (rebar cutting/bending, ramka alignment, formwork, concreting). |
| `weather` | 278 | Daily project weather and site status log (`1403/01/01` – `1403/09/30`): min/max temperature, weather condition, and active/inactive workshop status. |
| `problems` | 1,310 | Log of daily project obstacles and bottlenecks (`1403/01/01` – `1404/06/22`), including drawing revisions, equipment breakdowns, and payment/material delays. |
| `labor camp report` | 5,125 | Worker camp container (`کانکس`) occupancy log (`1403/02/30` – `1403/10/04`): container number, contractor, assigned workers, present, on leave, total capacity, and vacant capacity. |
| `personnel report` | 2,631 | Aggregated daily headcount by personnel category (HQ staff, drivers/operators, security, daily-wage workers, contractors) across Shifts 1, 2, and 3 (`1403/02/01` – `1403/10/04`). |
| `MACHINE DATA BANK 1` | 30,669 | Detailed daily machinery log (`1403/01/15` – `1404/09/30`): equipment name, status (`فعال` / `آماده` / `خراب`), ownership (`تملیکی` / `اجاره‌ای`), start/end times, repair hours, and net operating hours. |
| `manpower` | 34,533 | Granular daily headcount by job title (`عنوان شغلی`) in person-days from `1403/01/01` to `1404/06/31`. |
| `mashinery` | 18,510 | Daily summary counts of machinery and equipment (`کل`, `فعال`, `آماده به کار`, `غیر فعال`, `در دست تعمیر`) from `1403/01/01` to `1404/06/31`. |
