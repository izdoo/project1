# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from json import dumps

class BryntumSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bryntum_auto_scheduling = fields.Boolean('Auto scheduling', default=False)
    bryntum_user_assignment = fields.Boolean('User assignment', default=False)
    bryntum_gantt_config = fields.Text('Gantt configuration object', default='{}')
    bryntum_calendar_config = fields.Text('Calendar configuration object', default='{}')

    def set_values(self):
        res = super(BryntumSettings, self).set_values()
        projects = self.env["project.project"].search([])
        self.env['ir.config_parameter'].set_param('bryntum.auto_scheduling', self.bryntum_auto_scheduling)
        projects['bryntum_auto_scheduling'] = self.bryntum_auto_scheduling
        self.env['ir.config_parameter'].set_param('bryntum.user_assignment', self.bryntum_user_assignment)
        projects['bryntum_user_assignment'] = self.bryntum_user_assignment
        self.env['ir.config_parameter'].set_param('bryntum.gantt_config', self.bryntum_gantt_config)
        self.env['ir.config_parameter'].set_param('bryntum.calendar_config', self.bryntum_calendar_config)
        return res

    @api.model
    def get_values(self):
        res = super(BryntumSettings, self).get_values()
        su = self.env['ir.config_parameter'].sudo()

        projects = self.env["project.project"].search([])

        res.update(
            bryntum_auto_scheduling=su.get_param('bryntum.auto_scheduling'),
            bryntum_user_assignment=su.get_param('bryntum.user_assignment'),
            bryntum_gantt_config=su.get_param('bryntum.gantt_config') or '{}',
            bryntum_calendar_config=su.get_param('bryntum.calendar_config') or dumps(projects.get_default_calendar())
        )
        return res
