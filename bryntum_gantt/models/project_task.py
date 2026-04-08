# -*- coding: utf-8 -*-
from datetime import datetime
import logging
from odoo import models, fields, api
from odoo.tools.misc import format_date
import dateutil.parser
from ..tools.odoo_utils import is_enterprise

_logger = logging.getLogger(__name__)

if not is_enterprise():
    class Task(models.Model):
        _inherit = "project.task"

        planned_date_begin = fields.Datetime("Start date")
        planned_date_begin_formatted = fields.Char(compute='_compute_planned_date_begin')
        planned_date_end = fields.Datetime("End date")

        _sql_constraints = [
            ('planned_dates_check', "CHECK ((planned_date_begin <= planned_date_end))",
             "The planned start date must be prior to the planned end date."),
        ]

        @api.depends('planned_date_begin')
        def _compute_planned_date_begin(self):
            for task in self:
                task.planned_date_begin_formatted = format_date(self.env,
                                                                task.planned_date_begin) if task.planned_date_begin else None
else:
    class Task(models.Model):
        _inherit = "project.task"

        def _get_recurrence_start_date(self):
            return fields.Date.today()


def check_gantt_date(value):
    if isinstance(value, str):
        return dateutil.parser.parse(value, ignoretz=True)
    else:
        return value


