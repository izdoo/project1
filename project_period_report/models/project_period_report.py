# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectPeriodReport(models.Model):
    _name = "project.period.report"
    _description = "Project Period Report (Weekly / Monthly)"
    _order = "date_from desc, id desc"

    name = fields.Char(
        compute="_compute_name",
        store=True,
        readonly=False,
    )
    project_id = fields.Many2one(
        "project.project",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="project_id.company_id",
        store=True,
    )
    period_type = fields.Selection(
        [
            ("week", "Week"),
            ("month", "Month"),
        ],
        required=True,
        default="week",
    )
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    reporter_id = fields.Many2one(
        "res.users",
        string="Reporter",
        default=lambda self: self.env.user,
        required=True,
    )
    other_notes = fields.Html()
    weekly_completion_percent = fields.Float(string="% completion")
    weekly_bug_count = fields.Integer(string="Bug count")
    weekly_task_count = fields.Integer(string="Task count")
    weekly_man_day = fields.Float(string="Man-day")

    achievement_ids = fields.One2many(
        "project.period.report.achievement",
        "report_id",
        string="Achievements (this period)",
    )
    achievement_completed_ids = fields.One2many(
        "project.period.report.achievement",
        "report_id",
        string="Completed tasks",
        domain=[("line_type", "=", "completed")],
    )
    achievement_in_progress_ids = fields.One2many(
        "project.period.report.achievement",
        "report_id",
        string="In progress tasks",
        domain=[("line_type", "=", "in_progress")],
    )
    achievement_injected_ids = fields.One2many(
        "project.period.report.achievement",
        "report_id",
        string="Injected tasks",
        domain=[("line_type", "=", "injected")],
    )
    plan_next_ids = fields.One2many(
        "project.period.report.plan.line",
        "report_id",
        string="Next period plan",
    )
    progress_ids = fields.One2many(
        "project.period.report.progress",
        "report_id",
        string="Progress by area",
    )
    issue_ids = fields.One2many(
        "project.period.report.issue",
        "report_id",
        string="Issues",
    )
    risk_ids = fields.One2many(
        "project.period.report.risk",
        "report_id",
        string="Risks",
    )

    @api.depends("project_id", "period_type", "date_from", "date_to")
    def _compute_name(self):
        for rec in self:
            if rec.project_id and rec.date_from and rec.date_to:
                ptype = _("Week") if rec.period_type == "week" else _("Month")
                rec.name = "%s — %s (%s → %s)" % (
                    rec.project_id.name,
                    ptype,
                    rec.date_from,
                    rec.date_to,
                )
            else:
                rec.name = _("New Period Report")

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError(_("End date must be on or after start date."))

    def action_print_pdf(self):
        self.ensure_one()
        return self.env.ref(
            "project_period_report.action_report_project_period_report"
        ).report_action(self)

    def action_load_tasks_from_period(self):
        """Fill completed-task lines from tasks closed (fold stage) in this period."""
        self.ensure_one()
        Task = self.env["project.task"]
        Achievement = self.env["project.period.report.achievement"]
        if not self.project_id or not self.date_from or not self.date_to:
            return
        start_dt = fields.Datetime.to_datetime(self.date_from)
        end_exclusive = fields.Datetime.to_datetime(self.date_to) + timedelta(days=1)

        domain = [
            ("project_id", "=", self.project_id.id),
            ("stage_id.fold", "=", True),
            ("write_date", ">=", start_dt),
            ("write_date", "<", end_exclusive),
        ]
        tasks = Task.search(domain, order="sequence, id")
        self.achievement_ids.filtered(lambda l: l.line_type == "completed").unlink()
        for seq, task in enumerate(tasks, start=1):
            Achievement.create(
                {
                    "report_id": self.id,
                    "line_type": "completed",
                    "sequence": seq,
                    "task_id": task.id,
                    "name": task.name,
                }
            )
        return {
            "type": "ir.actions.act_window",
            "res_model": "project.period.report",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_load_next_period_plan(self):
        """Auto-fill next period plan from carry-over tasks + upcoming deadlines."""
        self.ensure_one()
        Task = self.env["project.task"]
        PlanLine = self.env["project.period.report.plan.line"]
        if not self.project_id or not self.date_from or not self.date_to:
            return

        # Source 1: unfinished tasks from previous period report (carry-over).
        previous_report = self.search(
            [
                ("project_id", "=", self.project_id.id),
                ("id", "!=", self.id),
                ("date_to", "<", self.date_from),
            ],
            order="date_to desc, id desc",
            limit=1,
        )
        carry_over_tasks = previous_report.achievement_in_progress_ids.mapped("task_id")
        carry_over_tasks = carry_over_tasks.filtered(lambda t: t and not t.stage_id.fold)

        # Source 2: tasks with deadline in next 7 days after current period.
        next_week_start = fields.Date.to_date(self.date_to) + timedelta(days=1)
        next_week_end = fields.Date.to_date(self.date_to) + timedelta(days=7)
        deadline_tasks = Task.search(
            [
                ("project_id", "=", self.project_id.id),
                ("stage_id.fold", "=", False),
                ("date_deadline", ">=", next_week_start),
                ("date_deadline", "<=", next_week_end),
            ],
            order="date_deadline asc, sequence, id",
        )

        # Replace current auto plan with a fresh list.
        self.plan_next_ids.unlink()
        seq = 1
        used_task_ids = set()

        for task in carry_over_tasks:
            if task.id in used_task_ids:
                continue
            used_task_ids.add(task.id)
            PlanLine.create(
                {
                    "report_id": self.id,
                    "sequence": seq,
                    "task_id": task.id,
                    "source_type": "carry_over",
                    "name": _("[Carry-over] %s") % task.name,
                }
            )
            seq += 1

        for task in deadline_tasks:
            if task.id in used_task_ids:
                continue
            used_task_ids.add(task.id)
            PlanLine.create(
                {
                    "report_id": self.id,
                    "sequence": seq,
                    "task_id": task.id,
                    "source_type": "due_next_week",
                    "name": _("[Due next week] %s") % task.name,
                }
            )
            seq += 1

        return {
            "type": "ir.actions.act_window",
            "res_model": "project.period.report",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }


class ProjectPeriodReportAchievement(models.Model):
    _name = "project.period.report.achievement"
    _description = "Period Report Achievement Line"
    _order = "sequence, id"

    report_id = fields.Many2one(
        "project.period.report",
        required=True,
        ondelete="cascade",
    )
    line_type = fields.Selection(
        [
            ("completed", "Task hoàn thành"),
            ("in_progress", "Task đang thực hiện"),
            ("injected", "Task bị chen thêm"),
        ],
        default="completed",
        required=True,
    )
    sequence = fields.Integer(default=10)
    task_id = fields.Many2one("project.task", ondelete="set null")
    name = fields.Text(required=True)


class ProjectPeriodReportPlanLine(models.Model):
    _name = "project.period.report.plan.line"
    _description = "Period Report Next Plan Line"
    _order = "sequence, id"

    report_id = fields.Many2one(
        "project.period.report",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    task_id = fields.Many2one("project.task", ondelete="set null")
    source_type = fields.Selection(
        [
            ("carry_over", "Carry-over from previous week"),
            ("due_next_week", "Due next week"),
            ("manual", "Manual"),
        ],
        default="manual",
        required=True,
    )
    name = fields.Text(required=True)


class ProjectPeriodReportProgress(models.Model):
    _name = "project.period.report.progress"
    _description = "Period Report Progress Line"
    _order = "sequence, id"

    report_id = fields.Many2one(
        "project.period.report",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    plan_percent = fields.Float(string="Plan %")
    actual_percent = fields.Float(string="Actual %")
    status = fields.Selection(
        [
            ("on_track", "On track"),
            ("delay", "Delay"),
            ("risk", "Risk"),
        ],
        default="on_track",
        required=True,
    )


class ProjectPeriodReportIssue(models.Model):
    _name = "project.period.report.issue"
    _description = "Period Report Issue Line"
    _order = "sequence, id"

    report_id = fields.Many2one(
        "project.period.report",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    problem = fields.Text(required=True)
    cause = fields.Text()
    impact = fields.Text()
    action_note = fields.Text(string="Action / Countermeasure")


class ProjectPeriodReportRisk(models.Model):
    _name = "project.period.report.risk"
    _description = "Period Report Risk Line"
    _order = "sequence, id"

    report_id = fields.Many2one(
        "project.period.report",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    name = fields.Text(required=True)
