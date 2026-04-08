# -*- coding: utf-8 -*-

from odoo import api, models


class ReportProjectPeriodReport(models.AbstractModel):
    _name = "report.project_period_report.period_report_document"
    _description = "Project Period Report PDF"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["project.period.report"].browse(docids)
        return {
            "doc_ids": docids,
            "doc_model": "project.period.report",
            "docs": docs,
        }
