/* @odoo-module */

import { BryntumGanttController } from "@bryntum_gantt/js/bryntum_gantt_controller";
import { BryntumGanttRenderer } from "@bryntum_gantt/js/bryntum_gantt_renderer";
import { BryntumArchParser } from "@bryntum_gantt/js/bryntum_arch_parser";
import { registry } from "@web/core/registry";
import { RelationalModel } from "@web/model/relational_model/relational_model";

export const BryntumGantt = {
    type: "BryntumGantt",
    searchMenuTypes: ["filter", "favorite"],
    Controller: BryntumGanttController,
    Renderer: BryntumGanttRenderer,
    ArchParser: BryntumArchParser,
    Model: RelationalModel,
    props: (genericProps, view) => {
        const { ArchParser } = view;
        const { arch, relatedModels, resModel } = genericProps;
        const archInfo = new ArchParser().parse(arch, relatedModels, resModel);
        return {
            ...genericProps,
            Model: view.Model,
            Renderer: view.Renderer,
            archInfo,
        };
    },
};

registry.category("views").add("BryntumGantt", BryntumGantt);
