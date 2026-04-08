#### Version 2.0.0

[FIXES]
- Support split task #93
- Odoo16.0 
- Upgrade Gantt library version to 5.2.6

#### Version 1.4.0

[FIXES]
- Error on setting baseline #92
- Add missing fonts

#### Version 1.3.9

[FIXES]
- Auto scheduling ignored on new tasks when set on Project level #91
- Split task is not supported removed from task edit menu #90
- Upgrade Gantt library version to 5.2.4

#### Version 1.3.8

[FIXES]
- WeekStartDay is set to default after zooming #88
- Wrongly set default value on ConstraintType #89
- Error when confirming the creation of the task with a tabulation #87
- Note field as column value - remove false and html tags in value #86
- Add indent and outdent features in task context bar #85
- Upgrade Gantt library version to 5.2.0

#### Version 1.3.7

[FIXES]
- Adding predecessor in editor will throw an error #82
- Enable feature configuration #83
- Add additional fields to the Task model #84

#### Version 1.3.6

[FIXES]
- Upgrade to Gantt 5.0.7
- Global font should not be changed by GanttView #73
- Make the gantt toolbar configurable #74
- Disable or enable MSExport feature (default) #75
- Create dependencies between projects #77
- Calendar should not have fixed ids #78
- Set projectId on newly created task #79
- Empty project store should not throw an error #80
- Global entry point in top menu to the Gantt Pro View #81

#### Version 1.3.5

[FIXES]
- Upgrade to Gantt 5.0.5
- Multiple projects can throw error when modifications are made #72
- Load routing changed into jsonRpc call

#### Version 1.3.4

[FIXES]
- Creating task: ManuallyScheduled default should be set correctly #65
- Field triggers are missing due to css hidden rule #67
- Drag drop tasks not working #68
- Apply config settings like daysperweek, hoursperday on the Project model #70

#### Version 1.3.3

[FIXES]
- Task dates should take timezone customer or user into account #63

#### Version 1.3.2

[FIXES]
- Upgrade library to version 5.0.1
- Wrong routing method name causes warning in Odoo log
- Error selecting multiple projects #61

#### Version 1.3.1

[FIXES]
- Javascript Bryntum Library Update to 5.0.0
- Fix Cycle during synchronous computation #58
- Use splitter to show Resource Utilization sheet #59
- Gantt toolbar scrollable instead of overflow button #60
- Fix floating new tasks on project node

#### Version 1.3.0

[FIXES]
- Manage and edit project and resource calendar #37
- Error on project view change (view does not load) #104
- Infinite loop on save error #105

#### Version 1.2.9

[FIXES]
- Gantt View module with included resource histogram #3
- UI should prevent to create tasks outside the scope of a project node #53
- Make project start date editable #55

#### Version 1.2.8

[FIXES]
- Error creating a child task <a href="https://github.com/bryntum/odoo-support/issues/49">#49</a>
- Dragging tasks is broken <a href="https://github.com/bryntum/odoo-support/issues/50">#50</a>
- Creating Tasks do not work https://github.com/bryntum/odoo-support/issues/52

#### Version 1.2.7

[FIXES]
- Show multiple projects in the gantt chart <a href="https://github.com/bryntum/odoo-support/issues/2">#2</a>
- Add export ms project feature to gantt
- Setting a start date out of range will result in an error and crash  <a href="https://github.com/bryntum/odoo-support/issues/46">#46</a>

#### Version 1.2.6

[FIXES]
- Add view state management on user level <a href="https://github.com/bryntum/odoo-support/issues/44">#44</a>
- Remove avatar base64 string from resource data <a href="https://github.com/bryntum/odoo-support/issues/42">#42</a>
- General calendar should be set on 7 day 24 hours workdays <a href="https://github.com/bryntum/odoo-support/issues/41">#41</a>
- Add configuration support for the gantt chart <a href="https://github.com/bryntum/odoo-support/issues/17">#17</a>
- Configure option to disable users as resource base <a href="https://github.com/bryntum/odoo-support/issues/45">#45</a>

#### Version 1.2.5

[FIXES]
- Localization is not found for 'Start' in 'Baselines'. Locale : En <a href="https://github.com/bryntum/odoo-support/issues/39">#39</a>
- Error message by opening "normal" tasks and recurring tasks <a href="https://github.com/bryntum/odoo-support/issues/40">#40</a>
- General calendar should be set on 7 day 24 hours workdays <a href="https://github.com/bryntum/odoo-support/issues/41">#37</a>

#### Version 1.2.4

[FIXES]
- Error on adding new assignment <a href="https://github.com/bryntum/odoo-support/issues/36">#36</a>
- Add roll up to the features and task model <a href="https://github.com/bryntum/odoo-support/issues/37">#37</a>

#### Version 1.2.3

[FIXES]
- Use resource model as resource base <a href="https://github.com/bryntum/odoo-support/issues/20">#20</a>
- Store dependency type <a href="https://github.com/bryntum/odoo-support/issues/32">#32</a>
- Cannot remove resource once allocated <a href="https://github.com/bryntum/odoo-support/issues/33">#33</a>

#### Version 1.2.2

[FIXES]
- Bug fix baselines not saved
- Bug fix Moving subtask to root level throws error
- Criticalpath calculation throws error on null dates
- Remove loadmask while saving
