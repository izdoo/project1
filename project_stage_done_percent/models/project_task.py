# -*- coding: utf-8 -*-
from odoo import api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    # Odoo core: "Hoàn tất" / Done in task state dropdown (see project.project_task CLOSED_STATES).
    _DONE_STATE = "1_done"

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        for task, vals in zip(tasks, vals_list):
            if "percent_done" in vals:
                continue
            if task.state == self._DONE_STATE:
                task._sync_percent_done_from_stage_when_done()
        return tasks

    def write(self, vals):
        res = super().write(vals)
        if "percent_done" in vals:
            return res
        if "state" not in vals and "stage_id" not in vals:
            return res
        for task in self:
            if task.state == self._DONE_STATE:
                task._sync_percent_done_from_stage_when_done()
        return res

    def _sync_percent_done_from_stage_when_done(self):
        """Set Gantt percent_done from stage only when task state is Done (Hoàn tất)."""
        self.ensure_one()
        if self.state != self._DONE_STATE:
            return
        if not self.stage_id:
            return
        pct = self.stage_id.stage_done_percent
        if pct is False:
            return
        target = int(pct)
        if self.percent_done != target:
            self.write({"percent_done": target})
