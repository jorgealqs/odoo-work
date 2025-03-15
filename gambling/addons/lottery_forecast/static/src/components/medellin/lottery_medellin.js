/** @odoo-module **/

import { Component, useState } from "@odoo/owl"
import { registry } from "@web/core/registry"
import { Layout } from "@web/search/layout"
import { AnalisysLotteryMedellin } from "./analysis/analysis_medellin"
import { TablaResultBaloto } from "../baloto/tabla_result/tabla_result"

export class LotteryMedellin extends Component {
    static template = "lottery.LotteryMedellin"
    static components = { Layout, AnalisysLotteryMedellin, TablaResultBaloto }

    setup() {
        this.display = {
            controlPanel: {
                "top-right": false,
                "bottom-right": false,
            },
        }
        this.state = useState({
            results: [],
            loading: false,
            error: null,
            selectedAnalysis: "",
            option: "",
        })
        this.gameOptions = this.getGameOptionsMedellin()
    }

    getGameOptionsMedellin() {
        return [
            {
                name: 'Medellín',
                options: this.getOptionsForGame('Medellin')
            }
        ]
    }

    getOptionsForGame(gameName) {
        const options = [
            { value: `three-${gameName}`, label: `Three numbers, ${gameName}` },
            { value: `four-${gameName}`, label: `Four numbers, ${gameName}` },
        ]
        return options
    }

    /**
     * Analiza los datos de la lotería de Medellín usando Pandas
     * @param {string} analysisType - Tipo de análisis a realizar
     * @param {string} option - Opción seleccionada
     * @returns {Promise<void>}
     */
    async analysisMedellinPandas(analysisType = null, option = null) {
        if (!analysisType || !option) {
            this.showNotification("Select an option!", "Error", "danger")
            return
        }

        const options = {
            analysisType,
        }

        this.state.results = await this.env.services.orm.call(
            'lottery.medellin',
            "pandasLotteryAnalysisMedellin",
            [],  // IMPORTANTE: lista vacía como primer argumento
            options  // Segundo argumento con los datos como **kw
        )
        this.state.option = analysisType
    }

    /**
     * Muestra una notificación en la interfaz
     * @param {string} message - Mensaje a mostrar
     * @param {string} title - Título de la notificación
     * @param {string} type - Tipo de notificación ('success', 'warning', 'danger', etc.)
     */
    showNotification(message, title, type) {
        this.env.services.notification.add(message, {
            title,
            type,
        })
    }

    onClickHistoricalM() {
        this.env.services.action.doAction({
            name: `Historical Medellín`,
            type: "ir.actions.act_window",
            res_model: "lottery.medellin",
            views: [
                [false, "kanban"],
                [false, "list"],
                [false, "form"],
            ],
        });
    }

}

registry.category("actions").add("action.LotteryMedellin", LotteryMedellin)
