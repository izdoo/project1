# -*- coding: utf-8 -*-
import re
import dateutil.parser
from json import dumps, loads
import base64

import pytz

from odoo import http
from odoo.http import Response, request


class BryntumGantt(http.Controller):
    task_id_template = 'project-task_%d'

    @staticmethod
    def get_gantt_date(date_field, tz=None):
        if not date_field:
            return ''
        if tz and hasattr(date_field, 'astimezone'):
            return date_field.astimezone(tz).strftime('%Y-%m-%dT%H:%M:%S')
        return date_field.strftime('%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def from_gantt_date(value):
        return dateutil.parser.parse(value, ignoretz=True)

    @staticmethod
    def get_avatar(value):
        if isinstance(value, (bytes, bytearray)):
            return base64.b64encode(value).decode('ascii')
        else:
            return None

    @staticmethod
    def get_assignment(assignment, task):

        if len(assignment.resource.ids) > 0:
            resource = assignment.resource
            prefix = 'u_'

        if len(assignment.resource_base.ids) > 0:
            resource = assignment.resource_base
            prefix = 'r_'

        resource_id = prefix + str(resource.id)

        return {
                'id': '%d-%s' % (task.id, resource_id),
                'resource': resource_id,
                'event': task.id,
                'units': assignment.units
                }

    @staticmethod
    def get_assignments(task, get_assignment):
        if len(task.assigned_resources.ids) > 0:
            return map(lambda assignment: get_assignment(assignment, task), task.assigned_resources)

        return map(
            lambda user: {'id': '%d-%d' % (task.id, user.id), 'resource': user.id, 'event': task.id, 'units': 100},
            task.assigned_ids)

    @staticmethod
    def get_baselines(task, tz, cfn):

        baselines = [
            {
                "name": baseline.name,
                "startDate": cfn(baseline.planned_date_begin, tz),
                "endDate": cfn(baseline.planned_date_end, tz)
            }
            for baseline in task.baselines
        ]

        return baselines

    @staticmethod
    def get_segments(task, tz, cfn):

        segments = [
            {
                "name": segment.name,
                "startDate": cfn(segment.planned_date_begin, tz),
                "endDate": cfn(segment.planned_date_end, tz)
            }
            for segment in task.segments
        ]

        if len(segments) > 0:
            return segments
        else:
            return None

    @staticmethod
    def field_related(data, cfields):
        response = {}
        for o_key, g_key, func in cfields:
            value = data.get(g_key, '0_empty_value_0')
            if value == '0_empty_value_0':
                continue
            if func and not value is None:
                response.update({o_key: func(value)})
            else:
                response.update({o_key: value})
        return response

    @staticmethod
    def to_task_id(gantt_id):
        groups = re.match(r'project-task_(\d+)', gantt_id)
        if groups:
            return int(groups.group(1))
        return None

    @staticmethod
    def to_project_id(gantt_id):
        groups = re.match(r'project_(\d+)', gantt_id)
        if groups:
            return int(groups.group(1))
        return None


    @staticmethod
    def is_gantt_new_id(new_id):
        return bool(re.match(r'_generated.+\d+', new_id))

    def get_tz(self):
        tz = pytz.utc
        try:
            if type(request.env.user.partner_id.tz) == str:
                tz = pytz.timezone(request.env.user.partner_id.tz) or pytz.utc
        except:
            return tz
        return tz

    @property
    def default_fields(self):
        return [
            ('name', 'name', None),
            ('planned_date_begin', 'startDate', self.from_gantt_date),
            ('planned_date_end', 'endDate', self.from_gantt_date),
            ('duration', 'duration', None),
            ('duration_unit', 'durationUnit', None),
            ('parent_id', 'parentId', self.to_task_id),
            ('project_id', 'project_id', self.to_project_id),
            ('parent_index', 'parentIndex', None),
            ('percent_done', 'percentDone', None),
            ('assigned_ids', 'assignedList', None),
            ('description', 'note', None),
            ('effort', 'effort', None),
            ('gantt_calendar_flex', 'calendar', None),
            ('date_deadline', 'date_deadline', self.from_gantt_date),
            ('scheduling_mode', 'schedulingMode', None),
            ('constraint_type', 'constraintType', None),
            ('constraint_date', 'constraintDate', self.from_gantt_date),
            ('effort_driven', 'effortDriven', None),
            ('bryntum_rollup', 'rollup', None),
            ('manually_scheduled', 'manuallyScheduled', None),
        ]

    @http.route('/bryntum_gantt/load', type='json', auth='user', cors="*")
    def bryntum_gantt_load(self, data=None, **kw):
      #  headers = {'content-type': 'application/json'}
        data_json = loads(data)
        project_ids = data_json.get('project_ids')
        only_projects = data_json.get('only_projects')

        tz = self.get_tz()
        # user = request.env.user
        project_env = request.env['project.project']
        # task_env = request.env['project.task']
        resource_env = request.env['resource.resource']

        users = []
        resources = []
        assignments = []
        dependencies = []
        projects = []
        project_nodes = []
        calendar = []

        use_user_ids = False

        for project_id in project_ids:

            if project_id:
                project_id = int(project_id)
            else:
                continue

            project = project_env.search([('id', '=', project_id)])
            task_objs = project.tasks

            if not project.id:
                continue

            project_id = 'project_%d' % project.id

            tasks = [
                {
                    "id": self.task_id_template % task.id,
                    "name": task.name,
                    "parentId": self.task_id_template % task.parent_id,
                    "parentIndex": task.parent_index,
                    "percentDone": task.percent_done,
                    "startDate": self.get_gantt_date(task.planned_date_begin, tz),
                    "endDate": self.get_gantt_date(task.planned_date_end, tz),
                    "expanded": True,
                    "date_deadline": self.get_gantt_date(task.date_deadline, tz),
                    "project_id": project_id,
                    "note": task.description,
                    "effort": task.effort,
                    "duration": task.duration,
                    "durationUnit": task.duration_unit,
                    "calendar": task.gantt_calendar_flex or task.gantt_calendar,
                    "schedulingMode": task.scheduling_mode,
                    "constraintType": task.constraint_type or None,
                    "constraintDate": self.get_gantt_date(task.constraint_date, tz),
                    "effortDriven": task.effort_driven,
                    "rollup": task.bryntum_rollup,
                    "manuallyScheduled": task.manually_scheduled if project.bryntum_auto_scheduling else True,
                    "baselines": self.get_baselines(task, tz, self.get_gantt_date),
                    "segments": self.get_segments(task, tz, self.get_gantt_date)
                }
                for task in task_objs
            ]

            if project.bryntum_user_assignment:
               use_user_ids = True

            assignments = assignments + [
                {
                    'id': assignment.get('id'),
                    'event': self.task_id_template % assignment.get('event'),
                    'resource': assignment.get('resource'),
                    'units': assignment.get('units')
                }
                for task in task_objs
                for assignment in self.get_assignments(task, self.get_assignment) or []
            ]

            dependencies = dependencies + [
                {
                    'id': link.id,
                    'fromTask': self.task_id_template % link.from_id,
                    'toTask': self.task_id_template % link.to_id,
                    'lag': link.lag,
                    'lagUnit': link.lag_unit,
                    'active': link.dep_active,
                    'type': link.type
                }
                for task in task_objs for link in task.linked_ids
            ]

            project_nodes.append({
                                'id': project_id,
                                'startDate': self.get_gantt_date(project.project_start_date, tz),
                                'name': project.name,
                                'project_id': project_id,
                                'manuallyScheduled': not project.bryntum_auto_scheduling,
                                'expanded': True,
                                'children': tasks
                            })


        if not bool(only_projects):
            all_projects = project_env.search([])
            projects = [
                        {
                            'id': 'project_%d' % project.id,
                            'name': project.name,
                            'manuallyScheduled': not project.bryntum_auto_scheduling
                        }
                        for project in all_projects
                    ]

            resource_ids = resource_env.search([])
            resources = [
                            {
                                "id": "r_" + str(resource.id),
                                "name": resource.name
                            }
                            for resource in resource_ids
                        ]

            su = request.env['ir.config_parameter'].sudo()
            calendar = all_projects.get_default_calendar()

            calendar_config = su.get_param('bryntum.calendar_config')

            if isinstance(calendar_config, str):
                try:
                    calendar = loads(calendar_config)
                except:
                    calendar = calendar

            if use_user_ids:
                user_env = request.env['res.users']
                user_ids = user_env.search([])
                users = [
                    {
                        "id": "u_" + str(user.id),
                        "name": user.name,
                        "city": user.partner_id.city
                    }
                    for user in user_ids
                ]

        params = {
            "success": True,
            "project": {
                'id': 'bryntum_gantt_project',
                "calendar": "general"
            },
            "projects": {
                "rows" : projects
            },
            "calendars": {
                "rows": calendar
            },
            "tasks": {
                "rows": project_nodes
            },
            "dependencies": {
                "rows": dependencies,
            },
            "resources": {
                "rows": users + resources
            },
            "assignments": {
                "rows": assignments
            },
            "timeRanges": {
                "rows": []
            }
        }
        #return Response(response=dumps(params), headers=headers)
        return params

    @staticmethod
    def gantt_id(_id):
        response = re.match(r'(project-task)_(\d+)', _id) \
                   or re.match(r'(project-project)_(\d+)', _id) \
                   or re.match(r'(project)_(\d+)', _id)
        if response:
            return response.group(1), int(response.group(2))
        else:
            return False, False

    @staticmethod
    def get_resource_id(id):
        # Use a breakpoint in the code line below to debug your script.
        groups = re.match(r'u_(\d+)', id)
        if groups:
            return int(groups.group(1)), None
        groups = re.match(r'r_(\d+)', id)
        if groups:
            return None, int(groups.group(1))
        return None, None

    @http.route('/bryntum_gantt/send/update', type='json', auth='user', cors="*")
    def bryntum_gantt_update(self, data=None, **kw):
        data_json = loads(data)
        task_env = request.env['project.task']
        project_env = request.env['project.project']
        task_linked_env = request.env['project.task.linked']
        task_assignments_env = request.env['project.task.assignment']
        task_baselines_env = request.env['project.task.baseline']
        task_segments_env = request.env['project.task.segment']

        try:
            for el in data_json:
                gantt_model_id = el['model']['id']
                model, int_id = self.gantt_id(gantt_model_id)

                if not int_id:
                    continue

                new_data = el.get('newData', {})

                if model == 'project-task':
                    task = task_env.search([('id', '=', int_id)])
                    task_gantt_ids = new_data.get('taskLinks')

                    if not task_gantt_ids is None:
                        task.linked_ids.unlink()
                        for link in task_gantt_ids:
                            task_linked_env.create({
                                'from_id': self.to_task_id(link.get('from')),
                                'to_id': self.to_task_id(link.get('to')),
                                'lag': int(link.get('lag')),
                                'lag_unit': link.get('lagUnit'),
                                'dep_active': link.get('active'),
                                'type': link.get('type')
                            })

                    task_assignments = new_data.get('assignedResources')

                    if not task_assignments is None:
                        task.assigned_resources.unlink()
                        for assignment in task_assignments:
                            resource_id = self.get_resource_id(assignment.get('resource_id'))
                            task_assignments_env.create({
                                'task': self.to_task_id(assignment.get('task_id')),
                                'resource': resource_id[0],
                                'resource_base': resource_id[1],
                                'units': int(assignment.get('units'))
                            })

                    baselines = new_data.get('baselines')

                    if not baselines is None:
                        task.baselines.unlink()
                        for baseline in baselines:
                            task_baselines_env.create({
                                'task': task.id,
                                'name': baseline.get('name'),
                                'planned_date_begin': self.from_gantt_date(baseline.get('startDate')),
                                'planned_date_end': self.from_gantt_date(baseline.get('endDate'))
                            })

                    segments = new_data.get('segments')

                    if not segments is None:
                        task.segments.unlink()
                        for segment in segments:
                            task_segments_env.create({
                                'task': task.id,
                                'name': segment.get('name'),
                                'planned_date_begin': self.from_gantt_date(segment.get('startDate')),
                                'planned_date_end': self.from_gantt_date(segment.get('endDate'))
                            })

                    data = self.field_related(new_data, self.default_fields)

                    task.write(data)
                elif model in ('project', 'project-project'):
                    project = project_env.search([('id', '=', int_id)])
                    start_date = new_data.get('startDate')
                    if project and start_date:
                        project.write({
                            'project_start_date': self.from_gantt_date(start_date)
                        })
                    name = new_data.get('name')
                    if project and name:
                        project.write({
                            'name': name
                        })

            return {'success': True, 'status': 'updated'}
        except Exception as e:
            return {'success': False, 'message': str(e) }

    @http.route('/bryntum_gantt/send/remove', type='json', auth='user', cors="*")
    def bryntum_gantt_remove(self, data=None, **kw):
        data_json = loads(data)
        task_env = request.env['project.task']

        task_gantt_ids = [item for outer in data_json for item in outer]
        task_int_ids = [self.to_task_id(el) for el in task_gantt_ids]

        task = task_env.search([('id', 'in', task_int_ids)])
        task.unlink()

        return {'success': True, 'status': 'deleted'}

    @http.route('/bryntum_gantt/send/create', type='json', auth='user', cors='*')
    def bryntum_gantt_create(self, data=None, project_id=None, **kw):
        data_json = loads(data)
        task_env = request.env['project.task']
        create_int_ids = []

        for rec in data_json:
            if not self.is_gantt_new_id(rec.get('id')):
                continue
            data = self.field_related(rec, self.default_fields)
            task = task_env.create(data)
            create_int_ids.append((rec.get('id'),
                                   self.task_id_template % task.id))

        return {
            'success': True,
            'status': 'created',
            'ids': create_int_ids
        }
