# -*- coding: utf-8 -*-

from odoo import _, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    period_report_ids = fields.One2many(
        "project.period.report",
        "project_id",
        string="Period Reports",
    )
    period_report_count = fields.Integer(
        compute="_compute_period_report_count",
    )

    def _compute_period_report_count(self):
        for project in self:
            project.period_report_count = len(project.period_report_ids)

    def action_open_period_reports(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Period Reports"),
            "res_model": "project.period.report",
            "view_mode": "list,form",
            "domain": [("project_id", "=", self.id)],
            "context": {"default_project_id": self.id},
        }
