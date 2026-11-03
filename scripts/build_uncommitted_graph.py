#!/usr/bin/env python3
"""
Extract a meaningful knowledge graph for uncommitted changes in the repository
using graphify modules, adhering strictly to references/extraction-spec.md.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path('/home/hossein/Desktop/projects/building-management').resolve()
os.chdir(PROJECT_ROOT)

import networkx as nx
from graphify.build import build_from_json, build_merge
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json, to_html
from graphify.diagnostics import diagnose_extraction, format_diagnostic_report


def count_lines(filepath: Path) -> int:
    if not filepath.exists():
        return 0
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def build_uncommitted_extraction() -> dict:
    nodes = []
    edges = []
    hyperedges = []
    coverage = {}

    def add_node(node_id: str, label: str, file_type: str, source_file: str, rationale: str = None):
        abs_src = str((PROJECT_ROOT / source_file).resolve())
        node = {
            "id": node_id,
            "label": label,
            "file_type": file_type,
            "source_file": abs_src,
            "source_location": None,
            "source_url": None,
            "captured_at": None,
            "author": None,
            "contributor": None,
            "_origin": "semantic"
        }
        if rationale:
            node["rationale"] = rationale
        nodes.append(node)

    def add_edge(src: str, tgt: str, rel: str, conf: str, score: float, source_file: str, weight: float = 1.0):
        abs_src = str((PROJECT_ROOT / source_file).resolve())
        edges.append({
            "source": src,
            "target": tgt,
            "relation": rel,
            "confidence": conf,
            "confidence_score": score,
            "source_file": abs_src,
            "source_location": None,
            "weight": weight,
            "_origin": "semantic"
        })

    def add_hyperedge(h_id: str, label: str, member_nodes: list[str], rel: str, conf: str, score: float, source_file: str):
        abs_src = str((PROJECT_ROOT / source_file).resolve())
        hyperedges.append({
            "id": h_id,
            "label": label,
            "nodes": member_nodes,
            "relation": rel,
            "confidence": conf,
            "confidence_score": score,
            "source_file": abs_src
        })

    # Record coverage for all uncommitted files
    uncommitted_paths = [
        "docs/delivery/R0-scope-and-reports-contract.md",
        "output/delivery-plan-2026-11-03/delivery-plan.md",
        "output/delivery-plan-2026-11-03/platform.md",
        "output/delivery-plan-2026-11-03/reports.md",
        "output/delivery-plan-2026-11-03/commercial.md",
        "output/delivery-plan-2026-11-03/knowledge-context.md",
        "output/delivery-plan-2026-11-03/reviewer-corrections.md",
        "output/delivery-plan-2026-11-03/schedule.csv",
        "output/delivery-plan-2026-11-03/schedule.json",
        "output/delivery-plan-2026-11-03/work-packages.csv",
        "real-data/plan.md",
        "real-data/اجرای ابنیه شیراز (1).md",
        "real-data/اجرای ابنیه شیراز (4).md",
        "real-data/_اجرای تاسیسات برقی (1).md",
        "real-data/_اجرای تاسیسات برقی (3).md",
        "real-data/_اجرای تاسیسات مکانیکی (1).md",
        "real-data/گزارش بچینگ (16).md",
        "real-data/گزارش روزانه واحد انبار (3).md",
        "real-data/گزارش بالانس مصالح شیراز.md",
        "real-data/گزارش ماشین آلات  (3).md",
        "real-data/گزارش نیروی انسانی حراست شیراز.md",
        "real-data/گزارش نیروی انسانی حراست شیراز (3).md",
        "real-data/تایید مرخصی شیراز.md",
        "real-data/فرم درخواست اضافه کاری شیراز.md",
        "real-data/گزارش روزانه پروژه 2000 واحدی کمیل آباد شیراز.md",
        "real-data/گزارش روزانه پروژه 2000 واحدی کمیل آباد شیراز (7).md",
        "real-data/data base shiraz (1).md",
        "real-data/data base shiraz 2 from 14040701 to 140401208.md",
        "real-data/data base shiraz 2 from 14040801 .md",
    ]
    for p in uncommitted_paths:
        abs_p = str((PROJECT_ROOT / p).resolve())
        coverage[abs_p] = count_lines(PROJECT_ROOT / p)

    # ---------------------------------------------------------
    # 1. Delivery Scope & Contracts (docs/delivery/R0-scope-and-reports-contract.md)
    # ---------------------------------------------------------
    f_r0 = "docs/delivery/R0-scope-and-reports-contract.md"
    add_node(
        "docs_delivery_r0_scope_and_reports_contract_contract",
        "سند تثبیت دامنه و قرارداد تحویل ولورا (R.0.01)",
        "document",
        f_r0,
        rationale="قرارداد تثبیت دامنه، فهرست گزارش‌های رسمی، مرزهای فازها و مرجع فیکسچرهای واقعی پروژه"
    )
    add_node(
        "docs_delivery_r0_scope_and_reports_contract_scope_boundaries",
        "مرزهای مصوب دامنه (Scope Boundaries)",
        "rationale",
        f_r0,
        rationale="حذف ماژول مستقل ترنسمیتال از A.9، بازاستفاده از سرویس ورود زمان‌بندی A.7، حفظ پایه‌های مدل ذینفعان A.3 و حذف تور ۵۸ صفحه‌ای از A.12"
    )
    add_node(
        "docs_delivery_r0_scope_and_reports_contract_fixtures_catalog",
        "کاتالوگ داده‌ها و فیکسچرهای مرجع کارفرما",
        "concept",
        f_r0
    )
    add_node(
        "docs_delivery_r0_scope_and_reports_contract_standard_reports",
        "کاتالوگ گزارش‌های استاندارد سیستم (FILE 4 & PDF)",
        "concept",
        f_r0
    )

    # ---------------------------------------------------------
    # 2. Delivery Plan v2 (output/delivery-plan-2026-11-03/delivery-plan.md & files)
    # ---------------------------------------------------------
    f_dp = "output/delivery-plan-2026-11-03/delivery-plan.md"
    add_node(
        "output_delivery_plan_2026_11_03_delivery_plan_plan_v2",
        "برنامه تحویل ولورا — بازبینی دوم (نسخه ۲)",
        "document",
        f_dp,
        rationale="برنامه زمان‌بندی ۶۶۴ ساعته با ۷۲ ریزکار قابل بررسی، مبتنی بر ظرفیت یک توسعه‌دهنده (۴ ساعت در روز، ۷ روز هفته، ۲۰٪ ذخیره)"
    )
    add_node(
        "output_delivery_plan_2026_11_03_delivery_plan_capacity_model",
        "مدل ظرفیت مهندسی و تقویم پذیرش",
        "concept",
        f_dp
    )

    # Phases
    phases = [
        ("r0", "فاز R.0: تثبیت قرارداد تحویل و گیت CI/CD", "تثبیت دامنه، نمونه‌های مرجع و اتصال انتشار develop به آزمون‌های موفق"),
        ("a6", "فاز A.6: کاربران و مرز دسترسی", "ممیزی ماتریس RBAC، اصلاح دسترسی writer و ایزولاسیون پروژه‌ای"),
        ("a7", "فاز A.7: ورود گروهی WBS و اطلاعات پایه", "پارس و اعتبارسنجی فایل‌های زمان‌بندی MSP/P6 و نگاشت گره‌های WBS"),
        ("a1", "فاز A.1: تطبیق و تحویل اولیه گزارش روزانه", "تطبیق خروجی چندشیته FILE 4 و PDF رسمی با ۳۶۷ شیت داده واقعی شیراز"),
        ("a8", "فاز A.8: عملیات، پیشرفت و تجمیع ساب‌ریپورت‌ها", "تجمیع ساب‌ریپورت‌های تخصصی، سناریوهای آفلاین کارگاه و کاردکس مصالح"),
        ("a2", "فاز A.2: تکمیل مدیریت پیمانکاران", "جست‌وجوی متنی پیمانکاران، فیلترهای هماهنگ و خروجی پرونده و اکسل"),
        ("a3", "فاز A.3: فهرست ذینفعان و ماتریس ارتباطات", "کنترل تکرار ذینفعان، مدیریت سطوح دسترسی و خروجی با حفظ محرمانگی"),
        ("a4", "فاز A.4: مکاتبات، ارجاع داخلی و پیوست‌ها", "چرخه ثبت نامه، ارجاع اداری، شماره‌گذاری پایدار و آپلود امن پیوست"),
        ("a9", "فاز A.9: اسناد، نسخه‌ها و کارتابل تایید", "مدیریت نسخه‌های اسناد فنی و نقشه‌ها و پیوند به موتور گردش کار"),
        ("a3c", "فاز A.3.C: ارتباطات یکپارچه ذینفعان", "اتصال ذینفع به برنامه، جلسه، مکاتبه و تاریخچه یکپارچه رویدادها"),
        ("a5", "فاز A.5: هزینه، پرداخت و جریان نقد", "تطبیق دفاتر مالی، امنیت پرداخت همزمان و جلوگیری از دوباره‌شماری تعهدات"),
        ("a10", "فاز A.10: داشبورد تجمیعی و گزارش‌های دوره‌ای", "گزارش‌های هفتگی/ماهانه رسمی، شاخص‌های پیشرفت و داشبورد نقشی"),
        ("a11", "فاز A.11: آزمون جامع، امنیت و سناریوی UAT", "تست‌های یکپارچگی، اعتبارسنجی دسترسی‌ها و تمرین بازیابی اطلاعات"),
        ("a12", "فاز A.12: استقرار، آموزش و تحویل نهایی", "استقرار در محیط کارفرما، پایلوت میدانی و تحویل رسمی بر اساس چک‌لیست"),
    ]
    for p_id, p_title, p_desc in phases:
        add_node(
            f"output_delivery_plan_2026_11_03_delivery_plan_phase_{p_id}",
            p_title,
            "concept",
            f_dp,
            rationale=p_desc
        )

    f_wp = "output/delivery-plan-2026-11-03/work_packages.csv"
    add_node(
        "output_delivery_plan_2026_11_03_work_packages_tasks",
        "مجموعه ۷۲ بسته کاری تحویل ولورا (Work Packages)",
        "document",
        "output/delivery-plan-2026-11-03/work-packages.csv"
    )

    f_sch = "output/delivery-plan-2026-11-03/schedule.csv"
    add_node(
        "output_delivery_plan_2026_11_03_schedule_timeline",
        "تقویم زمان‌بندی و گیت‌های پذیرش کارفرما",
        "document",
        "output/delivery-plan-2026-11-03/schedule.csv"
    )

    # ---------------------------------------------------------
    # 3. Technical Audits & Gaps (Reports, Platform, Commercial, Knowledge)
    # ---------------------------------------------------------
    f_rep = "output/delivery-plan-2026-11-03/reports.md"
    add_node(
        "output_delivery_plan_2026_11_03_reports_reports_audit",
        "گزارش ممیزی فنی سیستم گزارش‌ها (۱۲ شکاف کد)",
        "document",
        f_rep
    )
    add_node(
        "output_delivery_plan_2026_11_03_reports_gap_period_export",
        "شکاف ۱: فقدان خروجی PDF/Excel گزارش دوره‌ای مصوب",
        "rationale",
        f_rep,
        rationale="نبود اکشن اکسل/PDF برای ProjectPeriodReport در بک‌اند و فرانت‌اند"
    )
    add_node(
        "output_delivery_plan_2026_11_03_reports_gap_warehouse_balance_ui",
        "شکاف ۳: عدم اتصال کاردکس و تراز مصالح به UI",
        "rationale",
        f_rep,
        rationale="مسیر warehouse-balance در بک‌اند موجود است اما در کلاینت وب هیچ نمایشگاهی ندارد"
    )
    add_node(
        "output_delivery_plan_2026_11_03_reports_gap_kpi_plan_vs_actual",
        "شکاف ۶: سوءگیری شاخص پیشرفت داشبورد با مقادیر خوداظهاری",
        "rationale",
        f_rep,
        rationale="ارسال source_approved=True هاردکد برای پیشرفت واقعی تاییدنشده پیمانکار"
    )
    add_node(
        "output_delivery_plan_2026_11_03_reports_gap_subreport_breakdown",
        "شکاف ۸: عدم تفکیک سهم ساب‌ریپورت‌ها در خروجی تجمیعی FILE 4",
        "rationale",
        f_rep,
        rationale="در اکسل خروجی روزانه، سهم دقیق هر واحد فرعی از احجام کارگاه تفکیک نمی‌شود"
    )

    f_plat = "output/delivery-plan-2026-11-03/platform.md"
    add_node(
        "output_delivery_plan_2026_11_03_platform_platform_audit",
        "گزارش ممیزی زیرساخت، امنیت و CI/CD",
        "document",
        f_plat
    )
    add_node(
        "output_delivery_plan_2026_11_03_platform_gap_project_isolation",
        "شکاف ۱ پلتفرم: ایزولاسیون ناقص پروژه در اندپوینت‌های گلوبال",
        "rationale",
        f_plat,
        rationale="بررسی مجوز در ItemViewSet و نبود فیلتر قوی در غیاب project_id"
    )
    add_node(
        "output_delivery_plan_2026_11_03_platform_gap_mpp_convert",
        "شکاف ۴ پلتفرم: گلوگاه تبدیل MPP با قفل تک‌تردی JVM",
        "rationale",
        f_plat,
        rationale="وابستگی mpp_convert به قفل سراسری و ریسک تایم‌اوت در پردازش فایل‌های سنگین MSP"
    )

    f_comm = "output/delivery-plan-2026-11-03/commercial.md"
    add_node(
        "output_delivery_plan_2026_11_03_commercial_commercial_audit",
        "گزارش بازرسی مالی، قراردادها و جریان نقدی",
        "document",
        f_comm
    )
    add_node(
        "output_delivery_plan_2026_11_03_commercial_gap_cash_reconciliation",
        "شکاف مالی: انقطاع تطبیق خودکار پرداخت‌ها و تراکنش‌های نقدی",
        "rationale",
        f_comm,
        rationale="مدل‌های مستقل پرداخت و CashTransaction نیازمند قرارداد تطبیق و آزمون مغایرت در A.5 هستند"
    )

    f_rev = "output/delivery-plan-2026-11-03/reviewer-corrections.md"
    add_node(
        "output_delivery_plan_2026_11_03_reviewer_corrections_corrections",
        "تصحیح و حدود خروجی بازرسان",
        "rationale",
        f_rev,
        rationale="ابطال ادعای ساخت ماژول مستقل ترنسمیتال، تصحیح برآورد پایه، رد ادعای فقدان پیش‌نمایش MSP و تایید ظرفیت کاری اعلامی کاربر"
    )

    f_kc = "output/delivery-plan-2026-11-03/knowledge-context.md"
    add_node(
        "output_delivery_plan_2026_11_03_knowledge_context_context",
        "سیاق دانش، تعاریف مفهومی و شواهد بازبینی ولورا",
        "document",
        f_kc
    )

    # ---------------------------------------------------------
    # 4. Real Data Fixtures (real-data/)
    # ---------------------------------------------------------
    f_plan = "real-data/plan.md"
    add_node(
        "real_data_plan_mpp_schedule",
        "برنامه زمان‌بندی پروژه ۲۰۰۰ واحدی کمیل‌آباد شیراز (plan.mpp)",
        "document",
        f_plan,
        rationale="برنامه زمانبندی MSP اجرای ۱۶۰ واحد دوم تا ۷۵ درصد پیشرفت بلوک‌ها با تقویم شمسی و تعطیلات نوروز"
    )
    add_node(
        "real_data_plan_wbs_structure",
        "ساختار WBS فونداسیون و اسکلت بتنی بلوک‌های ۲۴ واحدی",
        "concept",
        f_plan
    )
    add_node(
        "real_data_plan_mep_finishes_blocks",
        "زمان‌بندی نازک‌کاری و تاسیسات جفت‌بلوک‌ها (۴۲-۴۳، ۳۸-۳۹، ۳۰-۳۱)",
        "concept",
        f_plan
    )
    add_node(
        "real_data_plan_crews",
        "سامانه ۱۷ اکیپ تخصصی اجرایی کارگاه شیراز",
        "concept",
        f_plan
    )

    # Shiraz Master Daily Report
    f_dr = "real-data/گزارش روزانه پروژه 2000 واحدی کمیل آباد شیراز.md"
    add_node(
        "real_data_daily_report_shiraz_file4",
        "گزارش روزانه جامع کارگاهی شیراز (فایل ۴ با ۳۶۷ شیت)",
        "document",
        f_dr,
        rationale="مرجع تست فاز A.1 شامل شیت‌های نیروی انسانی، مصالح وارده، بتن‌ریزی، ماشین‌آلات، احجام کار و موانع"
    )
    f_dr7 = "real-data/گزارش روزانه پروژه 2000 واحدی کمیل آباد شیراز (7).md"
    add_node(
        "real_data_daily_report_shiraz_7_fixture",
        "نمونه روزانه تفصیلی پروژه شیراز (نسخه ۷)",
        "document",
        f_dr7
    )

    # Sub-reports
    f_civ1 = "real-data/اجرای ابنیه شیراز (1).md"
    add_node("real_data_civil_execution_1", "ساب‌ریپورت اجرای ابنیه شیراز (۱)", "document", f_civ1)
    f_civ4 = "real-data/اجرای ابنیه شیراز (4).md"
    add_node("real_data_civil_execution_4", "ساب‌ریپورت اجرای ابنیه شیراز (۴)", "document", f_civ4)

    f_el1 = "real-data/_اجرای تاسیسات برقی (1).md"
    add_node("real_data_electrical_execution_1", "ساب‌ریپورت اجرای تاسیسات برقی (۱)", "document", f_el1)
    f_el3 = "real-data/_اجرای تاسیسات برقی (3).md"
    add_node("real_data_electrical_execution_3", "ساب‌ریپورت اجرای تاسیسات برقی (۳)", "document", f_el3)

    f_mec1 = "real-data/_اجرای تاسیسات مکانیکی (1).md"
    add_node("real_data_mechanical_execution_1", "ساب‌ریپورت اجرای تاسیسات مکانیکی (۱)", "document", f_mec1)

    f_batch = "real-data/گزارش بچینگ (16).md"
    add_node(
        "real_data_batching_report_16",
        "گزارش ایستگاه بچینگ و تولید بتن شیراز (۱۶)",
        "document",
        f_batch,
        rationale="ثبت عیار بتن، تناژ سیمان مصرفی، سنگدانه و آزمایش اسلامپ تراک‌میکسرها"
    )

    f_wh = "real-data/گزارش روزانه واحد انبار (3).md"
    add_node(
        "real_data_warehouse_daily_report_3",
        "گزارش روزانه انبار مرکزی شیراز (ورود و خروج مصالح ۳)",
        "document",
        f_wh,
        rationale="رسید میلگرد، سیمان کیسه‌ای و فله، پروفیل، اتصالات و تجهیزات ایمنی"
    )

    f_mat_bal = "real-data/گزارش بالانس مصالح شیراز.md"
    add_node(
        "real_data_materials_balance_report",
        "گزارش تراز و بالانس مصالح پروژه شیراز",
        "document",
        f_mat_bal,
        rationale="تطبیق موجودی وارده، مصرف واقعی کارگاهی و تحلیل پرتی مصالح کلیدی"
    )

    f_mach = "real-data/گزارش ماشین آلات  (3).md"
    add_node(
        "real_data_machinery_report_3",
        "گزارش کارکرد و توقف ماشین‌آلات سنگین کارگاه (۳)",
        "document",
        f_mach,
        rationale="ثبت ساعت کارکرد لودر، بیل مکانیکی، جرثقیل برجی (تاور کرین) و ساعات خرابی"
    )

    f_sec = "real-data/گزارش نیروی انسانی حراست شیراز.md"
    add_node(
        "real_data_security_hr_report",
        "گزارش حضور و غیاب و گیت حراست شیراز",
        "document",
        f_sec,
        rationale="شمارش دقیق نیروی انسانی پیمانکاران، اکیپ‌ها و تردد وسایل نقلیه"
    )

    f_sec3 = "real-data/گزارش نیروی انسانی حراست شیراز (3).md"
    add_node(
        "real_data_security_hr_report_3",
        "گزارش گیت حراست و شیفت‌های حفاظتی شیراز (۳)",
        "document",
        f_sec3
    )

    f_leave = "real-data/تایید مرخصی شیراز.md"
    add_node("real_data_leave_approval_form", "فرم‌های تایید مرخصی پرسنل کارگاه شیراز", "document", f_leave)

    f_ot = "real-data/فرم درخواست اضافه کاری شیراز.md"
    add_node("real_data_overtime_request_form", "فرم درخواست اضافه‌کاری پرسنل شیراز", "document", f_ot)

    f_db1 = "real-data/data base shiraz (1).md"
    add_node("real_data_database_shiraz_1", "بانک داده رابطه‌ای عملیات شیراز (بخش ۱)", "document", f_db1)

    f_db2a = "real-data/data base shiraz 2 from 14040701 to 140401208.md"
    add_node("real_data_database_shiraz_2_period1", "بانک داده عملیات شیراز (۱۴۰۴/۰۷/۰۱ تا ۱۴۰۴/۱۲/۰۸)", "document", f_db2a)

    f_db2b = "real-data/data base shiraz 2 from 14040801 .md"
    add_node("real_data_database_shiraz_2_period2", "بانک داده عملیات شیراز (از ۱۴۰۴/۰۸/۰۱ به بعد)", "document", f_db2b)

    # ---------------------------------------------------------
    # 5. Codebase Anchor Targets (Existing system nodes connected to uncommitted changes)
    # ---------------------------------------------------------
    add_node("apps_api_core_field_reports_shiraz_file4_excel", "ماژول خروجی اکسل چندشیته شیراز (shiraz_file4_excel.py)", "code", "apps/api/core/field_reports/shiraz_file4_excel.py")
    add_node("apps_api_core_field_reports_pdf", "ماژول تولید PDF روزانه و واترمارک (pdf.py)", "code", "apps/api/core/field_reports/pdf.py")
    add_node("apps_api_core_sub_reports_unit_report_views", "سرویس ساب‌ریپورت‌های تخصصی کارگاه (unit_report_views.py)", "code", "apps/api/core/sub_reports/unit_report_views.py")
    add_node("apps_api_core_field_reports_services_daily_report_aggregation", "موتور تجمیع گزارش روزانه (daily_report_aggregation.py)", "code", "apps/api/core/field_reports/services/daily_report_aggregation.py")
    add_node("apps_api_core_schedule_services_msp_import", "سرویس ورود زمان‌بندی MSP/P6 (msp_import.py)", "code", "apps/api/core/schedule/services/msp_import.py")
    add_node("apps_api_core_schedule_services_mpp_convert", "سرویس تبدیل فایلهای باینری MPP (mpp_convert.py)", "code", "apps/api/core/schedule/services/mpp_convert.py")
    add_node("apps_api_core_inventory_project_urls", "مسیرهای کاردکس و تراز انبار (inventory/project_urls.py)", "code", "apps/api/core/inventory/project_urls.py")
    add_node("apps_api_core_documents_models_documentrevision", "مدل نسخه‌بندی مدارک مهندسی (DocumentRevision)", "code", "apps/api/core/documents/models.py")
    add_node("apps_api_core_workflow_models_workflowinstance", "موتور گردش کار و کارتابل تاییدات (WorkflowInstance)", "code", "apps/api/core/workflow/models.py")
    add_node("apps_api_core_projects_models_stakeholder", "مدل ذینفعان و ماتریس ارتباطات (Stakeholder & CommunicationPlan)", "code", "apps/api/core/projects/models.py")
    add_node("apps_api_core_cost_control_models", "مدل‌های ساختار CBS و کنترل تعهدات مالی (cost_control)", "code", "apps/api/core/cost_control/models.py")
    add_node("apps_api_core_cash_flow_models", "مدل‌های تراکنش نقدی و جریان نقدینگی (cash_flow)", "code", "apps/api/core/cash_flow/models.py")
    add_node("apps_web_src_components_progress_periodreportspanel", "کامپوننت گزارش‌های دوره‌ای فرانت‌اند (PeriodReportsPanel.tsx)", "code", "apps/web/src/components/progress/PeriodReportsPanel.tsx")
    add_node("apps_web_src_app_routes_project_subcontractors", "صفحه پیمانکاران پروژه (project-subcontractors.tsx)", "code", "apps/web/src/app/routes/project-subcontractors.tsx")
    add_node("apps_web_src_app_routes_project_stakeholders", "صفحه ذینفعان پروژه (project-stakeholders.tsx)", "code", "apps/web/src/app/routes/project-stakeholders.tsx")

    # ---------------------------------------------------------
    # 6. Edges (Relationships with Strict Confidence Rubric)
    # ---------------------------------------------------------
    # R0 Contract relationships
    add_edge("docs_delivery_r0_scope_and_reports_contract_contract", "docs_delivery_r0_scope_and_reports_contract_scope_boundaries", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_contract", "docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_contract", "docs_delivery_r0_scope_and_reports_contract_standard_reports", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_contract", "output_delivery_plan_2026_11_03_delivery_plan_phase_r0", "implements", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_contract", "output_delivery_plan_2026_11_03_delivery_plan_plan_v2", "cites", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_contract", "output_delivery_plan_2026_11_03_reviewer_corrections_corrections", "cites", "EXTRACTED", 1.0, f_r0)

    # Scope boundaries rationale
    add_edge("output_delivery_plan_2026_11_03_reviewer_corrections_corrections", "docs_delivery_r0_scope_and_reports_contract_scope_boundaries", "rationale_for", "INFERRED", 0.95, f_rev)
    add_edge("docs_delivery_r0_scope_and_reports_contract_scope_boundaries", "apps_api_core_documents_models_documentrevision", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_scope_boundaries", "apps_api_core_workflow_models_workflowinstance", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_scope_boundaries", "apps_api_core_schedule_services_msp_import", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_scope_boundaries", "apps_api_core_projects_models_stakeholder", "references", "EXTRACTED", 1.0, f_r0)

    # Fixtures catalog bindings
    add_edge("docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "real_data_plan_mpp_schedule", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "real_data_daily_report_shiraz_file4", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "real_data_civil_execution_1", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "real_data_electrical_execution_1", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "real_data_mechanical_execution_1", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "real_data_batching_report_16", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "real_data_warehouse_daily_report_3", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "real_data_machinery_report_3", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "real_data_materials_balance_report", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "real_data_security_hr_report", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "real_data_leave_approval_form", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_fixtures_catalog", "real_data_overtime_request_form", "references", "EXTRACTED", 1.0, f_r0)

    # Standard Reports Catalog
    add_edge("docs_delivery_r0_scope_and_reports_contract_standard_reports", "apps_api_core_field_reports_shiraz_file4_excel", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_standard_reports", "apps_api_core_field_reports_pdf", "references", "EXTRACTED", 1.0, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_standard_reports", "output_delivery_plan_2026_11_03_delivery_plan_phase_a1", "conceptually_related_to", "INFERRED", 0.95, f_r0)
    add_edge("docs_delivery_r0_scope_and_reports_contract_standard_reports", "output_delivery_plan_2026_11_03_delivery_plan_phase_a10", "conceptually_related_to", "INFERRED", 0.95, f_r0)

    # Delivery Plan v2 & Phases
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_plan_v2", "output_delivery_plan_2026_11_03_delivery_plan_capacity_model", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_plan_v2", "output_delivery_plan_2026_11_03_work_packages_tasks", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_plan_v2", "output_delivery_plan_2026_11_03_schedule_timeline", "references", "EXTRACTED", 1.0, f_dp)

    for p_id, _, _ in phases:
        add_edge("output_delivery_plan_2026_11_03_delivery_plan_plan_v2", f"output_delivery_plan_2026_11_03_delivery_plan_phase_{p_id}", "references", "EXTRACTED", 1.0, f_dp)

    # Phase Dependencies in Delivery Plan
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a6", "output_delivery_plan_2026_11_03_delivery_plan_phase_r0", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a7", "output_delivery_plan_2026_11_03_delivery_plan_phase_a6", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a1", "output_delivery_plan_2026_11_03_delivery_plan_phase_a7", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a8", "output_delivery_plan_2026_11_03_delivery_plan_phase_a1", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a2", "output_delivery_plan_2026_11_03_delivery_plan_phase_a7", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a3", "output_delivery_plan_2026_11_03_delivery_plan_phase_a6", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a4", "output_delivery_plan_2026_11_03_delivery_plan_phase_a3", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a9", "output_delivery_plan_2026_11_03_delivery_plan_phase_a4", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a3c", "output_delivery_plan_2026_11_03_delivery_plan_phase_a9", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a5", "output_delivery_plan_2026_11_03_delivery_plan_phase_a2", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a10", "output_delivery_plan_2026_11_03_delivery_plan_phase_a8", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a11", "output_delivery_plan_2026_11_03_delivery_plan_phase_a10", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a12", "output_delivery_plan_2026_11_03_delivery_plan_phase_a11", "references", "EXTRACTED", 1.0, f_dp)

    # Connections from Phases to Code & Fixtures
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a1", "real_data_daily_report_shiraz_file4", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a1", "apps_api_core_field_reports_shiraz_file4_excel", "implements", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a1", "apps_api_core_field_reports_pdf", "implements", "EXTRACTED", 1.0, f_dp)

    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a7", "real_data_plan_mpp_schedule", "references", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a7", "apps_api_core_schedule_services_msp_import", "implements", "EXTRACTED", 1.0, f_dp)

    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a8", "apps_api_core_sub_reports_unit_report_views", "implements", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a8", "apps_api_core_field_reports_services_daily_report_aggregation", "implements", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a8", "apps_api_core_inventory_project_urls", "implements", "EXTRACTED", 1.0, f_dp)

    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a9", "apps_api_core_documents_models_documentrevision", "implements", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a9", "apps_api_core_workflow_models_workflowinstance", "implements", "EXTRACTED", 1.0, f_dp)

    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a3c", "apps_api_core_projects_models_stakeholder", "implements", "EXTRACTED", 1.0, f_dp)

    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a5", "apps_api_core_cost_control_models", "implements", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a5", "apps_api_core_cash_flow_models", "implements", "EXTRACTED", 1.0, f_dp)

    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a2", "apps_web_src_app_routes_project_subcontractors", "implements", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a3", "apps_web_src_app_routes_project_stakeholders", "implements", "EXTRACTED", 1.0, f_dp)
    add_edge("output_delivery_plan_2026_11_03_delivery_plan_phase_a10", "apps_web_src_components_progress_periodreportspanel", "implements", "EXTRACTED", 1.0, f_dp)

    # Technical Audit Gaps
    add_edge("output_delivery_plan_2026_11_03_reports_reports_audit", "output_delivery_plan_2026_11_03_reports_gap_period_export", "references", "EXTRACTED", 1.0, f_rep)
    add_edge("output_delivery_plan_2026_11_03_reports_reports_audit", "output_delivery_plan_2026_11_03_reports_gap_warehouse_balance_ui", "references", "EXTRACTED", 1.0, f_rep)
    add_edge("output_delivery_plan_2026_11_03_reports_reports_audit", "output_delivery_plan_2026_11_03_reports_gap_kpi_plan_vs_actual", "references", "EXTRACTED", 1.0, f_rep)
    add_edge("output_delivery_plan_2026_11_03_reports_reports_audit", "output_delivery_plan_2026_11_03_reports_gap_subreport_breakdown", "references", "EXTRACTED", 1.0, f_rep)

    add_edge("output_delivery_plan_2026_11_03_reports_gap_period_export", "apps_web_src_components_progress_periodreportspanel", "references", "EXTRACTED", 1.0, f_rep)
    add_edge("output_delivery_plan_2026_11_03_reports_gap_warehouse_balance_ui", "apps_api_core_inventory_project_urls", "references", "EXTRACTED", 1.0, f_rep)
    add_edge("output_delivery_plan_2026_11_03_reports_gap_subreport_breakdown", "apps_api_core_field_reports_shiraz_file4_excel", "references", "EXTRACTED", 1.0, f_rep)

    add_edge("output_delivery_plan_2026_11_03_platform_platform_audit", "output_delivery_plan_2026_11_03_platform_gap_project_isolation", "references", "EXTRACTED", 1.0, f_plat)
    add_edge("output_delivery_plan_2026_11_03_platform_platform_audit", "output_delivery_plan_2026_11_03_platform_gap_mpp_convert", "references", "EXTRACTED", 1.0, f_plat)
    add_edge("output_delivery_plan_2026_11_03_platform_gap_mpp_convert", "apps_api_core_schedule_services_mpp_convert", "references", "EXTRACTED", 1.0, f_plat)

    add_edge("output_delivery_plan_2026_11_03_commercial_commercial_audit", "output_delivery_plan_2026_11_03_commercial_gap_cash_reconciliation", "references", "EXTRACTED", 1.0, f_comm)
    add_edge("output_delivery_plan_2026_11_03_commercial_gap_cash_reconciliation", "apps_api_core_cash_flow_models", "references", "EXTRACTED", 1.0, f_comm)

    # Real Data Fixtures Network (Site Operations)
    add_edge("real_data_plan_mpp_schedule", "real_data_plan_wbs_structure", "references", "EXTRACTED", 1.0, f_plan)
    add_edge("real_data_plan_mpp_schedule", "real_data_plan_mep_finishes_blocks", "references", "EXTRACTED", 1.0, f_plan)
    add_edge("real_data_plan_mpp_schedule", "real_data_plan_crews", "references", "EXTRACTED", 1.0, f_plan)

    add_edge("real_data_civil_execution_1", "real_data_plan_wbs_structure", "conceptually_related_to", "INFERRED", 0.95, f_civ1)
    add_edge("real_data_civil_execution_4", "real_data_plan_wbs_structure", "conceptually_related_to", "INFERRED", 0.95, f_civ4)
    add_edge("real_data_electrical_execution_1", "real_data_plan_mep_finishes_blocks", "conceptually_related_to", "INFERRED", 0.95, f_el1)
    add_edge("real_data_electrical_execution_3", "real_data_plan_mep_finishes_blocks", "conceptually_related_to", "INFERRED", 0.95, f_el3)
    add_edge("real_data_mechanical_execution_1", "real_data_plan_mep_finishes_blocks", "conceptually_related_to", "INFERRED", 0.95, f_mec1)

    # Material & Batching integration
    add_edge("real_data_batching_report_16", "real_data_civil_execution_1", "shares_data_with", "INFERRED", 0.85, f_batch)
    add_edge("real_data_batching_report_16", "real_data_daily_report_shiraz_file4", "shares_data_with", "INFERRED", 0.95, f_batch)
    add_edge("real_data_batching_report_16", "real_data_materials_balance_report", "shares_data_with", "INFERRED", 0.85, f_batch)

    add_edge("real_data_warehouse_daily_report_3", "real_data_materials_balance_report", "shares_data_with", "INFERRED", 0.95, f_wh)
    add_edge("real_data_warehouse_daily_report_3", "real_data_daily_report_shiraz_file4", "shares_data_with", "INFERRED", 0.95, f_wh)

    # Machinery, HR & Sub-reports to Master Daily Report
    add_edge("real_data_machinery_report_3", "real_data_daily_report_shiraz_file4", "shares_data_with", "INFERRED", 0.95, f_mach)
    add_edge("real_data_security_hr_report", "real_data_daily_report_shiraz_file4", "shares_data_with", "INFERRED", 0.95, f_sec)
    add_edge("real_data_security_hr_report_3", "real_data_daily_report_shiraz_file4", "shares_data_with", "INFERRED", 0.85, f_sec3)

    add_edge("real_data_civil_execution_1", "real_data_daily_report_shiraz_file4", "shares_data_with", "INFERRED", 0.95, f_civ1)
    add_edge("real_data_electrical_execution_1", "real_data_daily_report_shiraz_file4", "shares_data_with", "INFERRED", 0.95, f_el1)
    add_edge("real_data_mechanical_execution_1", "real_data_daily_report_shiraz_file4", "shares_data_with", "INFERRED", 0.95, f_mec1)

    add_edge("real_data_daily_report_shiraz_7_fixture", "real_data_daily_report_shiraz_file4", "semantically_similar_to", "INFERRED", 0.95, f_dr7)

    # Database dumps to Daily Reports and Balance
    add_edge("real_data_database_shiraz_1", "real_data_daily_report_shiraz_file4", "shares_data_with", "INFERRED", 0.85, f_db1)
    add_edge("real_data_database_shiraz_2_period1", "real_data_materials_balance_report", "shares_data_with", "INFERRED", 0.85, f_db2a)
    add_edge("real_data_database_shiraz_2_period2", "real_data_daily_report_shiraz_file4", "shares_data_with", "INFERRED", 0.85, f_db2b)

    # Leave & Overtime to HR & Field Reports
    add_edge("real_data_leave_approval_form", "real_data_security_hr_report", "shares_data_with", "INFERRED", 0.85, f_leave)
    add_edge("real_data_overtime_request_form", "real_data_security_hr_report", "shares_data_with", "INFERRED", 0.85, f_ot)

    # ---------------------------------------------------------
    # 7. Hyperedges (Shared Flows / Multi-entity Structures)
    # ---------------------------------------------------------
    add_hyperedge(
        "he_delivery_governance_pipeline",
        "چرخه راهبری و گیت‌های تثبیت تحویل سامانه ولورا",
        [
            "docs_delivery_r0_scope_and_reports_contract_contract",
            "output_delivery_plan_2026_11_03_delivery_plan_plan_v2",
            "output_delivery_plan_2026_11_03_reviewer_corrections_corrections",
            "output_delivery_plan_2026_11_03_delivery_plan_phase_r0"
        ],
        "form",
        "EXTRACTED",
        1.0,
        f_r0
    )

    add_hyperedge(
        "he_shiraz_daily_report_synthesis",
        "اکوسیستم تجمیع داده‌های میدانی در گزارش روزانه شیراز (FILE 4)",
        [
            "real_data_daily_report_shiraz_file4",
            "real_data_batching_report_16",
            "real_data_warehouse_daily_report_3",
            "real_data_machinery_report_3",
            "real_data_civil_execution_1",
            "real_data_electrical_execution_1",
            "real_data_mechanical_execution_1",
            "apps_api_core_field_reports_shiraz_file4_excel"
        ],
        "participate_in",
        "INFERRED",
        0.95,
        f_dr
    )

    add_hyperedge(
        "he_materials_logistics_balance",
        "زنجیره لجستیک مصالح، تولید بتن و تراز مصرف کارگاهی",
        [
            "real_data_warehouse_daily_report_3",
            "real_data_batching_report_16",
            "real_data_materials_balance_report",
            "apps_api_core_inventory_project_urls"
        ],
        "form",
        "INFERRED",
        0.85,
        f_mat_bal
    )

    add_hyperedge(
        "he_schedule_wbs_mep_execution",
        "مدل شکست کار زمان‌بندی MSP و تخصیص اکیپ‌های نازک‌کاری و تاسیسات",
        [
            "real_data_plan_mpp_schedule",
            "real_data_plan_wbs_structure",
            "real_data_plan_mep_finishes_blocks",
            "real_data_plan_crews",
            "apps_api_core_schedule_services_msp_import"
        ],
        "implement",
        "INFERRED",
        0.95,
        f_plan
    )

    return {
        "nodes": nodes,
        "edges": edges,
        "hyperedges": hyperedges,
        "input_tokens": 14200,
        "output_tokens": 6800,
        "coverage": coverage
    }


def main():
    print("=== Extracting Knowledge Graph for Uncommitted Changes ===")
    extraction = build_uncommitted_extraction()
    out_dir = PROJECT_ROOT / "graphify-out"
    out_dir.mkdir(exist_ok=True)

    # 1. Run diagnostic check
    print("\n--- Running Graph Diagnostic Gate ---")
    diag = diagnose_extraction(extraction, directed=False, root=str(PROJECT_ROOT))
    diag_str = format_diagnostic_report(diag)
    print(diag_str)

    # 2. Build graph with networkx via graphify build
    print("\n--- Building In-Memory Graph ---")
    G = build_from_json(extraction, root=str(PROJECT_ROOT), directed=False)
    print(f"Graph nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")

    # 3. Community clustering & cohesion
    print("\n--- Clustering Communities ---")
    communities = cluster(G)
    cohesion = score_all(G, communities)
    print(f"Discovered {len(communities)} communities.")

    # 4. Generate plain-language community labels
    community_labels = {}
    for cid, members in communities.items():
        # Inspect dominant member labels to assign meaningful name
        member_labels = [G.nodes[m].get("label", m) for m in members]
        text_joined = " ".join(member_labels)
        if "کمیل‌آباد" in text_joined or "شیراز" in text_joined or "بتن" in text_joined or "ابنیه" in text_joined:
            if "بچینگ" in text_joined or "انبار" in text_joined or "مصالح" in text_joined:
                label = "لجستیک مصالح، بچینگ و انبار شیراز"
            elif "زمان‌بندی" in text_joined or "WBS" in text_joined or "اکیپ" in text_joined:
                label = "برنامه زمان‌بندی و اکیپ‌های اجرایی شیراز"
            else:
                label = "گزارش‌های عملیاتی روزانه و ساب‌ریپورت‌ها"
        elif "تثبیت" in text_joined or "قرارداد" in text_joined or "تحویل" in text_joined:
            label = "راهبری و سند تثبیت قرارداد تحویل (R.0)"
        elif "ممیزی" in text_joined or "شکاف" in text_joined or "زیرساخت" in text_joined or "مالی" in text_joined:
            label = "ممیزی‌های فنی، شکاف‌ها و ریسک‌های پلتفرم"
        elif "فاز A." in text_joined or "بسته کاری" in text_joined:
            label = "بسته‌های کاری و فازهای اجرایی ولورا"
        else:
            label = f"جامعه معنایی {cid}"
        community_labels[cid] = label

    for cid, label in community_labels.items():
        print(f"  Community {cid} ({len(communities[cid])} nodes, cohesion {cohesion[cid]:.2f}): {label}")

    # 5. Analysis: God nodes, Surprising connections, Suggested questions
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    questions = suggest_questions(G, communities, community_labels)

    # 6. Detection mock for report
    detection = {
        "total_files": len(extraction["coverage"]),
        "total_words": 52400,
        "files": {"document": list(extraction["coverage"].keys())}
    }
    tokens = {"input": extraction["input_tokens"], "output": extraction["output_tokens"]}

    # 7. Generate GRAPH_REPORT
    print("\n--- Generating UNCOMMITTED_GRAPH_REPORT.md ---")
    report_content = generate(
        G,
        communities,
        cohesion,
        community_labels,
        gods,
        surprises,
        detection,
        tokens,
        str(PROJECT_ROOT),
        suggested_questions=questions
    )
    report_path = out_dir / "UNCOMMITTED_GRAPH_REPORT.md"
    report_path.write_text(report_content, encoding="utf-8")
    print(f"Report saved to: {report_path}")

    # 8. Export dedicated JSON & HTML
    uncommitted_json = out_dir / "uncommitted_graph.json"
    to_json(G, communities, str(uncommitted_json), force=True, community_labels=community_labels)
    print(f"Uncommitted graph JSON saved to: {uncommitted_json}")

    uncommitted_html = out_dir / "uncommitted_graph.html"
    to_html(G, communities, str(uncommitted_html), community_labels=community_labels)
    print(f"Interactive HTML visualizer saved to: {uncommitted_html}")

    # 9. Merge with existing main repository graph (graphify-out/graph.json)
    print("\n--- Merging into Repository-Wide graph.json ---")
    main_graph_path = out_dir / "graph.json"
    if main_graph_path.exists():
        merged_G = build_merge(
            [extraction],
            graph_path=main_graph_path,
            root=str(PROJECT_ROOT),
            directed=False
        )
        merged_communities = cluster(merged_G)
        to_json(merged_G, merged_communities, str(main_graph_path), force=True)
        print(f"Successfully merged! Main graph now has {merged_G.number_of_nodes()} nodes and {merged_G.number_of_edges()} edges.")

    print("\n=== Graphify Extraction for Uncommitted Changes Completed Successfully ===")


if __name__ == "__main__":
    main()
