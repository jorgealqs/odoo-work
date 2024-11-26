/** @odoo-module **/

import { Component, useState } from "@odoo/owl"
import { registry } from "@web/core/registry"
import { Layout } from "@web/search/layout"
import { AnalisysLotteryMedellin } from "./analysis/analysis_medellin"

export class LotteryMedellin extends Component {
    static template = "lottery.LotteryMedellin"
    static components = { Layout, AnalisysLotteryMedellin }

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

        const results = await this.env.services.orm.call(
            'lottery.medellin',
            "pandasLotteryAnalysisMedellin"
        )
        console.log(analysisType, results)
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

}

registry.category("actions").add("action.LotteryMedellin", LotteryMedellin)
