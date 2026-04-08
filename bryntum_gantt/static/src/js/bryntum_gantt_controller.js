/** @odoo-module */

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Layout } from "@web/search/layout";
import { loadJS } from "@web/core/assets";

export class BryntumGanttController extends Component {
        static components = { Layout };
        static props = {};
        async setup() {

        /*
            orm : used orm instead of getting data using _rpc method
            controller is loaded first so, vue files are loaded asynchronously first using loadJS method.
        */
             this.domain = 0
             if (this.props && this.props.domain.length > 0){ this.domain = this.props.domain[2][2]}

             this.orm = useService('orm');
             this.response = this.get_response_values();
             await loadJS("bryntum_gantt/static/gantt_src/js/app.js?v210");
             await loadJS("bryntum_gantt/static/gantt_src/js/chunk-vendors.js");
             this.response.then(
                (val) => {
                   try {
                         let week_start = parseInt(val.week_start);
                         if (!isNaN(week_start)) {
                             window.o_gantt.week_start = week_start;
                         }
                         window.o_gantt.readOnly = val.bryntum_readonly_project;
                         window.o_gantt.saveWbs = val.bryntum_save_wbs;
                         eval('window.o_gantt.config = ' + val.bryntum_gantt_config);
                         window.o_gantt.bryntum_auto_scheduling = val.bryntum_auto_scheduling;
                     } catch (err) {
                             console.log('Gantt configuration object not valid');
                             window.o_gantt.run = true;
                     }
                    window.o_gantt.run = true;
                }
             )

            if (this.domain > 0) {
                window.o_gantt.projectID = this.domain;
            } else {
                window.o_gantt.projectID = 0;
            }
        }

        /*
            Getting Values on Initialization from a separate function
        */
       async get_response_values () {
            const response = await this.orm.call('project.project','get_bryntum_values',[]);
            return response;
        }
}

/*
    Controller has separate view, so need to create its view with layout component
*/
BryntumGanttController.template = 'bryntum_gantt.ControllerView'