class ProjectTask(models.Model):
    _inherit = 'project.task'

    duration = fields.Integer(string="Duration (days)", default=-1)
    duration_unit = fields.Char(string="Duration Unit", default='d')

    percent_done = fields.Integer(string="Done %", default=0)
    parent_index = fields.Integer(string="Parent Index", default=0)

    assigned_ids = fields.Many2many('res.users', relation='assigned_resources', string="Assigned resources")
    assigned_resources = fields.One2many('project.task.assignment',
                                         inverse_name='task',
                                         string='Assignments')
    employee_ids = fields.Many2many("hr.employee", string="Assignees")
    baselines = fields.One2many('project.task.baseline',
                                inverse_name='task',
                                string='Baselines')

    segments = fields.One2many('project.task.segment',
                               inverse_name='task',
                               string='Segments')

    effort = fields.Integer(string="Effort (hours)", default=0)

    gantt_calendar_flex = fields.Char(string="Gantt Calendar Ids")
    linked_ids = fields.One2many('project.task.linked',
                                 inverse_name='to_id',
                                 string='Linked')
    scheduling_mode = fields.Selection([
        ('Normal', 'Normal'),
        ('FixedDuration', 'Fixed Duration'),
        ('FixedEffort', 'Fixed Effort'),
        ('FixedUnits', 'Fixed Units')
    ], string='Scheduling Mode')
    constraint_type = fields.Selection([
        ('assoonaspossible', 'As soon as possible'),
        ('aslateaspossible', 'As late as possible'),
        ('muststarton', 'Must start on'),
        ('mustfinishon', 'Must finish on'),
        ('startnoearlierthan', 'Start no earlier than'),
        ('startnolaterthan', 'Start no later than'),
        ('finishnoearlierthan', 'Finish no earlier than'),
        ('finishnolaterthan', 'Finish no later than')
    ], string='Constraint Type')
    constraint_date = fields.Datetime(string="Constraint Date")
    effort_driven = fields.Boolean(string="Effort Driven", default=False)
    manually_scheduled = fields.Boolean(string="Manually Scheduled", default=False)
    bryntum_rollup = fields.Boolean(string="Rollup", default=False)
    wbs_value = fields.Char(string="WBS Value")

    def _users_to_employees(self, users):
        if not users:
            return self.env["hr.employee"]
        if "employee_id" in users._fields:
            return users.mapped("employee_id")
        if "employee_ids" in users._fields:
            return users.mapped("employee_ids")
        return self.env["hr.employee"]

    def _sync_gantt_assignments_from_employees(self):
        """Keep Bryntum assignment rows + user fields aligned with employee_ids."""
        for task in self:
            employees = task.employee_ids
            users = employees.mapped("user_id")

            task.assigned_resources.unlink()
            for employee in employees:
                self.env["project.task.assignment"].create(
                    {
                        "task": task.id,
                        "resource": employee.user_id.id or False,
                        "resource_base": employee.resource_id.id or False,
                        "units": int(100),
                    }
                )

            sync_vals = {}
            if "assigned_ids" in task._fields:
                sync_vals["assigned_ids"] = [(6, 0, users.ids)]
            if "user_ids" in task._fields:
                sync_vals["user_ids"] = [(6, 0, users.ids)]
            if sync_vals:
                task.with_context(skip_bryntum_assignment_sync=True).write(sync_vals)

    @api.onchange('planned_date_begin')
    def _onchange_planned_date_begin_keep_range_valid(self):
        """Prevent losing start date in UI when start > end by normalizing range."""
        for task in self:
            _logger.info(
                "Bryntum onchange planned_date_begin task_id=%s incoming=(%s, %s)",
                task.id or "new",
                task.planned_date_begin,
                task.planned_date_end,
            )
            if (
                task.planned_date_begin
                and task.planned_date_end
                and task.planned_date_begin > task.planned_date_end
            ):
                task.planned_date_end = task.planned_date_begin
                _logger.info(
                    "Bryntum onchange normalized end to start task_id=%s normalized=(%s, %s)",
                    task.id or "new",
                    task.planned_date_begin,
                    task.planned_date_end,
                )

    def write(self, vals):
        """
                override this function to pass resource to the gantt chart
        """
        if 'planned_date_begin' in vals or 'planned_date_end' in vals:
            _logger.info(
                "Bryntum task.write incoming task_ids=%s vals_planned=%s",
                self.ids,
                {k: vals.get(k) for k in ('planned_date_begin', 'planned_date_end') if k in vals},
            )
        if self.env.context.get("skip_bryntum_assignment_sync"):
            return super(ProjectTask, self).write(vals)
        if len(self) == 1:
            current = self
            new_start = vals.get('planned_date_begin')
            new_end = vals.get('planned_date_end')

            if new_start and new_end:
                if check_gantt_date(new_start) > check_gantt_date(new_end):
                    vals['planned_date_end'] = new_start
            elif new_start and current.planned_date_end:
                # Bryntum often sends only the changed field (startDate OR endDate).
                # Keep date range valid to avoid rollback/reset in UI.
                if check_gantt_date(new_start) > check_gantt_date(current.planned_date_end):
                    vals['planned_date_end'] = new_start
            elif new_end and current.planned_date_begin:
                if check_gantt_date(current.planned_date_begin) > check_gantt_date(new_end):
                    vals['planned_date_begin'] = new_end

            # Some databases have a constraint: planned_date_begin <= date_deadline.
            # Keep deadline aligned with planning dates to avoid rollback on save.
            candidate_start = vals.get('planned_date_begin') or current.planned_date_begin
            candidate_end = vals.get('planned_date_end') or current.planned_date_end
            candidate_deadline = vals.get('date_deadline') or current.date_deadline
            if candidate_start and candidate_deadline and check_gantt_date(candidate_start) > check_gantt_date(candidate_deadline):
                vals['date_deadline'] = candidate_end or candidate_start
        response = super(ProjectTask, self).write(vals)
        if 'planned_date_begin' in vals or 'planned_date_end' in vals:
            first = self[:1]
            _logger.info(
                "Bryntum task.write persisted first_task_id=%s planned=(%s, %s)",
                first.id if first else False,
                first.planned_date_begin if first else False,
                first.planned_date_end if first else False,
            )
        if any(key in vals for key in ("employee_ids", "user_ids", "assigned_ids")):
            for task in self:
                if "employee_ids" in vals:
                    employees = task.employee_ids
                elif "user_ids" in vals:
                    employees = self._users_to_employees(task.user_ids)
                    task.with_context(skip_bryntum_assignment_sync=True).write({"employee_ids": [(6, 0, employees.ids)]})
                else:
                    employees = self._users_to_employees(task.assigned_ids)
                    task.with_context(skip_bryntum_assignment_sync=True).write({"employee_ids": [(6, 0, employees.ids)]})
                task._sync_gantt_assignments_from_employees()
        return response

    @api.model_create_multi
    def create(self, vals_list):
        """
        override this function to pass resource to the gantt chart
        """
        for vals in vals_list:
            if (
                vals.get('planned_date_begin')
                and vals.get('planned_date_end')
                and check_gantt_date(vals.get('planned_date_begin')) > check_gantt_date(vals.get('planned_date_end'))
            ):
                vals['planned_date_end'] = vals.get('planned_date_begin')
            if (
                vals.get('planned_date_begin')
                and vals.get('date_deadline')
                and check_gantt_date(vals.get('planned_date_begin')) > check_gantt_date(vals.get('date_deadline'))
            ):
                vals['date_deadline'] = vals.get('planned_date_end') or vals.get('planned_date_begin')
        records = super(ProjectTask, self).create(vals_list)
        for task in records:
            if task.employee_ids:
                task._sync_gantt_assignments_from_employees()
            elif "user_ids" in task._fields and task.user_ids:
                employees = self._users_to_employees(task.user_ids)
                task.with_context(skip_bryntum_assignment_sync=True).write({"employee_ids": [(6, 0, employees.ids)]})
                task._sync_gantt_assignments_from_employees()
        return records


    def copy(self, default=None):
        task_copy = super(ProjectTask, self).copy(default)
        task_mapping = self.env.context.get('task_mapping_keys', {})
        task_mapping[self.id] = task_copy.id
        return task_copy

    @api.onchange('constraint_type')
    def _onchange_constraint_type(self):
        if not self.constraint_type:
            self.constraint_date = None
        else:
            self.constraint_date = {
                'assoonaspossible': self.planned_date_begin,
                'aslateaspossible': self.planned_date_end,
                'muststarton': self.planned_date_begin,
                'mustfinishon': self.planned_date_end,
                'startnoearlierthan': self.planned_date_begin,
                'startnolaterthan': self.planned_date_begin,
                'finishnoearlierthan': self.planned_date_end,
                'finishnolaterthan': self.planned_date_end
            }[self.constraint_type]



