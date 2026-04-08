# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    stage_done_percent = fields.Integer(
        string=_("Done % when task is completed (this stage)"),
        help=_(
            "If set, when a task is in state Done (Hoàn tất) and belongs to this stage/column, "
            "Done %% (Gantt / percent_done) is set to this value (0–100). "
            "Leave empty to not set Done %% automatically from this stage."
        ),
    )

    @api.constrains("stage_done_percent")
    def _check_stage_done_percent(self):
        for stage in self:
            if stage.stage_done_percent is False:
                continue
            if not (0 <= stage.stage_done_percent <= 100):
                raise ValidationError(
                    _("Done %% when entering this stage must be between 0 and 100.")
                )
