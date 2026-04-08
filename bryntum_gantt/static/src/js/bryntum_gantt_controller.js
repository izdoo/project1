/** @odoo-module */

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Layout } from "@web/search/layout";
import { loadBundle, loadJS } from "@web/core/assets";

export class BryntumGanttController extends Component {
    static components = { Layout };

    _extractProjectIdFromDomain(domain) {
        if (!Array.isArray(domain)) {
            return 0;
        }
        for (const item of domain) {
            if (Array.isArray(item) && item.length >= 3) {
                const [field, op, value] = item;
                if (field === "project_id" && ["=", "in"].includes(op)) {
                    if (Array.isArray(value)) {
                        const first = parseInt(value[0], 10);
                        return Number.isInteger(first) && first > 0 ? first : 0;
                    }
                    const pid = parseInt(value, 10);
                    return Number.isInteger(pid) && pid > 0 ? pid : 0;
                }
            }
            const nested = this._extractProjectIdFromDomain(item);
            if (nested > 0) {
                return nested;
            }
        }
        return 0;
    }

    _extractProjectIdFromUrl() {
        try {
            const path = window.location.pathname || "";
            // Example: /odoo/action-233/9/tasks/116
            const m = path.match(/\/action-\d+\/(\d+)\/tasks(?:\/\d+)?$/);
            if (m && m[1]) {
                const pid = parseInt(m[1], 10);
                if (Number.isInteger(pid) && pid > 0) {
                    return pid;
                }
            }
        } catch (_err) {
            // ignore
        }
        return 0;
    }

    _getProjectId() {
        const props = this.props || {};
        const context = props.context || {};
        const fromContext = parseInt(
            context.active_id || context.default_project_id || context.search_default_project_id,
            10,
        );
        if (Number.isInteger(fromContext) && fromContext > 0) {
            return fromContext;
        }
        const fromDomain = this._extractProjectIdFromDomain(props.domain);
        if (fromDomain > 0) {
            return fromDomain;
        }
        return this._extractProjectIdFromUrl();
    }

    async setup() {
        /*
            orm : used orm instead of getting data using _rpc method
            controller is loaded first so, vue files are loaded asynchronously first using loadJS method.
            Bundle Vue (gantt_src): window.o_gantt.run = true → mount Vue vào #bryntum-gantt.
        */
        this.domain = this._getProjectId();
        // Reset runtime state on each view open to avoid stale state
        // from previous Gantt sessions (common cause of first-open blank view).
        window.o_gantt = {
            projectID: this.domain > 0 ? this.domain : 0,
            lang: "en_En",
            readOnly: false,
            saveWbs: false,
            run: false,
            config: { project: { week_start: 1, hoursPerDay: 8 } },
        };
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
        const bryntumGanttAssetsVer = "19.0.2.0.8";
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
