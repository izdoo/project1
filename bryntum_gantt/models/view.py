# -*- coding: utf-8 -*-
from odoo import models, fields

def _get_field_selection():
    return fields.Selection(
        selection_add=[('BryntumGantt', "Bryntum Gantt")],
        default='BryntumGantt',
        ondelete={'BryntumGantt': 'set default'},
    )


class View(models.Model):
    _inherit = 'ir.ui.view'
    type = _get_field_selection()

    def _get_view_info(self):
        # Odoo 19: session.view_info / views registry only allows types declared here
        return {
            'BryntumGantt': {'icon': 'fa fa-th-list', 'multi_record': True},
        } | super()._get_view_info()


class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'
    view_mode = _get_field_selection()
