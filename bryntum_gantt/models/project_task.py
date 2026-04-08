# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.misc import format_date
import dateutil.parser
from ..tools.odoo_utils import is_enterprise

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

    def write(self, vals):
        """
                override this function to pass resource to the gantt chart
        """
        response = super(ProjectTask, self).write(vals)
        if vals.get('employee_ids'):
            self.assigned_resources.unlink()
            for rec in self.employee_ids:
                self.assigned_resources.create({
                    'task': self.id,
                    'resource': False,
                    'resource_base': rec.id,
                    'units': int(100)
                })
        return response
    def create(self, vals):
        """
        override this function to pass resource to the gantt chart
        """
        response = super(ProjectTask, self).create(vals)
        if response.employee_ids:
            self.assigned_resources.unlink()
            for rec in response.employee_ids:
                self.assigned_resources.create({
                    'task': response.id,
                    'resource': False,
                    'resource_base': rec.id,
                    'units': int(100)
                })
        return response


    @api.returns('self', lambda value: value.id)
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