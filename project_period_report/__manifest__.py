# -*- coding: utf-8 -*-
{
    "name": "Project Period Report (Weekly / Monthly)",
    "version": "19.0.1.0.0",
    "category": "Project",
    "summary": "Structured weekly/monthly project reports with PDF export (i18n: en, vi, ja).",
    "description": """
        Báo cáo tuần / tháng theo dự án: thực tích, kế hoạch, tiến độ, issue (問題/原因/影響), action, risk.
        Ngôn ngữ hiển thị và PDF theo ngôn ngữ người dùng.
    """,
    "author": "OdooENV",
    "license": "LGPL-3",
    "price": 15.0,
    "currency": "USD",
    "depends": ["project", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_period_report_views.xml",
        "views/project_project_views.xml",
        "views/project_menus.xml",
        "report/project_period_report_report.xml",
        "report/project_period_report_templates.xml",
    ],
    "installable": True,
    "application": False,
}
