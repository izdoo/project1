/** @odoo-module */

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Layout } from "@web/search/layout";
import { loadBundle, loadJS } from "@web/core/assets";

export class BryntumGanttController extends Component {
    static components = { Layout };
    static props = {};
    async setup() {
        /*
            orm : used orm instead of getting data using _rpc method
            controller is loaded first so, vue files are loaded asynchronously first using loadJS method.
            Bundle Vue (gantt_src): window.o_gantt.run = true → mount Vue vào #bryntum-gantt.
        */
        this.domain = 0;
        if (this.props && this.props.domain && this.props.domain.length > 0) {
            this.domain = this.props.domain[2][2];
        }

        window.o_gantt = Object.assign(
            {
                projectID: this.domain > 0 ? this.domain : 0,
                lang: "en_En",
                readOnly: false,
                saveWbs: false,
                config: { project: { week_start: 1, hoursPerDay: 8 } },
            },
            window.o_gantt || {},
        );
        window.production = true;

        this.orm = useService("orm");
        this.response = this.get_response_values();
        await loadBundle("web._assets_jquery");
        if (typeof window.$ === "undefined" && window.jQuery) {
            window.$ = window.jQuery;
        }
        // Fallback nếu bundle không suy ra được từ <script> (app.js gán __webpack_require__.p động).
        window.__webpack_public_path__ = "/bryntum_gantt/static/gantt_src/";
        // Bump ?v= khi đổi bundle để tránh cache trình duyệt (lỗi cũ như atob trên avatar).
        const bryntumGanttAssetsVer = "19.0.2.0.6";
        await loadJS(
            `/bryntum_gantt/static/gantt_src/js/chunk-vendors.js?v=${bryntumGanttAssetsVer}`,
        );
        await loadJS(`/bryntum_gantt/static/gantt_src/js/app.js?v=${bryntumGanttAssetsVer}`);
        this.response.then((val) => {
            try {
                const week_start = parseInt(val.week_start, 10);
                if (!isNaN(week_start)) {
                    window.o_gantt.week_start = week_start;
                }
                window.o_gantt.readOnly = val.bryntum_readonly_project;
                window.o_gantt.saveWbs = val.bryntum_save_wbs;
                eval("window.o_gantt.config = " + val.bryntum_gantt_config);
                window.o_gantt.bryntum_auto_scheduling = val.bryntum_auto_scheduling;
            } catch (err) {
                console.log("Gantt configuration object not valid");
                window.o_gantt.run = true;
            }
            window.o_gantt.run = true;
        });

        window.o_gantt.projectID = this.domain > 0 ? this.domain : 0;
    }

    async get_response_values() {
        const response = await this.orm.call("project.project", "get_bryntum_values", []);
        return response;
    }
}

BryntumGanttController.template = "bryntum_gantt.ControllerView";
