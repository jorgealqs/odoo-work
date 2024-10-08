/** @odoo-module **/

import { Component } from "@odoo/owl"
import { registry } from "@web/core/registry"
import { Layout } from "@web/search/layout"
import { HistoricalButton } from "./button_historical/button"

export class BalotoForecast extends Component {
    static template = "baloto.BalotoForecast"
    static components = { Layout, HistoricalButton }

    setup() {
        this.display = {
            controlPanel: {
                "top-right": false,
                "bottom-right": false,
            },
        }
    }

    openHistoricalView(lotteryType = "") {
        const context = {}
        if (lotteryType) {
            context[`search_default_lottery_type_id_${lotteryType}`] = 1
        }

        this.env.services.action.doAction({
            name: `Historical ${lotteryType}`,
            type: "ir.actions.act_window",
            res_model: "lottery.baloto",
            views: [
                [false, "kanban"],
                [false, "list"],
                [false, "form"],
            ],
            context: context,
        })
    }
}

registry.category("actions").add("action.BalotoForecast", BalotoForecast)