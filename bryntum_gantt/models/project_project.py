# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.misc import format_date
import dateutil.parser
from ..tools.odoo_utils import is_enterprise

class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_start_date = fields.Datetime(string="Project Start Date",
                                         default=datetime.today())

    bryntum_auto_scheduling = fields.Boolean('Auto scheduling', default=False)
    bryntum_user_assignment = fields.Boolean('User assignment', default=False)

    def get_default_calendar(self):
            return [
                {
                    "id": "general",
                    "name": "General",
                    "intervals": [],
                    "expanded": True,
                    "children": [
                        {
                            "id": "business",
                            "name": "Business",
                            "intervals": [
                                {
                                    "recurrentStartDate": "every weekday at 12:00",
                                    "recurrentEndDate": "every weekday at 13:00",
                                    "isWorking": False
                                },
                                {
                                    "recurrentStartDate": "every weekday at 17:00",
                                    "recurrentEndDate": "every weekday at 08:00",
                                    "isWorking": False
                                }
                            ]
                        },
                        {
                            "id": "night",
                            "name": "Night shift",
                            "intervals": [
                                {
                                    "recurrentStartDate": "every weekday at 6:00",
                                    "recurrentEndDate": "every weekday at 22:00",
                                    "isWorking": False
                                }
                            ]
                        }
                    ]
                }
            ]

    @api.model
    def get_bryntum_values(self):
        su = self.env['ir.config_parameter'].sudo()

        res = {
            "bryntum_auto_scheduling": su.get_param('bryntum.auto_scheduling'),
            "bryntum_user_assignment": su.get_param('bryntum.user_assignment'),
            "bryntum_gantt_config": su.get_param('bryntum.gantt_config') or '{}'
        }
        return res