class ProjectTaskLinked(models.Model):
    _name = 'project.task.linked'
    _description = 'Project Task Linked'

    from_id = fields.Many2one('project.task', ondelete='cascade', string='From')
    to_id = fields.Many2one('project.task', ondelete='cascade', string='To')
    lag = fields.Integer(string="Lag", default=0)
    lag_unit = fields.Char(string="Lag Unit", default='d')
    type = fields.Integer(string="Type", default=2)
    dep_active = fields.Boolean(string="Active", default=True)


class ProjectTaskAssignmentUser(models.Model):
    _name = 'project.task.assignment'
    _description = 'Project Task User Assignment'

    task = fields.Many2one('project.task', ondelete='cascade', string='Task')
    resource = fields.Many2one('res.users', ondelete='cascade', string='User')
    resource_base = fields.Many2one('resource.resource', ondelete='cascade', string='Resource')
    units = fields.Integer(string="Units", default=0)


class ProjectTaskBaseline(models.Model):
    _name = 'project.task.baseline'
    _description = 'Project Task User Assignment'

    task = fields.Many2one('project.task', ondelete='cascade', string='Task')
    name = fields.Char(string="Name", default='')
    planned_date_begin = fields.Datetime("Start date")
    planned_date_end = fields.Datetime("End date")


class ProjectTaskSegment(models.Model):
    _name = 'project.task.segment'
    _description = 'Project Task Segment'

    task = fields.Many2one('project.task', ondelete='cascade', string='Task')
    name = fields.Char(string="Name", default='')
    planned_date_begin = fields.Datetime("Start date")
    planned_date_end = fields.Datetime("End date")